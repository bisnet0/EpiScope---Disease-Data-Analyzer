import os
import joblib
import json
import pandas as pd
import tensorflow as tf
import google.generativeai as genai
from backend.models.user_model import db, User
from backend.models.diagnosis_model import ArbovirusDiagnosis, GlaucomaDiagnosis
from backend.utils.data_helpers import (
    parse_json_from_gemini_response,
    get_symptom_list_from_cols,
    convert_numpy_floats,
    preprocess_glaucoma_image,
)

ARTIFACTS_DIR = "/app/model_artifacts"
print("--- Inicializando AI Service (Multi-Model) ---")

# 1. Configuração do Gemini
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model_gemini = genai.GenerativeModel("gemini-2.5-flash")
except Exception as e:
    print(f"Erro Gemini: {e}")
    model_gemini = None

# 2. Carregamento do Model Zoo (Arboviroses)
ARBO_MODELS = {}
arbo_model_columns = []
arbo_target_map = {}

try:
    # Carrega metadados (iguais para todos)
    with open(os.path.join(ARTIFACTS_DIR, "model_columns.json"), "r") as f:
        arbo_model_columns = json.load(f)
    with open(os.path.join(ARTIFACTS_DIR, "target_map.json"), "r") as f:
        arbo_target_map = {int(k): v for k, v in json.load(f).items()}

    # Lista de modelos esperados
    model_files = {
        "xgboost_standard": "xgboost_standard.joblib",
        "xgboost_genetic": "xgboost_genetic.joblib", # Só vai existir se rodou o AG
        "random_forest": "randomforest.joblib",
        "decision_tree": "decisiontree.joblib"
    }

    print("Carregando modelos de Arbovírus...")
    for key, filename in model_files.items():
        path = os.path.join(ARTIFACTS_DIR, filename)
        if os.path.exists(path):
            try:
                ARBO_MODELS[key] = joblib.load(path)
                print(f"✅ {key} carregado.")
            except Exception as e:
                print(f"❌ Erro ao carregar {key}: {e}")
        else:
            print(f"⚠️ {key} não encontrado (pule se não treinou ainda).")

    # Fallback: Se não achou nenhum novo, tenta o antigo (compatibilidade)
    if not ARBO_MODELS:
        old_path = os.path.join(ARTIFACTS_DIR, "xgboost_model.joblib")
        if os.path.exists(old_path):
            ARBO_MODELS["legacy_xgboost"] = joblib.load(old_path)
            print("⚠️ Usando modelo Legacy XGBoost.")

except Exception as e:
    print(f"Erro fatal carregando modelos Arbo: {e}")

# 3. Carregamento Glaucoma (CNN)
try:
    glaucoma_cnn_model = tf.keras.models.load_model(
        os.path.join(ARTIFACTS_DIR, "glaucoma_cnn_model.h5")
    )
    with open(os.path.join(ARTIFACTS_DIR, "glaucoma_info.json"), "r") as f:
        g_info = json.load(f)
    GLAUCOMA_CLASS_NAMES = g_info.get("class_names", ["Normal", "Glaucomatous"])
    GLAUCOMA_IMG_SIZE = g_info.get("image_size", 224)
except Exception:
    glaucoma_cnn_model = None
    GLAUCOMA_CLASS_NAMES = ["Normal", "Glaucomatous"]
    GLAUCOMA_IMG_SIZE = 224


# --- ARBOVIRUS PIPELINE (ATUALIZADO PARA MULTI-MODELO) ---
def run_arbovirus_pipeline(text_description, age, sex, user_id, model_choice="all"):
    if not ARBO_MODELS or not model_gemini:
        return {"error": "Serviços de IA indisponíveis"}, 503

    # 1. Gemini estrutura os sintomas
    symptoms_list = get_symptom_list_from_cols(arbo_model_columns)
    prompt = f'Analise: "{text_description}". Extraia sintomas JSON true/false. Possíveis: {symptoms_list}.'
    try:
        gemini_resp = model_gemini.generate_content(prompt)
        structured = parse_json_from_gemini_response(gemini_resp.text)
        if not structured: raise ValueError("Falha ao estruturar JSON")
    except Exception as e:
        return {"error": f"Erro na IA Generativa: {str(e)}"}, 500

    # 2. Prepara o DataFrame
    try:
        df = pd.DataFrame(columns=arbo_model_columns, index=[0]).fillna(0)
        for s, v in structured.items():
            if s in df.columns and v:
                df.loc[0, s] = 1
        df.loc[0, "idade"] = age
        df.loc[0, "sexo_encoded"] = 1 if sex.upper() == "F" else 0
        
        input_features_log = convert_numpy_floats(df.to_dict(orient="records")[0])
    except Exception as e:
        return {"error": f"Erro no pré-processamento de dados: {e}"}, 500

    # 3. Multi-Inferência (Roda todos os modelos)
    comparative_results = {}
    best_model_name = "none"
    highest_confidence = -1.0
    final_probs = {}

    # Define quais modelos rodar
    models_to_run = ARBO_MODELS if model_choice == "all" else {model_choice: ARBO_MODELS.get(model_choice)}
    
    try:
        for name, model in models_to_run.items():
            if not model: continue
            
            # Predição
            probs = model.predict_proba(df[arbo_model_columns])[0]
            model_result = {arbo_target_map[i]: float(p) for i, p in enumerate(probs)}
            
            # Quem é o vencedor deste modelo?
            top_disease = max(model_result, key=model_result.get)
            confidence = model_result[top_disease]
            
            # Guarda para o comparativo
            comparative_results[name] = {
                "diagnosis": top_disease,
                "confidence": confidence,
                "full_probs": model_result
            }

            # Lógica do "Campeão Geral" (Maior confiança vence)
            if confidence > highest_confidence:
                highest_confidence = confidence
                best_model_name = name
                final_probs = model_result # Usa as probs do campeão para a resposta final
    
    except Exception as e:
        return {"error": f"Erro durante inferência dos modelos: {e}"}, 500

    if not final_probs:
         return {"error": "Nenhum modelo conseguiu processar a solicitação"}, 500

    top_diagnosis_winner = max(final_probs, key=final_probs.get)

    # 4. Persistência e Log
    try:
        user = User.query.get(user_id)
        if not user: return {"error": "Usuário não encontrado"}, 404

        new_diag = ArbovirusDiagnosis(
            user_id=user_id,
            user_email=user.email,
            username=user.username,
            age=age,
            sex=sex,
            text_description=text_description,
            structured_symptoms=structured,
            input_features=input_features_log,
            prediction_result=convert_numpy_floats(final_probs), # Salva probs do vencedor
            top_diagnosis=top_diagnosis_winner,
            model_version=f"Winner_{best_model_name}", # Registra quem ganhou
        )
        db.session.add(new_diag)
        db.session.commit()
        print(f"Diagnóstico Arbo salvo ID: {new_diag.id} (Vencedor: {best_model_name})")

    except Exception as e:
        db.session.rollback()
        return {"error": f"Erro na Persistência: {str(e)}"}, 500

    # 5. Explicação Amigável (Baseada no vencedor)
    try:
        res_txt = "\n".join([f"{k}: {v:.1%}" for k, v in final_probs.items()])
        prompt_friendly = f"Explique para paciente ({age} anos): Sintomas: {text_description}. Probabilidades: {res_txt}. Mais provável: {top_diagnosis_winner}. USE DISCLAIMER: NÃO É DIAGNÓSTICO."
        friendly = model_gemini.generate_content(prompt_friendly).text
    except Exception:
        friendly = "Erro ao gerar explicação amigável."

    # 6. Retorno Completo
    return {
        "friendly_response": friendly,
        "analysis_details": {
            "probabilities": convert_numpy_floats(final_probs),
            "structured_symptoms": structured,
            "diagnosis_id": new_diag.id,
            "winner_model": best_model_name,
            "comparative_stats": comparative_results # Frontend vai usar isso para gráficos!
        },
    }, 200


def run_symptom_structure(text_description):
    if not model_gemini:
        return {"error": "Gemini off"}, 503
    symptoms = get_symptom_list_from_cols(arbo_model_columns)
    try:
        resp = model_gemini.generate_content(
            f'Analise: "{text_description}". JSON true/false: {symptoms}.'
        )
        return parse_json_from_gemini_response(resp.text), 200
    except Exception as e:
        return {"error": str(e)}, 500


def run_glaucoma_pipeline(image_bytes, user_id):
    if not glaucoma_cnn_model:
        return {"error": "Modelo CNN off"}, 503

    img_batch = preprocess_glaucoma_image(
        image_bytes, (GLAUCOMA_IMG_SIZE, GLAUCOMA_IMG_SIZE)
    )
    if img_batch is None:
        return {"error": "Imagem inválida"}, 400

    try:
        pred = glaucoma_cnn_model.predict(img_batch)[0][0]
        prob_normal = float(pred)
        prob_glaucoma = 1.0 - prob_normal
        results = {
            GLAUCOMA_CLASS_NAMES[0]: prob_glaucoma,
            GLAUCOMA_CLASS_NAMES[1]: prob_normal,
        }

        if prob_normal >= 0.5:
            predicted_class = "Normal"
            confidence = prob_normal
        else:
            predicted_class = "Glaucomatous"
            confidence = prob_glaucoma
            
        user = User.query.get(user_id)
        if not user:
            return {"error": "Usuário não encontrado para log"}, 404

        new_diag = GlaucomaDiagnosis(
            user_id=user_id,
            user_email=user.email,
            username=user.username,
            prediction_result=convert_numpy_floats(results),
            predicted_class=predicted_class,
            confidence=float(confidence),
            model_version="MobileNetV2_FineTuned",
        )
        db.session.add(new_diag)
        db.session.commit()

        friendly = model_gemini.generate_content(
            f"Analise Glaucoma. Prob: {results}. Explique PRELIMINAR. Consulte oftalmo."
        ).text
    except Exception as e:
        db.session.rollback()
        return {"error": f"Erro no processamento/persistência: {e}"}, 500

    return {
        "friendly_response": friendly,
        "analysis_details": {"probabilities": results, "diagnosis_id": new_diag.id},
    }, 200