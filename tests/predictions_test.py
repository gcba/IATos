import librosa
from algos.prediction import predict


def test_prediction_nsample():
    sample, _ = librosa.load("samples/sample-negative.ogg", sr=22050)
    result = predict(sample, 0.5)
    assert result["Probability"] < 0.1
    assert result["Class"] == 0


def test_prediction_psample():
    sample, _ = librosa.load("samples/sample-positive.ogg", sr=22050)
    result = predict(sample, 0.5)
    assert result["Probability"] > 0.9
    assert result["Class"] == 1
