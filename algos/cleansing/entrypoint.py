from typing import NamedTuple
import numpy as np
import librosa

class CleansingParams(NamedTuple):
    preemphasis_coef: float


def clean_audio_segment(
    audio_amp: np.ndarray,
    params: CleansingParams,
):
    # filter audio amp with preemphasis
    return librosa.effects.preemphasis(audio_amp, coef=params.preemphasis_coef)
