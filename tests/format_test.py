import librosa

def test_loads_vorbis_encoding():
    audio_amp, _ = librosa.load('samples/sample-vorbis.ogg')
    assert len(audio_amp) == 65312

def test_loads_opus_encoding():
    audio_amp, _ = librosa.load('samples/sample-opus.ogg')
    assert len(audio_amp) == 68796
