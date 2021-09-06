import io
import numpy as np
import librosa
from PIL import Image as PImage
from typing import Dict
from pathlib import Path
from fastai.vision import load_learner, open_image
from .pipelines import setup_pipeline, MelSpecParams, ColorSpecParams


__all__ = [
    "ModelApp",
]


class FastAI:
    """Conector para modelos entrenados con el framework Fast.AI"""

    def __init__(self, file: Path):
        self._model = self._load(file)

    def predict(self, sample: PImage) -> float:
        """Infiere la probabilidad para la clase 1 (Positivo)"""
        sample = self._preprocessing(sample)
        _, _, [_, p] = self._model.predict(sample)
        return p.item()

    def _preprocessing(self, sample: PImage):
        """Convierte la imagen en el input de fastai"""
        # Workaround: Adds JPEG compression noise to image
        with io.BytesIO() as img:
            sample.save(img, format="JPEG")
            return open_image(img)

    def _load(self, file: Path):
        """Carga el modelo utilizando fastai"""
        return load_learner(file.parent, file=file.name)


class ModelApp:
    """Abstraccion para utilizar modelos predictivos"""

    def __init__(self, classifier):
        self._classifier = classifier

    def predict(self, sample: PImage, threshold: float = 0.5) -> Dict[str, float]:
        prob = self._classifier.predict(sample)
        return {
            "Probability": prob,
            "Class": float(prob >= threshold),
        }

    @classmethod
    def load(cls, model: Path, framework: str):
        if framework == "fastai":
            return cls(FastAI(model))

# App del servicio predictivo
model = ModelApp.load(model=Path("models/ml-fai-pv1-dv3.pkl"), framework="fastai")

def predict(signal: np.array, threshold: float, mel_spec: MelSpecParams, color_spec: ColorSpecParams) -> Dict[str, float]:
    """Punto de entrada para la prediccion
    
    Acepta la señal de audio cargada con `librosa.load` y se aplican
    transformaciones para traducir el audio a features. Por ultimo se
    pasa la muestra al modelo para que realize la prediccion junto a
    un THRESHOLD para determinar la clase.

    Returns
    -------
    dict[str, float] : Diccionario con la probabilidad para la clase 1 y la clase
        asignada usando el THRESHOLD.
    """
    pipeline = setup_pipeline(mel_spec, color_spec)
    sample = pipeline.transform(signal)
    return model.predict(sample, threshold)

