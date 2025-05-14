import replicate
from dotenv import load_dotenv
import os

load_dotenv(".env")

base_url = os.getenv("VOCAL_REMOVER_WEBHOOK")
task = "vocal-remover"

def create_vocal_reomver_task(
    audio, t_id, duration = 0
):
    
    input = {
        "audio" : audio
    }

    callback_url = f"{base_url}?task={task}&t_id={t_id}&duration={duration}"

    rep = replicate.predictions.create(
        version="b4978c1ac2d9e40f3be3cb51f4266969979850699522cafb45180fb54835e57e",
        input=input,
        webhook=callback_url,
        webhook_events_filter=["completed"],
    )

    return rep.id
