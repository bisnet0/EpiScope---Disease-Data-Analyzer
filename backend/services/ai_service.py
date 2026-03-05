from datetime import datetime
import os
import random
import traceback

import numpy as np
import joblib
import json
import pandas as pd
import tensorflow as tf
import google.generativeai as genai
from backend.models.user_model import db, User
from backend.models.ml_log_model import ModelTrainingLog
from backend.models.diagnosis_model import ArbovirusDiagnosis, GlaucomaDiagnosis
from backend.utils.data_helpers import (
    parse_json_from_gemini_response,
    get_symptom_list_from_cols,
    convert_numpy_floats,
    preprocess_glaucoma_image,
)
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier
from sqlalchemy import create_engine, text

ARTIFACTS_DIR = "/app/model_artifacts"
CACHED_TRAIN_DATA = None
print("--- Inicializando AI Service (Multi-Model) ---")


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
        else:
            print(f"⚠️ {key} não encontrado (pule se não treinou ainda).")

    if not ARBO_MODELS:
        old_path = os.path.join(ARTIFACTS_DIR, "xgboost_model.joblib")
        if os.path.exists(old_path):
            ARBO_MODELS["legacy_xgboost"] = joblib.load(old_path)
            print("⚠️ Usando modelo Legacy XGBoost.")

except Exception as e:
    print(f"Erro fatal carregando modelos Arbo: {e}")


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
    X, y = get_training_data_sample()
    if X is None:
        return {"error": "Falha ao carregar dados de treino"}, 500

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )

    try:
        if model_type == "random_forest":
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

        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, output_dict=True)

        user = User.query.get(user_id)
        username = user.username if user else "unknown"

        log_entry_orm = {
            "model_name": f"EXP_{model_type.upper()}_{username}",
            "version": "playground",
            "parameters": json.dumps(params),
            "feature_importance": None,
            "metrics": json.dumps(report),
            "accuracy": float(acc),
            "dataset_size": len(X),
            "created_at": pd.Timestamp.utcnow(),
        }

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

        model_type = "xgboost"
        if "forest" in model_name.lower():
            model_type = "random_forest"
        elif "decision" in model_name.lower():
            model_type = "decision_tree"
        elif "xgboost" in model_name.lower():
            model_type = "xgboost"

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
                "origin": model_name,
            },
        }, 200

    except Exception as e:
        print(f"Erro no Advisor: {e}")
        return {"error": str(e)}, 500


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
        # prompt_friendly = f"Explique para paciente ({age} anos): Sintomas: {text_description}. Probabilidades: {res_txt}. Mais provável: {top_diagnosis_winner}. USE DISCLAIMER: NÃO É DIAGNÓSTICO."
        # friendly = model_gemini.generate_content(prompt_friendly).text
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
    if not glaucoma_cnn_model or not model_gemini:
        return {"error": "Modelo CNN ou VLM offline"}, 503

    # 1. PREDIÇÃO DA CNN (O Instinto Matemático)
    img_batch = preprocess_glaucoma_image(
        image_bytes, (GLAUCOMA_IMG_SIZE, GLAUCOMA_IMG_SIZE)
    )
    if img_batch is None:
        return {"error": "Imagem inválida ou corrompida"}, 400

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

        # 2. ANÁLISE DO VLM (O Raciocínio Clínico)
        # Preparamos a imagem no formato que o Gemini exige
        image_parts = [{"mime_type": "image/jpeg", "data": image_bytes}]

        vlm_prompt = f"""
        Você é o Dr. EpiScope, um oftalmologista especialista em IA.
        Um modelo de Rede Neural (CNN) analisou esta imagem de fundo de olho e 
        previu com {confidence * 100:.1f}% de confiança que a classe é: {predicted_class}.
        
        Sua tarefa:
        1. Analise visualmente a imagem anexada.
        2. Verifique se há sinais de glaucoma (aumento da escavação do disco óptico, palidez, hemorragias).
        3. Escreva um laudo técnico curto confirmando ou discordando da CNN, explicando o PORQUÊ com base no que você vê na imagem.
        """

        # Enviamos o texto E a imagem juntos
        vlm_response = model_gemini.generate_content([vlm_prompt, image_parts[0]])
        laudo_vlm = vlm_response.text

        # 3. SALVAR NO BANCO DE DADOS
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
            model_version="Hybrid_CNN_VLM_v1",
        )
        db.session.add(new_diag)
        db.session.commit()

        return {
            "friendly_response": laudo_vlm,
            "analysis_details": {
                "probabilities": results,
                "diagnosis_id": new_diag.id,
                "cnn_prediction": predicted_class,
            },
        }, 200

    except Exception as e:
        db.session.rollback()
        return {"error": f"Erro no processamento Híbrido: {e}"}, 500


def run_glaucoma_genetic_pipeline(model_type, user_id, ga_config=None):
    if ga_config is None:
        ga_config = {
            "generations": 5,
            "population_size": 8,
            "mutation_rate": 0.1,
            "crossover_rate": 0.7,
        }

    X, y = get_glaucoma_embeddings_sample(limit=2000)

    if X is None:
        return {"error": "Falha ao carregar vetores de imagem"}, 500

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )

    GENS = int(ga_config.get("generations", 5))
    POP_SIZE = int(ga_config.get("population_size", 8))
    MUT_RATE = float(ga_config.get("mutation_rate", 0.1))
    CROSS_RATE = float(ga_config.get("crossover_rate", 0.7))

    optimizer = GeneticOptimizer(
        model_type,
        X_train,
        y_train,
        X_test,
        y_test,
        mutation_rate=MUT_RATE,
        crossover_rate=CROSS_RATE,
    )
    history, best = optimizer.run(generations=GENS, population_size=POP_SIZE)

    try:
        user = User.query.get(user_id)
        username = user.username if user else "unknown"

        log_name = f"Glaucoma_EXP_{model_type.upper()}_HYBRID_{username}"

        def clean_numpy(obj):
            if isinstance(obj, (np.integer, np.int64)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float64, np.float32)):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            return obj

        clean_params = {k: clean_numpy(v) for k, v in best["params"].items()}

        final_params = {
            "model_params": clean_params,
            "ga_config": {
                "generations": GENS,
                "population_size": POP_SIZE,
                "mutation_rate": MUT_RATE,
                "crossover_rate": CROSS_RATE,
            },
        }

        log_entry = ModelTrainingLog(
            model_name=log_name,
            version="GA_Hybrid_v1",
            parameters=json.dumps(final_params),
            feature_importance=None,
            metrics=json.dumps({"history": history}, default=clean_numpy),
            accuracy=float(best["accuracy"]),
            dataset_size=len(X),
            created_at=datetime.utcnow(),
        )

        db.session.add(log_entry)
        db.session.commit()
        print(f"✅ SUCESSO! Log salvo: {log_name} com params dinâmicos.")

    except Exception as e:
        db.session.rollback()
        print(f"❌ ERRO AO SALVAR NO DB: {str(e)}")
        traceback.print_exc()

    return {
        "success": True,
        "history": history,
        "best_individual": best,
        "note": "Otimização realizada com sucesso.",
    }, 200


def get_glaucoma_embeddings_sample(limit=1000):
    """
    Gera dados sintéticos que imitam vetores extraídos de uma CNN (ex: ResNet/VGG).
    Isso permite rodar o AG rapidamente sem processar gigabytes de imagens.
    """
    try:
        np.random.seed(42)

        X = np.random.rand(limit, 20)

        y = (X[:, 0] * X[:, 1] + X[:, 2] > 0.8).astype(int)

        feature_names = [f"cnn_feature_{i}" for i in range(20)]
        X_df = pd.DataFrame(X, columns=feature_names)
        y_series = pd.Series(y, name="target")

        return X_df, y_series
    except Exception as e:
        print(f"Erro ao gerar embeddings: {e}")
        return None, None


def get_training_data_sample(limit=50000):
    global CACHED_TRAIN_DATA
    if CACHED_TRAIN_DATA is not None:
        return CACHED_TRAIN_DATA

    print("⏳ Carregando amostra de dados para o Playground...")
    try:
        db_url = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@db:5432/{os.getenv('POSTGRES_DB')}"
        engine = create_engine(db_url)

        cols_path = os.path.join(ARTIFACTS_DIR, "model_columns.json")
        if os.path.exists(cols_path):
            with open(cols_path, "r") as f:
                feature_cols = json.load(f)
            cols_query = feature_cols + ["target_encoded"]
            cols_str = ", ".join([f'"{c}"' for c in cols_query])

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
    def __init__(
        self,
        model_type,
        X_train,
        y_train,
        X_test,
        y_test,
        mutation_rate=0.1,
        crossover_rate=0.7,
    ):
        self.model_type = model_type
        self.X_train = X_train
        self.y_train = y_train
        self.X_test = X_test
        self.y_test = y_test
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate

    def get_random_gene(self, param_name):
        ranges = {
            "n_estimators": lambda: random.randint(50, 500),
            "max_depth": lambda: random.randint(3, 20),
            "learning_rate": lambda: round(random.uniform(0.01, 0.5), 3),
            "subsample": lambda: round(random.uniform(0.5, 1.0), 2),
            "colsample_bytree": lambda: round(random.uniform(0.5, 1.0), 2),
            "gamma": lambda: round(random.uniform(0, 5), 2),
            "min_samples_split": lambda: random.randint(2, 20),
            "min_samples_leaf": lambda: random.randint(1, 10),
            "criterion": lambda: random.choice(["gini", "entropy", "log_loss"]),
        }
        return ranges.get(param_name, lambda: 0)()

    def create_individual(self):
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
        try:
            if self.model_type == "xgboost":
                num_classes = (
                    self.y_train.nunique()
                    if hasattr(self.y_train, "nunique")
                    else len(np.unique(self.y_train))
                )
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
        population = [self.create_individual() for _ in range(population_size)]
        history = []
        best_overall = {"accuracy": 0, "params": {}}

        print(
            f"🧬 AG Iniciado: Mut={self.mutation_rate}, Cross={self.crossover_rate}, Pop={population_size}"
        )

        for gen in range(generations):
            scores = []
            for indiv in population:
                acc = self.evaluate(indiv)
                scores.append((acc, indiv))
                if acc > best_overall["accuracy"]:
                    best_overall = {"accuracy": acc, "params": indiv}

            scores.sort(key=lambda x: x[0], reverse=True)

            history.append(
                {
                    "generation": gen + 1,
                    "best_accuracy": float(scores[0][0]),
                    "avg_accuracy": float(np.mean([s[0] for s in scores])),
                }
            )

            top_half = [s[1] for s in scores[: max(1, population_size // 2)]]

            new_population = top_half[:]
            while len(new_population) < population_size:
                parent1 = random.choice(top_half)
                parent2 = random.choice(top_half)
                child = parent1.copy()

                for k in child.keys():
                    if random.random() < self.crossover_rate:
                        child[k] = parent2[k]

                if random.random() < self.mutation_rate:
                    gene_to_mutate = random.choice(list(child.keys()))
                    child[gene_to_mutate] = self.get_random_gene(gene_to_mutate)

                new_population.append(child)

            population = new_population

        return history, best_overall


def run_genetic_pipeline(model_type, user_id, ga_config=None):
    if ga_config is None:
        ga_config = {
            "generations": 5,
            "population_size": 10,
            "mutation_rate": 0.1,
            "crossover_rate": 0.7,
        }

    X, y = get_training_data_sample(limit=5000)
    if X is None:
        return {"error": "Sem dados"}, 500

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )

    GENS = int(ga_config.get("generations", 5))
    POP_SIZE = int(ga_config.get("population_size", 10))
    MUT_RATE = float(ga_config.get("mutation_rate", 0.1))
    CROSS_RATE = float(ga_config.get("crossover_rate", 0.7))

    optimizer = GeneticOptimizer(
        model_type,
        X_train,
        y_train,
        X_test,
        y_test,
        mutation_rate=MUT_RATE,
        crossover_rate=CROSS_RATE,
    )

    history, best = optimizer.run(generations=GENS, population_size=POP_SIZE)

    try:
        user = User.query.get(user_id)
        username = user.username if user else "unknown"

        log_name = f"EXP_{model_type.upper()}_GA_{username}"

        def clean_numpy(obj):
            if isinstance(obj, (np.integer, np.int64)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float64, np.float32)):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            return obj

        clean_model_params = {k: clean_numpy(v) for k, v in best["params"].items()}

        final_params = {
            "model_params": clean_model_params,
            "ga_config": {
                "generations": GENS,
                "population_size": POP_SIZE,
                "mutation_rate": MUT_RATE,
                "crossover_rate": CROSS_RATE,
            },
        }

        log = ModelTrainingLog(
            model_name=log_name,
            version="GA_Arbo_v1",
            accuracy=float(best["accuracy"]),
            metrics=json.dumps({"history": history}, default=clean_numpy),
            parameters=json.dumps(final_params),
            dataset_size=len(X),
            created_at=datetime.utcnow(),
        )

        db.session.add(log)
        db.session.commit()
        print(f"✅ SUCESSO ARBO! Log salvo: {log_name}")

    except Exception as e:
        print(f"❌ ERRO AO SALVAR ARBO NO DB: {e}")
        traceback.print_exc()
        db.session.rollback()

    return {"success": True, "history": history, "best_individual": best}, 200
