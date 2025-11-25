# backend/optimize_ga_arbovirus.py
import pandas as pd
import numpy as np
import random
import json
import os
from sqlalchemy import create_engine
from xgboost import XGBClassifier
from sklearn.model_selection import cross_val_score, StratifiedKFold

# --- CONFIGURAÇÕES DO AG ---
POPULATION_SIZE = 10
GENERATIONS = 5
MUTATION_RATE = 0.1
TOURNAMENT_SIZE = 3
CV_FOLDS = 3

# --- LIMITADORES DE DADOS (CRUCIAL PARA PERFORMANCE) ---
LIMIT_FOR_GA = 100000  # Define o limite aqui em cima para não dar erro

# Caminho para salvar o resultado
ARTIFACTS_DIR = "/app/model_artifacts"
BEST_PARAMS_PATH = os.path.join(ARTIFACTS_DIR, 'best_hyperparameters.json')

# --- 1. DEFINIÇÃO DOS GENES (Espaço de Busca) ---
PARAM_GRID = {
    'n_estimators': {'type': 'int', 'min': 50, 'max': 300},    
    'max_depth': {'type': 'int', 'min': 3, 'max': 10},         
    'learning_rate': {'type': 'float', 'min': 0.01, 'max': 0.3},
    'subsample': {'type': 'float', 'min': 0.5, 'max': 1.0},     
    'colsample_bytree': {'type': 'float', 'min': 0.5, 'max': 1.0}, 
    'gamma': {'type': 'float', 'min': 0, 'max': 5}              
}

# --- FUNÇÕES AUXILIARES ---

def get_db_connection():
    DB_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@db:5432/{os.getenv('POSTGRES_DB')}"
    return create_engine(DB_URL)

def load_data():
    """Carrega os dados limpos do banco com AMOSTRAGEM"""
    engine = get_db_connection()
    print("Carregando dados para otimização...")
    try:
        # Lê apenas as colunas se o json existir (mais rápido), ou lê tudo se não existir
        cols_path = os.path.join(ARTIFACTS_DIR, 'model_columns.json')
        if os.path.exists(cols_path):
            with open(cols_path, 'r') as f:
                feature_cols = json.load(f)
            # Adiciona target
            cols_query = feature_cols + ['target_encoded']
            cols_str = ', '.join([f'"{c}"' for c in cols_query])
            
            # Lê do banco
            df = pd.read_sql(f'SELECT {cols_str} FROM cleaned_arboviroses_cases', engine)
        else:
            df = pd.read_sql('SELECT * FROM cleaned_arboviroses_cases', engine)
            feature_cols = [c for c in df.columns if c not in ['doenca_alvo', 'target_encoded', 'dt_notific', 'id_municip']]

        # --- APLICA A AMOSTRAGEM AQUI ---
        total_rows = len(df)
        if total_rows > LIMIT_FOR_GA:
            print(f"Dataset grande ({total_rows} linhas). Usando amostra de {LIMIT_FOR_GA} para o AG.")
            df = df.sample(n=LIMIT_FOR_GA, random_state=42)
        else:
            print(f"Dataset dentro do limite ({total_rows} linhas). Usando completo.")
        # --------------------------------
            
        X = df[feature_cols]
        y = df['target_encoded']
        return X, y
    except Exception as e:
        print(f"Erro ao carregar dados: {e}")
        return None, None

# --- IMPLEMENTAÇÃO DO AG ---

def create_individual():
    individual = {}
    for key, limits in PARAM_GRID.items():
        if limits['type'] == 'int':
            individual[key] = random.randint(limits['min'], limits['max'])
        else:
            individual[key] = random.uniform(limits['min'], limits['max'])
    return individual

def fitness_function(params, X, y):
    """Calcula F1-Score Macro com Cross-Validation."""
    model = XGBClassifier(
        objective='multi:softmax',
        num_class=3,
        n_jobs=-1,
        tree_method='hist',
        random_state=42,
        **params
    )
    
    skf = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=42)
    scores = cross_val_score(model, X, y, cv=skf, scoring='f1_macro')
    
    return scores.mean()

def selection(population, fitnesses):
    selected = []
    for _ in range(len(population)):
        aspirants_idxs = random.sample(range(len(population)), TOURNAMENT_SIZE)
        best_idx = aspirants_idxs[0]
        for idx in aspirants_idxs[1:]:
            if fitnesses[idx] > fitnesses[best_idx]:
                best_idx = idx
        selected.append(population[best_idx])
    return selected

def crossover(parent1, parent2):
    child1, child2 = {}, {}
    for key in PARAM_GRID.keys():
        if random.random() < 0.5:
            child1[key] = parent1[key]
            child2[key] = parent2[key]
        else:
            child1[key] = parent2[key]
            child2[key] = parent1[key]
    return child1, child2

def mutation(individual):
    for key in individual.keys():
        if random.random() < MUTATION_RATE:
            limits = PARAM_GRID[key]
            if limits['type'] == 'int':
                individual[key] = random.randint(limits['min'], limits['max'])
            else:
                individual[key] = random.uniform(limits['min'], limits['max'])
    return individual

# --- LOOP PRINCIPAL ---

def run_genetic_algorithm():
    X, y = load_data()
    if X is None: return

    print(f"\n--- Iniciando AG (População: {POPULATION_SIZE}, Gerações: {GENERATIONS}) ---")
    
    population = [create_individual() for _ in range(POPULATION_SIZE)]
    
    best_overall_params = None
    best_overall_fitness = -1.0

    for generation in range(GENERATIONS):
        print(f"\nGeração {generation + 1}/{GENERATIONS}...")
        
        fitnesses = []
        for i, ind in enumerate(population):
            fit = fitness_function(ind, X, y)
            fitnesses.append(fit)
        
        gen_best_idx = np.argmax(fitnesses)
        gen_best_fit = fitnesses[gen_best_idx]
        print(f"  Melhor da Geração: {gen_best_fit:.4f}")

        if gen_best_fit > best_overall_fitness:
            best_overall_fitness = gen_best_fit
            best_overall_params = population[gen_best_idx]
        
        selected_parents = selection(population, fitnesses)
        
        next_population = []
        next_population.append(best_overall_params) # Elitismo
        
        while len(next_population) < POPULATION_SIZE:
            parent1 = random.choice(selected_parents)
            parent2 = random.choice(selected_parents)
            child1, child2 = crossover(parent1, parent2)
            child1 = mutation(child1)
            child2 = mutation(child2)
            next_population.append(child1)
            if len(next_population) < POPULATION_SIZE:
                next_population.append(child2)
        
        population = next_population

    print("\n--- Otimização Concluída ---")
    print(f"Melhor F1-Macro encontrado: {best_overall_fitness:.4f}")
    print(f"Melhores Parâmetros: {best_overall_params}")

    with open(BEST_PARAMS_PATH, 'w') as f:
        json.dump(best_overall_params, f, indent=4)
    print(f"Parâmetros salvos em: {BEST_PARAMS_PATH}")

if __name__ == "__main__":
    run_genetic_algorithm()