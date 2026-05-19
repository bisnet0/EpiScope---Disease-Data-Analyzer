import os
import json
import random
import traceback
from datetime import datetime
from typing import cast, Dict, Any, Tuple
import numpy as np
import pandas as pd
import tensorflow as tf
import google.generativeai as genai

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier

# 👇 Imports ajustados para a nova arquitetura
from backend.modules.auth.models.user_model import db, User
from backend.modules.laboratory.models.ml_log_model import ModelTrainingLog
from backend.modules.glaucoma.models.glaucoma_model import (
    GlaucomaDiagnosis,
)  # 👈 Nome do arquivo atualizado
from backend.utils.data_helpers import convert_numpy_floats, preprocess_glaucoma_image

# ==========================================
# 📂 RESOLUÇÃO DINÂMICA DE CAMINHOS
# ==========================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODULE_DIR = os.path.dirname(SCRIPT_DIR)
TRAIN_RESULTS_DIR = os.path.join(MODULE_DIR, "train_results")

# Configuração do Gemini VLM
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))  # type: ignore
    model_gemini = genai.GenerativeModel("gemini-2.5-flash-lite")  # type: ignore
except Exception as e:
    print(f"Erro Gemini: {e}")
    model_gemini = None

# Carregamento do modelo CNN de Glaucoma
try:
    glaucoma_cnn_model = tf.keras.models.load_model(
        os.path.join(TRAIN_RESULTS_DIR, "glaucoma_cnn_model.h5")
    )
    with open(os.path.join(TRAIN_RESULTS_DIR, "glaucoma_info.json"), "r") as f:
        g_info = json.load(f)
    GLAUCOMA_CLASS_NAMES = g_info.get("class_names", ["Normal", "Glaucomatous"])
    GLAUCOMA_IMG_SIZE = g_info.get("image_size", 224)
    print("✅ [GLAUCOMA SERVICE] Modelo CNN e Metadados carregados com sucesso!")
except Exception as e:
    print(f"⚠️ [GLAUCOMA SERVICE] Modelos não encontrados: {e}")
    glaucoma_cnn_model = None
    GLAUCOMA_CLASS_NAMES = ["Normal", "Glaucomatous"]
    GLAUCOMA_IMG_SIZE = 224


# ==========================================
# 🧠 CLASSE DE OTIMIZAÇÃO (ALGORITMO GENÉTICO)
# ==========================================
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

            model.fit(self.X_train, self.y_train)  # type: ignore
            acc = accuracy_score(self.y_test, model.predict(self.X_test))  # type: ignore
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
                if acc > best_overall["accuracy"]:  # type: ignore
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


# ==========================================
# 👁️ SERVIÇOS PRINCIPAIS DE GLAUCOMA
# ==========================================


def get_glaucoma_embeddings_sample(limit=1000):
    """Gera dados sintéticos imitando embeddings da CNN."""
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


def run_glaucoma_pipeline(image_bytes, user_id):
    if not glaucoma_cnn_model or not model_gemini:
        return {"error": "Modelo CNN ou VLM offline"}, 503

    img_batch = preprocess_glaucoma_image(
        image_bytes, (GLAUCOMA_IMG_SIZE, GLAUCOMA_IMG_SIZE)
    )
    if img_batch is None:
        return {"error": "Imagem inválida ou corrompida"}, 400

    try:
        pred = glaucoma_cnn_model.predict(img_batch)[0][0]  # type: ignore
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

        vlm_response = model_gemini.generate_content([vlm_prompt, image_parts[0]])  # type: ignore
        laudo_vlm = vlm_response.text

        user = User.query.get(user_id)  # type: ignore
        if not user:
            return {"error": "Usuário não encontrado para log"}, 404

        # 👇 PULO DO GATO: Prometendo pro Pylance que é um dicionário e validando as tipagens
        new_diag = GlaucomaDiagnosis(
            user_id=user_id,
            user_email=str(user.email),
            username=str(user.username),
            prediction_result=cast(Dict[str, Any], convert_numpy_floats(results)),
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

    if X is None or y is None:
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
        user = User.query.get(user_id)  # type: ignore
        username = str(user.username) if user else "unknown"

        log_name = f"Glaucoma_EXP_{model_type.upper()}_HYBRID_{username}"

        def clean_numpy(obj: Any) -> Any:
            """Converte tipos do NumPy para tipos nativos do Python à prova de Pylance."""
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            # Se for um número do NumPy (np.int64, np.float32, etc), ele terá o método .item()
            elif hasattr(obj, "item") and callable(getattr(obj, "item")):
                return obj.item()
            return obj

        # Type guard para evitar o KeyError
        best_params = best.get("params", {})
        clean_params = {k: clean_numpy(v) for k, v in best_params.items()}  # type: ignore

        final_params = {
            "model_params": clean_params,
            "ga_config": {
                "generations": GENS,
                "population_size": POP_SIZE,
                "mutation_rate": MUT_RATE,
                "crossover_rate": CROSS_RATE,
            },
        }

        # Type guard para o accuracy que pode vir do dicionário vazio
        best_acc = best.get("accuracy", 0.0)

        log_entry = ModelTrainingLog(
            user_id=user_id,
            model_name=log_name,
            version="GA_Hybrid_v1",
            parameters=json.dumps(final_params),
            feature_importance=None,
            metrics=json.dumps({"history": history}, default=clean_numpy),
            accuracy=float(best_acc),  # type: ignore
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
