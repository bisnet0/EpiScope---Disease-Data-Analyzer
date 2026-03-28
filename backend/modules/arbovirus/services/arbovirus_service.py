import os
import json
import joblib
import pandas as pd
import google.generativeai as genai

# 👇 Imports ajustados para a nova arquitetura
from backend.modules.auth.models.user_model import db, User
from backend.modules.arbovirus.models.diagnosis_model import ArbovirusDiagnosis
from backend.utils.data_helpers import (
    parse_json_from_gemini_response,
    get_symptom_list_from_cols,
    convert_numpy_floats,
)

# Caminho dinâmico para os artefatos de ML do Arbovírus
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODULE_DIR = os.path.dirname(SCRIPT_DIR)
ARTIFACTS_DIR = "/app/model_artifacts" # Ou a pasta de artefatos que você configurou

try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model_gemini = genai.GenerativeModel("gemini-2.5-flash-lite")
except Exception as e:
    print(f"Erro Gemini: {e}")
    model_gemini = None

ARBO_MODELS = {}
arbo_model_columns = []
arbo_target_map = {}

try:
    with open(os.path.join(ARTIFACTS_DIR, "model_columns.json"), "r") as f:
        arbo_model_columns = json.load(f)
    with open(os.path.join(ARTIFACTS_DIR, "target_map.json"), "r") as f:
        arbo_target_map = {int(k): v for k, v in json.load(f).items()}

    model_files = {
        "xgboost_standard": "xgboost_standard.joblib",
        "xgboost_genetic": "xgboost_genetic.joblib",
        "random_forest": "randomforest.joblib",
        "decision_tree": "decisiontree.joblib",
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

    if not ARBO_MODELS:
        old_path = os.path.join(ARTIFACTS_DIR, "xgboost_model.joblib")
        if os.path.exists(old_path):
            ARBO_MODELS["legacy_xgboost"] = joblib.load(old_path)
            print("⚠️ Usando modelo Legacy XGBoost.")

except Exception as e:
    print(f"Erro fatal carregando modelos Arbo: {e}")

def run_arbovirus_pipeline(text_description, age, sex, user_id, model_choice="all"):
    if not ARBO_MODELS or not model_gemini:
        return {"error": "Serviços de IA indisponíveis"}, 503

    symptoms_list = get_symptom_list_from_cols(arbo_model_columns)
    prompt = f'Analise: "{text_description}". Extraia sintomas JSON true/false. Possíveis: {symptoms_list}.'
    try:
        gemini_resp = model_gemini.generate_content(prompt)
        structured = parse_json_from_gemini_response(gemini_resp.text)
        if not structured:
            raise ValueError("Falha ao estruturar JSON")
    except Exception as e:
        return {"error": f"Erro na IA Generativa: {str(e)}"}, 500

    try:
        df = pd.DataFrame(columns=arbo_model_columns, index=[0]).fillna(0)
        for s, v in structured.items():
            if s in df.columns and v:
                df.loc[0, s] = 1
        df.loc[0, "idade"] = age
        df.loc[0, "sexo_encoded"] = 1 if sex.upper() == "F" else 0
        df = df.apply(pd.to_numeric, errors="coerce").fillna(0)

        input_features_log = convert_numpy_floats(df.to_dict(orient="records")[0])
    except Exception as e:
        return {"error": f"Erro no pré-processamento de dados: {e}"}, 500

    comparative_results = {}
    best_model_name = "none"
    highest_confidence = -1.0
    final_probs = {}

    models_to_run = (
        ARBO_MODELS
        if model_choice == "all"
        else {model_choice: ARBO_MODELS.get(model_choice)}
    )

    try:
        for name, model in models_to_run.items():
            if not model:
                continue

            probs = model.predict_proba(df[arbo_model_columns])[0]
            model_result = {arbo_target_map[i]: float(p) for i, p in enumerate(probs)}

            top_disease = max(model_result, key=model_result.get)
            confidence = model_result[top_disease]

            comparative_results[name] = {
                "diagnosis": top_disease,
                "confidence": confidence,
                "full_probs": model_result,
            }

            if confidence > highest_confidence:
                highest_confidence = confidence
                best_model_name = name
                final_probs = model_result

    except Exception as e:
        return {"error": f"Erro durante inferência dos modelos: {e}"}, 500

    if not final_probs:
        return {"error": "Nenhum modelo conseguiu processar a solicitação"}, 500

    top_diagnosis_winner = max(final_probs, key=final_probs.get)

    try:
        user = User.query.get(user_id)
        if not user:
            return {"error": "Usuário não encontrado"}, 404

        new_diag = ArbovirusDiagnosis(
            user_id=user_id,
            user_email=user.email,
            username=user.username,
            age=age,
            sex=sex,
            text_description=text_description,
            structured_symptoms=structured,
            input_features=input_features_log,
            prediction_result=convert_numpy_floats(final_probs),
            top_diagnosis=top_diagnosis_winner,
            model_version=f"Winner_{best_model_name}",
        )
        db.session.add(new_diag)
        db.session.commit()
        print(f"Diagnóstico Arbo salvo ID: {new_diag.id} (Vencedor: {best_model_name})")

    except Exception as e:
        db.session.rollback()
        return {"error": f"Erro na Persistência: {str(e)}"}, 500

    try:
        res_txt = "\n".join([f"{k}: {v:.1%}" for k, v in final_probs.items()])
        friendly = "Explicação desativada para economia de cota."
    except Exception:
        friendly = "Erro ao gerar explicação amigável."

    return (
        {
            "friendly_response": friendly,
            "analysis_details": {
                "probabilities": convert_numpy_floats(final_probs),
                "structured_symptoms": structured,
                "diagnosis_id": new_diag.id,
                "winner_model": best_model_name,
                "comparative_stats": comparative_results,
            },
        },
        200,
    )