import yaml
from pathlib import Path
from sklearn.pipeline import Pipeline
from typing import NamedTuple
from .transformers import Denoising, MelSpectogram, ColoredSpectogram

class MelSpecParams(NamedTuple):
    sr: int
    n_fft: int
    hop_length: int
    n_mels: int
    fmin: float
    fmax: float
    ref: str
    T: bool
    as_ratio: bool


class ColorSpecParams(NamedTuple):
    cmap: str


def setup_pipeline(mel_spec: MelSpecParams, color_spec: ColorSpecParams):
    # Pipeline que traducen audio a features
    # filename: Path -> feature: PIL.Image
    return Pipeline(
        steps=[
            ("denoising", Denoising()),
            ("mel_spectogram", MelSpectogram.read_params(mel_spec._asdict())),
            ("spec_to_image", ColoredSpectogram.read_params(color_spec._asdict())),
        ]
    )
