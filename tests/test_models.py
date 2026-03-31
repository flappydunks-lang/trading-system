import os
import tempfile
import torch
from models.train_lstm import train
from models.predict import ModelPredictor


def test_train_and_predict():
    # train on a very small period for a smoke test
    out = 'models/test_checkpoint.pt'
    train('SPY', period='60d', interval='1d', window=10, epochs=2, out=out)
    assert os.path.exists(out)
    pred = ModelPredictor(checkpoint=out)
    assert hasattr(pred, 'predict')
    print('Model predictor loaded successfully')
