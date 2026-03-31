import os
import json
import random
import traceback
from datetime import datetime
from typing import Any
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier
from sqlalchemy import create_engine, text

# 👇 Imports ajustados para a nova arquitetura
from backend.modules.auth.models.user_model import db, User
from backend.modules.laboratory.models.ml_log_model import ModelTrainingLog

# Configurações de diretório para os artefatos base (ajuste se necessário)
ARTIFACTS_DIR = "/app/model_artifacts"
CACHED_TRAIN_DATA = None


# ==========================================
# 📊 CARREGAMENTO DE DADOS (COM CACHE)
# ==========================================
def get_training_data_sample(limit=50000):
    global CACHED_TRAIN_DATA
    if CACHED_TRAIN_DATA is not None:
        return CACHED_TRAIN_DATA

    print("⏳ [LABORATORY] Carregando amostra de dados para o Playground...")
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
        else:
            print("❌ Arquivo model_columns.json não encontrado.")
            return None, None
    except Exception as e:
        print(f"Erro carregando dados: {e}")
        return None, None


# ==========================================
# 🧬 CLASSE DE OTIMIZAÇÃO (ALGORITMO GENÉTICO)
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


# ==========================================
# 🧪 SERVIÇOS DO LABORATÓRIO (EXPERIMENTOS)
# ==========================================


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

            # 👇 TYPE GUARD: Garante que 'y' não é None e calcula as classes com segurança
            if y is None:
                return {"error": "Dados alvo (y) não definidos ou vazios"}, 400

            num_classes = int(
                y.nunique() if hasattr(y, "nunique") else len(np.unique(y))
            )

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
            with conn.begin():
                conn.execute(insert_query, log_entry_orm)

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

        def clean_numpy(obj: Any) -> Any:
            """Converte tipos do NumPy para tipos nativos do Python à prova de Pylance."""
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            # 👇 O Pulo do Gato: se for um número do NumPy, extraímos o valor nativo
            elif hasattr(obj, "item") and callable(getattr(obj, "item")):
                return obj.item()
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
            user_id=user_id,
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
