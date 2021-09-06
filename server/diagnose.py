import connexion
import six
import uuid
import numpy as np
import urllib.request
import logging
from time import time
from urllib.parse import urlparse

from runtime import load_config, execute, WorkUnit

from .persistence import bootstrap_persistence

cleansing_params, segmentation_params, mel_spec_params, colos_spec_params = load_config()
persistence = bootstrap_persistence()

def assert_valid_url_syntax(url):  
    result = urlparse(url)
    assert all([result.scheme, result.netloc])

def download_audio(request_id, audio_url):
    audio_path = f'/tmp/{request_id}'
    urllib.request.urlretrieve(audio_url, audio_path)
    return audio_path

def diagnose_post(body):  # noqa: E501
    logging.info("new diagnose request")

    request_id = uuid.uuid4()
    received_on = time()
    audio_url = body.get('audioUrl')
    audio_path = None
    work_result = None
    
    if audio_url is None:
        return 'Param for audio input (\'audioUrl\') is missing', 400

    try:
        assert_valid_url_syntax(audio_url)
    except Exception as err:
        logging.exception(err)
        return 'URL for audio input is invalid', 400

    logging.debug("downloading audio from url")

    try:
        audio_path = download_audio(request_id, audio_url)
    except Exception as err:
        logging.exception(err)
        return "Error downloading the raw audio input", 400

    work = WorkUnit(
        source_file = audio_path,
        cleansing_params = cleansing_params,
        segmentation_params = segmentation_params,
        mel_spec_params = mel_spec_params,
        color_spec_params = colos_spec_params,
    )

    logging.debug("submiting work unit to runtime")

    try:
        work_result = execute(work)
    except Exception as err:
        logging.exception(err)
        return "Error executing inference process", 500

    logging.debug("dispatching async persistence")
    persistence.track_request_sample(request_id, body, work, work_result, received_on)

    return {
        'requestId': request_id,
        'score': np.max(list(map(lambda r: r['Probability'], work_result))),
        'isPositive': True if np.max(list(map(lambda r: r['Class'], work_result))) >= 1 else False
    }
