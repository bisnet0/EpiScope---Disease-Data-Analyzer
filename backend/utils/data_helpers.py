import json
import re
import numpy as np
from PIL import Image
import io
from typing import Any, List, Dict, Optional, Tuple

def parse_json_from_gemini_response(text: str) -> Optional[Dict[str, Any]]:
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    json_str = match.group(1) if match else text
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return None

def get_symptom_list_from_cols(cols: List[str]) -> List[str]:
    symptoms = []
    for col in cols:
        if col not in ["sexo_encoded", "idade", "doenca_alvo", "target_encoded"]:
            symptoms.append(col)
    return symptoms

def convert_numpy_floats(data: Any) -> Any:
    if isinstance(data, dict):
        return {k: convert_numpy_floats(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_numpy_floats(item) for item in data]
    # 👇 Garante que arrays inteiros do Numpy virem listas nativas
    elif isinstance(data, np.ndarray):
        return data.tolist()
    # 👇 A mágica do Duck Typing: Qualquer escalar do Numpy tem o método .item()
    elif hasattr(data, "item") and callable(getattr(data, "item")):
        return data.item()
    
    return data

def preprocess_glaucoma_image(image_bytes: bytes, target_size: Tuple[int, int] = (224, 224)) -> Any:
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img_resized = img.resize(target_size)
        img_array = np.array(img_resized)
        img_normalized = img_array / 255.0
        return np.expand_dims(img_normalized, axis=0)
    except Exception as e:
        print(f"Erro ao pré-processar imagem: {e}")
        return None