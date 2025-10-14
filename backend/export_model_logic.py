# backend/export_model_logic.py (Versão Definitiva e Funcional)

import joblib
import json
import numpy as np

print("Carregando modelo e artefatos...")

try:
    # Carrega todos os artefatos necessários
    model = joblib.load('decision_tree_model.joblib')
    with open('model_columns.json', 'r') as f:
        feature_names = json.load(f)
    with open('target_map.json', 'r') as f:
        target_map = {int(k): v for k, v in json.load(f).items()}
        class_names = [target_map[i] for i in sorted(target_map.keys())]

    # Acessa a estrutura interna da árvore de decisão
    tree = model.tree_

    # Função recursiva para percorrer a árvore e gerar o código Python
    def generate_python_code(node_id=0, depth=1):
        indent = "    " * depth
        
        # Verifica se é um nó de decisão (tem filhos)
        if tree.children_left[node_id] != tree.children_right[node_id]:
            # Pega o nome da feature e o valor do limiar
            feature_index = tree.feature[node_id]
            feature = feature_names[feature_index]
            threshold = tree.threshold[node_id]
            
            # Gera o 'if'
            code = f"{indent}if input_data.get('{feature}', 0) <= {threshold:.4f}:\n"
            # Chama a função para o filho da esquerda (condição verdadeira)
            code += generate_python_code(tree.children_left[node_id], depth + 1)
            # Gera o 'else'
            code += f"{indent}else:\n"
            # Chama a função para o filho da direita (condição falsa)
            code += generate_python_code(tree.children_right[node_id], depth + 1)
            return code
        else:
            # É uma folha (resultado final), gera o 'return'
            value = tree.value[node_id]
            predicted_class_index = np.argmax(value)
            predicted_class_name = class_names[predicted_class_index]
            return f"{indent}return '{predicted_class_name}'\n"

    print("\n--- LÓGICA DA ÁRVORE DE DECISÃO (Formato Python) ---")
    print("Copie o bloco de código gerado abaixo e cole na função 'predict_diagnosis' do seu dapp.py\n")
    print("# --- INÍCIO DAS REGRAS ---")
    
    # Inicia a geração do código a partir do nó raiz (0)
    final_code = generate_python_code()
    print(final_code)
    
    print("# --- FIM DAS REGRAS ---")

except FileNotFoundError:
    print("ERRO: Artefatos do modelo não encontrados. Execute o train_model.py primeiro.")
except Exception as e:
    print(f"Ocorreu um erro inesperado: {e}")