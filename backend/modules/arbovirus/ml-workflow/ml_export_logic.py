import joblib
import json
import numpy as np

def main():
    print("Carregando modelo e artefatos...")

    try:
        # Nota: Lembre-se que ao rodar esse script no futuro, você precisará 
        # estar no diretório correto onde esses arquivos .joblib e .json foram salvos,
        # ou passar o caminho absoluto (ex: os.path.join(os.path.dirname(__file__), '...'))
        model = joblib.load("decision_tree_model.joblib")
        
        with open("model_columns.json", "r") as f:
            feature_names = json.load(f)
        
        with open("target_map.json", "r") as f:
            target_map = {int(k): v for k, v in json.load(f).items()}
            class_names = [target_map[i] for i in sorted(target_map.keys())]

        tree = model.tree_

        def generate_python_code(node_id=0, depth=1):
            indent = "    " * depth

            if tree.children_left[node_id] != tree.children_right[node_id]:
                feature_index = tree.feature[node_id]
                feature = feature_names[feature_index]
                threshold = tree.threshold[node_id]

                code = f"{indent}if input_data.get('{feature}', 0) <= {threshold:.4f}:\n"
                code += generate_python_code(tree.children_left[node_id], depth + 1)
                code += f"{indent}else:\n"
                code += generate_python_code(tree.children_right[node_id], depth + 1)
                return code
            else:
                value = tree.value[node_id]
                predicted_class_index = np.argmax(value)
                predicted_class_name = class_names[predicted_class_index]
                return f"{indent}return '{predicted_class_name}'\n"

        print("\n--- LÓGICA DA ÁRVORE DE DECISÃO (Formato Python) ---")
        print(
            "Copie o bloco de código gerado abaixo e cole na função 'predict_diagnosis' do seu dapp.py\n"
        )
        print("# --- INÍCIO DAS REGRAS ---")

        final_code = generate_python_code()
        print(final_code)

        print("# --- FIM DAS REGRAS ---")

    except FileNotFoundError:
        print(
            "ERRO: Artefatos do modelo não encontrados. Execute o script de treinamento primeiro."
        )
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    main()