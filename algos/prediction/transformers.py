import librosa
import numpy as np

from PIL import Image
from typing import Optional
from sklearn.base import BaseEstimator, TransformerMixin
from matplotlib.cm import ScalarMappable

__all__ = [
    "Denoising",
    "MelSpectogram",
    "ColoredSpectogram",
]


class BaseTransformer(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    @classmethod
    def read_params(cls, params):
        return cls(**params)


class Denoising(BaseTransformer):
    """Placeholder para la capa "denoising" actualmente en codigo MATLAB"""

    def transform(self, X: np.array, y: Optional[np.array] = None) -> np.array:
        """Codigo aqui"""
        return X


class MelSpectogram(BaseTransformer):
    """Transforma una señal en un espectograma con escala de Mel utilizando librosa
    
    Parameters
    ----------

    Los parametros para instanciar son los que se pasan a `librosa.feature.melspectogram`
    y a `librosa.power_to_db`.

    Returns
    -------

    np.array : Numpy array del espectograma con valores en decibeles.

    """

    def __init__(
        self,
        sr: int,
        n_fft: int,
        hop_length: int,
        n_mels: int,
        fmin: int,
        fmax: int,
        ref: str,
        T: bool,
        as_ratio: bool,
    ):
        self.sr = sr
        self.n_fft = n_fft
        self.hop_length = hop_length
        self.n_mels = n_mels
        self.fmin = fmin
        self.fmax = fmax
        self.ref = ref
        self.T = T
        self.as_ratio = as_ratio

    def transform(self, X: np.array, y: Optional[np.array] = None) -> np.array:
        X_ = self._mel_spec(X)
        if self.T:  # backward compatibility
            X_ = X_.T
        return librosa.power_to_db(X_, ref=getattr(np, self.ref))

    def _mel_spec(self, X: np.array) -> np.array:
        hop = self.hop_length
        if self.as_ratio:  # backward compatibility
            hop = X.size // self.hop_length
        return librosa.feature.melspectrogram(
            y=X, sr=self.sr, hop_length=hop, n_mels=self.n_mels
        )


class ColoredSpectogram(BaseTransformer):
    """Transforma una matriz de valores a una imagen con escala de colores.
    
    Parameters
    ----------
    cmap : str
        Escala de colores accesible desde `matplotlib.cm.get_cmap`.

    Returns
    -------
    PIL.Image : Imagen en modo RGB.

    """

    def __init__(self, cmap: str):
        self.cmap = cmap

    def transform(self, X: np.array, y: Optional[np.array] = None) -> Image:
        X_ = ScalarMappable(cmap=self.cmap).to_rgba(X, bytes=True)
        return Image.fromarray(X_).convert("RGB")
