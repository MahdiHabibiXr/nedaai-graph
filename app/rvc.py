import replicate
from dotenv import load_dotenv
import os
import aiohttp

load_dotenv(".env")

base_url = os.getenv("RVC_WEBHOOK")
task = "voice-changer"


def create_rvc_conversion(
    model_url,
    t_id,
    uid,
    id,
    pitch=0,
    voice_name=None,
    rvc_model="CUSTOM",
    duration=0,
    audio=None,
    audio_file=None,
):
    if audio is None:
        audio = audio_file

    input = {
        "protect": 0.5,
        "rvc_model": rvc_model,  # to use custom = CUSTOM
        "index_rate": 0.5,
        "input_audio": audio,
        "pitch_change": pitch,
        "rms_mix_rate": 0.3,
        "filter_radius": 3,
        "custom_rvc_model_download_url": model_url,
        "output_format": "wav",
    }

    callback_url = (
        f"{base_url}?task={task}&t_id={t_id}&duration={duration}&uid={uid}&_id={id}"
    )

    rep = replicate.predictions.create(
        version="d18e2e0a6a6d3af183cc09622cebba8555ec9a9e66983261fc64c8b1572b7dce",
        input=input,
        webhook=callback_url,
        webhook_events_filter=["completed"],
    )

    return rep.id
