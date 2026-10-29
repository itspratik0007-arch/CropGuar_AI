import os
import io
import logging
from typing import Tuple, List, Dict, Any, Optional
import numpy as np
from PIL import Image

try:
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False
    ort = None

from app.disease_metadata import DISEASE_METADATA, SUPPORTED_CROPS, get_disease_info

logger = logging.getLogger("cropshield.model_service")

# PlantVillage 38 Classes in exact index order matching the fine-tuned MobileNetV2 ONNX model
CLASS_NAMES: List[str] = [
    "Apple Scab",                                        # 0
    "Apple with Black Rot",                              # 1
    "Cedar Apple Rust",                                  # 2
    "Healthy Apple",                                     # 3
    "Healthy Blueberry Plant",                           # 4
    "Cherry with Powdery Mildew",                        # 5
    "Healthy Cherry Plant",                              # 6
    "Corn (Maize) with Cercospora and Gray Leaf Spot",   # 7
    "Corn (Maize) with Common Rust",                     # 8
    "Corn (Maize) with Northern Leaf Blight",            # 9
    "Healthy Corn (Maize) Plant",                        # 10
    "Grape with Black Rot",                              # 11
    "Grape with Esca (Black Measles)",                   # 12
    "Grape with Isariopsis Leaf Spot",                   # 13
    "Healthy Grape Plant",                               # 14
    "Orange with Citrus Greening",                       # 15
    "Peach with Bacterial Spot",                         # 16
    "Healthy Peach Plant",                               # 17
    "Bell Pepper with Bacterial Spot",                   # 18
    "Healthy Bell Pepper Plant",                         # 19
    "Potato with Early Blight",                          # 20
    "Potato with Late Blight",                           # 21
    "Healthy Potato Plant",                              # 22
    "Healthy Raspberry Plant",                           # 23
    "Healthy Soybean Plant",                             # 24
    "Squash with Powdery Mildew",                        # 25
    "Strawberry with Leaf Scorch",                       # 26
    "Healthy Strawberry Plant",                          # 27
    "Tomato with Bacterial Spot",                        # 28
    "Tomato with Early Blight",                          # 29
    "Tomato with Late Blight",                           # 30
    "Tomato with Leaf Mold",                             # 31
    "Tomato with Septoria Leaf Spot",                    # 32
    "Tomato with Spider Mites or Two-spotted Spider Mite",# 33
    "Tomato with Target Spot",                           # 34
    "Tomato Yellow Leaf Curl Virus",                     # 35
    "Tomato Mosaic Virus",                               # 36
    "Healthy Tomato Plant"                               # 37
]

class DiseaseModelService:
    def __init__(self, model_relative_path: str = "models/mobilenet_v2_plant_disease.onnx"):
        self.model_version = "mobilenet_v2_plantvillage_v1"
        self.model_filename = model_relative_path
        self._session = None
        self._input_name = None
        self._is_initialized = False

    def _resolve_model_path(self) -> Optional[str]:
        # Try relative to current working directory and relative to backend directory
        candidates = [
            os.path.join(os.getcwd(), "backend", self.model_filename),
            os.path.join(os.getcwd(), self.model_filename),
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", self.model_filename)),
        ]
        for p in candidates:
            if os.path.isfile(p):
                return p
        return None

    def initialize_model(self) -> bool:
        if self._is_initialized and self._session is not None:
            return True

        if not ONNX_AVAILABLE:
            logger.warning("onnxruntime is not installed. Real inference model cannot be loaded.")
            return False

        path = self._resolve_model_path()
        if not path:
            logger.warning("Model file %s not found in candidate paths.", self.model_filename)
            return False

        try:
            # Configure CPU execution provider with optimal thread settings for standard servers
            sess_options = ort.SessionOptions()
            sess_options.intra_op_num_threads = 2
            sess_options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
            sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

            self._session = ort.InferenceSession(path, sess_options, providers=["CPUExecutionProvider"])
            self._input_name = self._session.get_inputs()[0].name
            self._is_initialized = True
            logger.info("Crop disease classification model initialized successfully from %s", path)
            return True
        except Exception as e:
            logger.error("Failed to load ONNX model: %s", str(e))
            self._session = None
            self._is_initialized = False
            return False

    @property
    def is_configured(self) -> bool:
        if not self._is_initialized:
            self.initialize_model()
        return self._is_initialized and self._session is not None

    def preprocess_image(self, image_bytes: bytes) -> np.ndarray:
        """
        Preprocesses raw image bytes into normalized (1, 3, 224, 224) float32 tensor
        following MobileNetV2 PlantVillage preprocessor configuration:
        - Resize shortest edge to 256
        - Center crop to 224x224
        - Rescale to [0, 1]
        - Normalize with mean=[0.5, 0.5, 0.5] and std=[0.5, 0.5, 0.5] -> range [-1.0, 1.0]
        """
        try:
            image = Image.open(io.BytesIO(image_bytes))
        except Exception as err:
            raise ValueError(f"Uploaded file is not a readable or valid image format: {err}")

        # Ensure RGB format
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Resize shortest edge to 256 keeping aspect ratio
        width, height = image.size
        target_shortest = 256
        if width < height:
            new_width = target_shortest
            new_height = int(height * (target_shortest / width))
        else:
            new_height = target_shortest
            new_width = int(width * (target_shortest / height))

        image = image.resize((new_width, new_height), Image.Resampling.BILINEAR)

        # Center crop 224x224
        left = (new_width - 224) // 2
        top = (new_height - 224) // 2
        right = left + 224
        bottom = top + 224
        image = image.crop((left, top, right, bottom))

        # Convert to numpy float32
        img_arr = np.array(image, dtype=np.float32)

        # Rescale [0, 255] -> [0.0, 1.0]
        img_arr = img_arr / 255.0

        # Normalize with mean=0.5, std=0.5
        mean = np.array([0.5, 0.5, 0.5], dtype=np.float32)
        std = np.array([0.5, 0.5, 0.5], dtype=np.float32)
        img_arr = (img_arr - mean) / std

        # Transpose from (H, W, C) to (C, H, W)
        img_arr = np.transpose(img_arr, (2, 0, 1))

        # Add batch dimension: (1, 3, 224, 224)
        input_tensor = np.expand_dims(img_arr, axis=0).astype(np.float32)
        return input_tensor

    def predict(self, image_bytes: bytes, crop_hint: Optional[str] = None) -> Dict[str, Any]:
        """
        Runs model inference on input image bytes.
        Returns top prediction, confidence score, and top 3 class probabilities.
        """
        if not self.is_configured:
            raise RuntimeError("Disease classification model is not configured or model weights are missing.")

        input_tensor = self.preprocess_image(image_bytes)

        # Execute ONNX session
        outputs = self._session.run(None, {self._input_name: input_tensor})
        logits = outputs[0][0]  # shape: (38,)

        # Compute numerically stable Softmax probabilities
        exp_logits = np.exp(logits - np.max(logits))
        probabilities = exp_logits / np.sum(exp_logits)

        # Top 1 class
        top1_idx = int(np.argmax(probabilities))
        top1_prob = float(probabilities[top1_idx])
        predicted_label = CLASS_NAMES[top1_idx]
        confidence_percent = int(round(top1_prob * 100.0))

        # Top 3 class alternatives
        top_indices = np.argsort(probabilities)[::-1][:3]
        top3_classes = []
        for idx in top_indices:
            top3_classes.append({
                "label": CLASS_NAMES[idx],
                "confidence": int(round(float(probabilities[idx]) * 100.0)),
                "probability": round(float(probabilities[idx]), 4)
            })

        disease_info = get_disease_info(predicted_label)
        is_healthy = bool(disease_info.get("is_healthy", False))

        # Flag crop mismatch if user selected a crop different from model's predicted host crop
        predicted_crop = disease_info.get("crop", "")
        crop_mismatch = False
        if crop_hint and crop_hint.lower() not in ["all", "any", "other", ""]:
            # Check if crop hint roughly matches predicted crop
            if predicted_crop.lower() not in crop_hint.lower() and crop_hint.lower() not in predicted_crop.lower():
                crop_mismatch = True

        return {
            "predicted_label": predicted_label,
            "confidence": confidence_percent,
            "is_healthy": is_healthy,
            "crop": predicted_crop,
            "crop_mismatch": crop_mismatch,
            "selected_crop": crop_hint or predicted_crop,
            "model_version": self.model_version,
            "top_classes": top3_classes,
            "disease_info": disease_info
        }

disease_model_service = DiseaseModelService()
