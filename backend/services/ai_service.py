import os
import random

import numpy as np
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
from sklearn.model_selection import train_test_split  # <--- NOVO
from sklearn.metrics import accuracy_score, classification_report  # <--- NOVO
from sklearn.ensemble import RandomForestClassifier  # <--- NOVO
from sklearn.tree import DecisionTreeClassifier  # <--- NOVO
from xgboost import XGBClassifier  # <--- NOVO
from sqlalchemy import create_engine, text  # <--- NOV

ARTIFACTS_DIR = "/app/model_artifacts"
CACHED_TRAIN_DATA = None
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
        "xgboost_genetic": "xgboost_genetic.joblib",  # Só vai existir se rodou o AG
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


def run_experiment_pipeline(user_id, model_type, params):
    # 1. Carrega dados (Amostra)
    X, y = get_training_data_sample()
    if X is None:
        return {"error": "Falha ao carregar dados de treino"}, 500

    # 2. Split (Treino/Teste na hora)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )

    # 3. Instancia o Modelo baseado nos parâmetros do Front
    try:
        if model_type == "random_forest":
            # Converte params que vêm como string/float
            n_est = int(params.get("n_estimators", 100))
            depth = int(params.get("max_depth", 10))
            model = RandomForestClassifier(
                n_estimators=n_est, max_depth=depth, random_state=42, n_jobs=-1
            )

        elif model_type == "decision_tree":
            depth = int(params.get("max_depth", 10))
            crit = params.get("criterion", "gini")
            model = DecisionTreeClassifier(
                max_depth=depth, criterion=crit, random_state=42
            )

        elif model_type == "xgboost":
            n_est = int(params.get("n_estimators", 100))
            lr = float(params.get("learning_rate", 0.1))
            depth = int(params.get("max_depth", 6))
            # XGB precisa saber quantas classes
            num_classes = y.nunique()
            model = XGBClassifier(
                n_estimators=n_est,
                learning_rate=lr,
                max_depth=depth,
                objective="multi:softmax",
                num_class=num_classes,
                random_state=42,
                n_jobs=-1,
            )
        else:
            return {"error": "Tipo de modelo desconhecido"}, 400

        # 4. Treina (Fit)
        model.fit(X_train, y_train)

        # 5. Avalia
        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, output_dict=True)

        # 6. Salva Log do Experimento no Banco (Importante para o Admin ver depois)
        # Tenta pegar metadados do usuario
        user = User.query.get(user_id)
        username = user.username if user else "unknown"

        log_entry_orm = {
            "model_name": f"EXP_{model_type.upper()}_{username}",  # Tag diferente para experimentos
            "version": "playground",
            "parameters": json.dumps(params),
            "feature_importance": None,
            "metrics": json.dumps(report),
            "accuracy": float(acc),
            "dataset_size": len(X),
            "created_at": pd.Timestamp.utcnow(),
        }

        # Inserção SQL (Copiada do ml_train_model.py e ajustada)
        db_url = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@db:5432/{os.getenv('POSTGRES_DB')}"
        engine_log = create_engine(db_url)

        insert_query = text("""
            INSERT INTO model_training_logs 
            (model_name, version, parameters, feature_importance, metrics, accuracy, dataset_size, created_at)
            VALUES (:model_name, :version, :parameters, :feature_importance, :metrics, :accuracy, :dataset_size, :created_at)
        """)

        with engine_log.connect() as conn:
            conn.execute(insert_query, log_entry_orm)
            conn.commit()

        # 7. Retorna resultados para o Front plotar
        return {
            "success": True,
            "accuracy": acc,
            "metrics": report,
            "model_config": params,
        }, 200

    except Exception as e:
        print(f"Erro no experimento: {e}")
        return {"error": str(e)}, 500


def get_best_optimization_suggestion():
    try:
        db_url = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@db:5432/{os.getenv('POSTGRES_DB')}"
        engine_log = create_engine(db_url)

        # Busca o registro com a MAIOR acurácia da história (seja experimento ou treino oficial)
        # Ignora DecisionTree se quiser focar nos modelos complexos, mas vamos deixar geral.
        query = text("""
            SELECT model_name, parameters, accuracy 
            FROM model_training_logs 
            WHERE model_name NOT LIKE 'Glaucoma%' 
            ORDER BY accuracy DESC 
            LIMIT 1
        """)

        with engine_log.connect() as conn:
            result = conn.execute(query).fetchone()

        if not result:
            return {"error": "Nenhum dado histórico encontrado."}, 404

        model_name, params_json, acc = result

        # Normaliza o nome do modelo para o Frontend
        model_type = "xgboost"  # default
        if "forest" in model_name.lower():
            model_type = "random_forest"
        elif "decision" in model_name.lower():
            model_type = "decision_tree"
        elif "xgboost" in model_name.lower():
            model_type = "xgboost"

        # Trata o JSON (as vezes vem string do banco)
        if isinstance(params_json, str):
            import json

            params = json.loads(params_json)
        else:
            params = params_json

        return {
            "success": True,
            "suggestion": {
                "model_type": model_type,
                "accuracy": float(acc),
                "params": params,
                "origin": model_name,  # Pra saber se veio do AG ou de um teste manual
            },
        }, 200

    except Exception as e:
        print(f"Erro no Advisor: {e}")
        return {"error": str(e)}, 500


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
        if not structured:
            raise ValueError("Falha ao estruturar JSON")
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
    models_to_run = (
        ARBO_MODELS
        if model_choice == "all"
        else {model_choice: ARBO_MODELS.get(model_choice)}
    )

    try:
        for name, model in models_to_run.items():
            if not model:
                continue

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
                "full_probs": model_result,
            }

            # Lógica do "Campeão Geral" (Maior confiança vence)
            if confidence > highest_confidence:
                highest_confidence = confidence
                best_model_name = name
                final_probs = (
                    model_result  # Usa as probs do campeão para a resposta final
                )

    except Exception as e:
        return {"error": f"Erro durante inferência dos modelos: {e}"}, 500

    if not final_probs:
        return {"error": "Nenhum modelo conseguiu processar a solicitação"}, 500

    top_diagnosis_winner = max(final_probs, key=final_probs.get)

    # 4. Persistência e Log
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
            prediction_result=convert_numpy_floats(
                final_probs
            ),  # Salva probs do vencedor
            top_diagnosis=top_diagnosis_winner,
            model_version=f"Winner_{best_model_name}",  # Registra quem ganhou
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
    return (
        {
            "friendly_response": friendly,
            "analysis_details": {
                "probabilities": convert_numpy_floats(final_probs),
                "structured_symptoms": structured,
                "diagnosis_id": new_diag.id,
                "winner_model": best_model_name,
                "comparative_stats": comparative_results,  # Frontend vai usar isso para gráficos!
            },
        },
        200,
    )


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


def get_training_data_sample(limit=50000):
    global CACHED_TRAIN_DATA
    if CACHED_TRAIN_DATA is not None:
        return CACHED_TRAIN_DATA

    print("⏳ Carregando amostra de dados para o Playground...")
    try:
        db_url = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@db:5432/{os.getenv('POSTGRES_DB')}"
        engine = create_engine(db_url)

        # Lê colunas do JSON para ser consistente
        cols_path = os.path.join(ARTIFACTS_DIR, "model_columns.json")
        if os.path.exists(cols_path):
            with open(cols_path, "r") as f:
                feature_cols = json.load(f)
            cols_query = feature_cols + ["target_encoded"]
            cols_str = ", ".join([f'"{c}"' for c in cols_query])

            # Pega uma amostra aleatória do banco (rápido)
            query = f"SELECT {cols_str} FROM cleaned_arboviroses_cases ORDER BY RANDOM() LIMIT {limit}"
            df = pd.read_sql(query, engine)

            X = df[feature_cols]
            y = df["target_encoded"]

            CACHED_TRAIN_DATA = (X, y)
            print(f"✅ Dados carregados: {len(df)} linhas.")
            return X, y
    except Exception as e:
        print(f"Erro carregando dados: {e}")
        return None, None


class GeneticOptimizer:
    def __init__(self, model_type, X_train, y_train, X_test, y_test):
        self.model_type = model_type
        self.X_train = X_train
        self.y_train = y_train
        self.X_test = X_test
        self.y_test = y_test

    def get_random_gene(self, param_name):
        """Gera um valor aleatório para um gene (parâmetro)"""
        # Espaço de Busca (DNA dos Modelos)
        ranges = {
            # XGBoost DNA
            "n_estimators": lambda: random.randint(50, 500),
            "max_depth": lambda: random.randint(3, 20),
            "learning_rate": lambda: round(random.uniform(0.01, 0.5), 3),
            "subsample": lambda: round(random.uniform(0.5, 1.0), 2),
            "colsample_bytree": lambda: round(random.uniform(0.5, 1.0), 2),
            "gamma": lambda: round(random.uniform(0, 5), 2),
            # Random Forest DNA (compartilha n_estimators e max_depth)
            "min_samples_split": lambda: random.randint(2, 20),
            "min_samples_leaf": lambda: random.randint(1, 10),
            # Decision Tree DNA (compartilha max_depth, min_samples...)
            "criterion": lambda: random.choice(["gini", "entropy", "log_loss"]),
        }
        return ranges.get(param_name, lambda: 0)()

    def create_individual(self):
        """Cria um modelo com parâmetros aleatórios"""
        params = {}
        if self.model_type == "xgboost":
            params = {
                "n_estimators": self.get_random_gene("n_estimators"),
                "max_depth": self.get_random_gene("max_depth"),
                "learning_rate": self.get_random_gene("learning_rate"),
                "subsample": self.get_random_gene("subsample"),
                "colsample_bytree": self.get_random_gene("colsample_bytree"),
                "gamma": self.get_random_gene("gamma"),
            }
        elif self.model_type == "random_forest":
            params = {
                "n_estimators": self.get_random_gene("n_estimators"),
                "max_depth": self.get_random_gene("max_depth"),
                "min_samples_split": self.get_random_gene("min_samples_split"),
                "min_samples_leaf": self.get_random_gene("min_samples_leaf"),
            }
        elif self.model_type == "decision_tree":
            params = {
                "max_depth": self.get_random_gene("max_depth"),
                "min_samples_split": self.get_random_gene("min_samples_split"),
                "criterion": self.get_random_gene("criterion"),
            }
        return params

    def evaluate(self, params):
        """Treina e retorna a acurácia (Fitness Function)"""
        try:
            if self.model_type == "xgboost":
                # XGB precisa saber num_class
                num_classes = self.y_train.nunique()
                model = XGBClassifier(
                    **params,
                    objective="multi:softmax",
                    num_class=num_classes,
                    n_jobs=1,
                    random_state=42,
                )
            elif self.model_type == "random_forest":
                model = RandomForestClassifier(**params, n_jobs=1, random_state=42)
            elif self.model_type == "decision_tree":
                model = DecisionTreeClassifier(**params, random_state=42)

            model.fit(self.X_train, self.y_train)
            acc = accuracy_score(self.y_test, model.predict(self.X_test))
            return acc
        except:
            return 0.0

    def run(self, generations=5, population_size=10):
        """Executa o Algoritmo Genético"""
        population = [self.create_individual() for _ in range(population_size)]
        history = []
        best_overall = {"accuracy": 0, "params": {}}

        print(
            f"🧬 Iniciando Evolução: {self.model_type.upper()} | Gen: {generations} | Pop: {population_size}"
        )

        for gen in range(generations):
            # 1. Avaliação (Fitness)
            scores = []
            for indiv in population:
                acc = self.evaluate(indiv)
                scores.append((acc, indiv))
                if acc > best_overall["accuracy"]:
                    best_overall = {"accuracy": acc, "params": indiv}

            # Ordena pelos melhores
            scores.sort(key=lambda x: x[0], reverse=True)
            best_gen_acc = scores[0][0]

            history.append(
                {
                    "generation": gen + 1,
                    "best_accuracy": float(best_gen_acc),
                    "avg_accuracy": float(np.mean([s[0] for s in scores])),
                }
            )

            # 2. Seleção (Elitismo - mantemos os top 50%)
            top_half = [s[1] for s in scores[: population_size // 2]]

            # 3. Crossover e Mutação para preencher o resto
            new_population = top_half[:]
            while len(new_population) < population_size:
                parent1 = random.choice(top_half)
                parent2 = random.choice(top_half)
                child = parent1.copy()

                # Crossover (mistura 50% dos genes)
                for k in child.keys():
                    if random.random() > 0.5:
                        child[k] = parent2[k]

                # Mutação (10% de chance de mudar um gene aleatório)
                if random.random() < 0.2:
                    gene_to_mutate = random.choice(list(child.keys()))
                    child[gene_to_mutate] = self.get_random_gene(gene_to_mutate)

                new_population.append(child)

            population = new_population

        return history, best_overall


# --- ROTA DE SERVIÇO ---
def run_genetic_pipeline(model_type):
    # 1. Pega amostra rápida (5000 linhas para o AG ser ágil no front)
    X, y = get_training_data_sample(limit=5000)
    if X is None:
        return {"error": "Sem dados"}, 500

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )

    # 2. Inicializa e Roda o AG
    optimizer = GeneticOptimizer(model_type, X_train, y_train, X_test, y_test)

    # Roda 5 gerações com 8 indivíduos (40 treinos no total)
    # Isso deve levar ~10-20 segundos, aceitável para UX de "Loading"
    history, best = optimizer.run(generations=5, population_size=8)

    return {
        "success": True,
        "history": history,  # Para o gráfico de evolução
        "best_individual": best,  # Para preencher os sliders
    }, 200
