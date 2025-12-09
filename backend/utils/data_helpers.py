# backend/utils/data_helpers.py
import json
import re
import numpy as np
from PIL import Image
import io

def parse_json_from_gemini_response(text):
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    json_str = match.group(1) if match else text
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return None

def get_symptom_list_from_cols(cols):
    symptoms = []
    for col in cols:
        if col not in ["sexo_encoded", "idade", "doenca_alvo", "target_encoded"]:
            symptoms.append(col)
    return symptoms

def convert_numpy_floats(data):
    if isinstance(data, dict):
        return {k: convert_numpy_floats(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_numpy_floats(item) for item in data]
    elif isinstance(data, (np.float32, np.float64)):
        return float(data)
    elif isinstance(data, (np.int32, np.int64)):
        return int(data)
    return data

def preprocess_glaucoma_image(image_bytes, target_size=(224, 224)):
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img_resized = img.resize(target_size)
        img_array = np.array(img_resized)
        img_normalized = img_array / 255.0
        return np.expand_dims(img_normalized, axis=0)
    except Exception as e:
        print(f"Erro ao pré-processar imagem: {e}")
        return None