
from typing import NamedTuple
import numpy as np
import librosa

from algos.cleansing import clean_audio_segment, CleansingParams
from algos.prediction import predict, MelSpecParams, ColorSpecParams
from algos.segmentation import find_caugh_segments, SegmentationParams

class WorkUnit(NamedTuple):
    source_file: str
    cleansing_params: CleansingParams
    segmentation_params: SegmentationParams
    mel_spec_params: MelSpecParams
    color_spec_params: ColorSpecParams

def execute(work: WorkUnit):
    # load audio from local source file
    audio_amp, _ = librosa.load(work.source_file, sr=work.segmentation_params.sample_rate)

    # clean up any noise in the audio before processing
    audio_amp = clean_audio_segment(audio_amp, work.cleansing_params)

    # split the raw audio into caugh segments
    segments = find_caugh_segments(audio_amp, work.segmentation_params)
    
    results = []
    for segment in segments:
        # normalize signal
        # TODO: this should be refactorred into the `algos` package
        segment = np.interp(segment, (segment.min(), segment.max()), (-1, +1))

        # run the diagnose prediction algorithm
        # TODO: set the threshold value as a parameter in the workunit
        result = predict(segment, 0.5, work.mel_spec_params, work.color_spec_params)

        # we're done with the segment, append the result to work output
        results.append(result)

    return results

