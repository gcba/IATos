import librosa
import librosa.display
import librosa.effects
import numpy as np
import scipy.signal
from typing import NamedTuple, Tuple

class SegmentationParams(NamedTuple):
    envelope_size: float
    detection_threshold: float
    validation_time: float
    validation_threshold: float
    sample_rate: float
    min_segment_length: int

def _yield_equal_time_slices(audio_samples, time_span: int, sample_rate: int):
    sample_span = time_span * sample_rate
    for offset in np.arange(0, len(audio_samples), sample_span):
        yield (int(offset), int(offset+sample_span))

def _compute_slice_envelope(audio_samples, slice: Tuple[int, int], sample_rate: int):
    since, until = slice
    slice_samples = audio_samples[since:until]
    return dict(
        value = np.power(np.mean(slice_samples), 2),
        timestamp = (since / sample_rate),
    )

def _compute_noise_floor(audio_samples, detection_threshold: float):
    return np.power(np.mean(audio_samples), 2) * detection_threshold

def _refine_event_start_offset(audio_samples, peak_offset, noise_floor: float, step: int):
    cur_index = peak_offset

    while (cur_index - step) > 0:
        since_index = cur_index - step
        since_index = since_index if since_index > 0 else 0
        
        until_index = cur_index + step
        until_index = until_index if until_index < len(audio_samples) else (len(audio_samples)-1)
        
        if audio_samples[cur_index - step] >= audio_samples[cur_index] and np.power(np.mean(audio_samples[since_index:until_index]), 2) < noise_floor:
            return since_index

        cur_index -= step

    return 0

def _refine_event_end_offset(audio_samples, peak_offset, noise_floor: float, step: int):
    cur_index = peak_offset

    while (cur_index + step) < (len(audio_samples)-1):
        since_index = cur_index - step
        since_index = since_index if since_index > 0 else 0
        
        until_index = cur_index + step
        until_index = until_index if until_index < len(audio_samples) else (len(audio_samples)-1)
        
        if audio_samples[cur_index + step] >= audio_samples[cur_index] and np.power(np.mean(audio_samples[since_index:until_index]), 2) < noise_floor:
            return until_index

        cur_index += step
    
    return (len(audio_samples)-1)


def _refine_event_span(audio_samples, peak: dict, noise_floor: float, params: SegmentationParams):
    peak_offset = int(peak['timestamp'] * params.sample_rate)
    step = int(params.envelope_size * params.sample_rate)
    min_index = _refine_event_start_offset(audio_samples, peak_offset, noise_floor, step)
    max_index = _refine_event_end_offset(audio_samples, peak_offset, noise_floor, step)

    return dict(
        peak_offset=peak_offset,
        start_offset=min_index,
        end_offset=max_index
    )

def _event_is_above_validation_threshold(audio_samples, event: dict, params: SegmentationParams)->bool:
    peak_offset = event['peak_offset']
    before_offset = int(peak_offset - (params.validation_time * params.sample_rate))
    if before_offset < 0: return False
    return audio_samples[peak_offset] >= audio_samples[before_offset] + params.validation_threshold

def _event_is_not_signal_boundary(audio_samples, event: dict) -> bool:
    min_index = event['start_offset']
    max_index = event['end_offset']
    return min_index > 0 and max_index < (len(audio_samples)-1)

def _merge_overlapping_events(original_events: list)->list:
    original_events.sort(key=lambda i: i['start_offset'])
    final_events = [original_events[0]] if len(original_events) > 0 else []

    for current in original_events:
        previous = final_events[-1]
        if current['start_offset'] <= previous['end_offset']:
            previous['end_offset'] = max(previous['end_offset'], current['end_offset'])
        else:
            final_events.append(current)

    return final_events

def _event_is_longer_than_min_length(event: dict, params: SegmentationParams)->bool:
    start = event['start_offset']
    end = event['end_offset']
    delta = end - start
    length = delta / params.sample_rate
    return length >= params.min_segment_length

def _get_audio_slice_for_event(audio_samples, event: dict):
    start = event['start_offset']
    end = event['end_offset']
    return audio_samples[start:end]

def find_caugh_segments(
    audio_amp: np.ndarray,
    params: SegmentationParams,
):
    audio_db = librosa.amplitude_to_db(audio_amp, top_db=80.0) + 80.0

    # create a generator of equally time-sized slices from the full audio signal
    slices = _yield_equal_time_slices(audio_db, params.envelope_size, params.sample_rate)

    # map the time slices into audio envelope values
    envelopes = [_compute_slice_envelope(audio_db, slice, params.sample_rate) for slice in slices]
    
    # compute the noise floor of the full audio signal
    noise_floor = _compute_noise_floor(audio_db, params.detection_threshold)

    # find the peaks of the audio by filtering the envelopes that are above the noise floor value 
    candidate_peaks = [envelope for envelope in envelopes if envelope['value'] > noise_floor]
    
    # turn each peak into an 'event' by finding the start / end of the audio segment containing the peak
    candidate_events = [_refine_event_span(audio_db, peak, noise_floor, params) for peak in candidate_peaks]
    
    # filter only the events that are above the validation threshold param
    candidate_events = [event for event in candidate_events if _event_is_above_validation_threshold(audio_db, event, params)]

    # leave out any events that are contiguous to the boundaries of the full audio
    candidate_events = [event for event in candidate_events if _event_is_not_signal_boundary(audio_db, event)]

    # merge any events that overlap with each other
    merged_events = _merge_overlapping_events(candidate_events)

    # leave out any events that are below the minimun time length param
    merged_events = [event for event in merged_events if _event_is_longer_than_min_length(event, params)]

    # return a generator of audio segments (amplitude samples) that match the found event
    return [_get_audio_slice_for_event(audio_amp, event) for event in merged_events]
