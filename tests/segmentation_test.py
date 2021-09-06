import librosa
from algos.segmentation import SegmentationParams, find_caugh_segments

BENCHMARK_PARAMS = SegmentationParams(
    envelope_size=0.05,
    detection_threshold=1.5,
    validation_time=0.125,
    validation_threshold=6,
    sample_rate=22050,
    min_segment_length=0.1,
)

BENCHMARK1_OUTPUT_SHAPES = [
    (20944,),
    (26453,),
    (14328,),
    (7714,),
    (15430,),
    (16533,),
    (25356,),
    (15430,)
]

def test_benchmark1_matches_output():
    # load audio from local source file
    audio_amp, _ = librosa.load('samples/preprocessing/benchmark_1/raw.ogg', sr=BENCHMARK_PARAMS.sample_rate)

    segments = find_caugh_segments(
        audio_amp=audio_amp,
        params=BENCHMARK_PARAMS,
    )

    segment_shapes = [s.shape for s in segments]

    assert segment_shapes == BENCHMARK1_OUTPUT_SHAPES
