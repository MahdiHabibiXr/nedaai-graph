from io import BytesIO
import librosa
import numpy as np
import soundfile
from pydub import AudioSegment
import parselmouth


def get_voice_array(audio_bytes: BytesIO) -> tuple[np.ndarray, int]:
    audio_bytes.seek(0)
    try:
        y, sr = soundfile.read(audio_bytes)
    except:
        audio_bytes.seek(0)
        audio_segment = AudioSegment.from_file(audio_bytes)
        wav_io = BytesIO()
        audio_segment.export(wav_io, format="wav")
        wav_io.seek(0)
        y, sr = soundfile.read(wav_io)

    if len(y.shape) > 1:
        y = np.mean(y, axis=1)

    y = y.astype(np.float32)

    # Resample to 16kHz
    if sr != 16000:
        y = librosa.resample(y, orig_sr=sr, target_sr=16000)
        sr = 16000

    return y, sr


def calculate_voice_pitch_parselmouth(audio: np.ndarray, sr: int) -> np.ndarray:
    sound = parselmouth.Sound(audio, sampling_frequency=sr)
    pitch_obj = sound.to_pitch(time_step=0.01)
    pitch_values = pitch_obj.selected_array["frequency"]
    pitch_values[pitch_values == 0] = np.nan
    return pitch_values


def clean_pitch_values(pitch_values: np.ndarray) -> dict:
    valid = pitch_values[~np.isnan(pitch_values)]
    if len(valid) == 0:
        return {}
    q1 = np.percentile(valid, 25)
    q3 = np.percentile(valid, 75)
    mid = valid[(valid >= q1) & (valid <= q3)]
    return {
        "min": np.nanmin(pitch_values),
        "max": np.nanmax(pitch_values),
        "average": np.nanmean(pitch_values),
        "median": np.nanmedian(pitch_values),
        "q1": q1,
        "q3": q3,
        "q_average": (q1 + q3) / 2,
        "robust_average": np.nanmean(mid),
        "robust_median": np.nanmedian(mid),
    }


def get_voice_pitch(audio_bytes: BytesIO) -> dict:
    y, sr = get_voice_array(audio_bytes)
    pitch_values = calculate_voice_pitch_parselmouth(y, sr)
    return clean_pitch_values(pitch_values)


def calculate_pitch_shift(source_pitch: float, target_pitch: float) -> float:
    if source_pitch == 0 or target_pitch == 0:
        return 0.0
    shift = 12 * np.log2(target_pitch / source_pitch)
    return float(np.clip(shift, -12, 12))


def process_pitch_shift(source_audio: BytesIO, target_model_pitch: float) -> float:
    source_pitch_info = get_voice_pitch(source_audio)
    if not source_pitch_info:
        return 0.0

    source_avg_pitch = source_pitch_info["robust_median"]
    pitch_shift = calculate_pitch_shift(source_avg_pitch, target_model_pitch)
    return pitch_shift
