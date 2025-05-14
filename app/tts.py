import requests
import json
import base64
import os

# url = "https://api.metisai.ir/openai/v1/chat/completions"

# payload = json.dumps({
#   "model": "gpt-4o-audio-preview",
#   "modalities": [
#     "text",
#     "audio"
#   ],
#   "audio": {
#     "voice": "alloy",
#     "format": "wav"
#   },
#   "messages": [
#     {
#       "role": "user",
#       "content": "You are a tts assistant that will say the given text in the given style and given language. Only response with the asked text. Text : هوش مصنوعیِ نِدا اِی آی، تقلید صدای فارسی زبان. 80 هزار کاربر ماهانه در حال استفاده از این نرم افزار هوش مصنوعی هستند. وقت آن است که شما هم محتوای وایرال خود را بسازید! Style : Ads narration Language : Persian"
#     }
#   ],
#   "store": True
# })
# headers = {
#   'Content-Type': 'application/json',
#   'Authorization': 'tpsg-w0E9986Cslw6tkQEDEhbjLCDh2IE2XH'
# }

# response = requests.request("POST", url, headers=headers, data=payload)

# print(response.text)


def generate_tts(
    text, style, language, voice="alloy", format="mp3", file_name="output.mp3"
):
    url = "https://api.metisai.ir/openai/v1/chat/completions"

    payload = json.dumps(
        {
            "model": "gpt-4o-audio-preview",
            "modalities": ["text", "audio"],
            "audio": {"voice": voice, "format": format},
            "messages": [
                {
                    "role": "user",
                    "content": f"You are a TTS assistant that generates speech based on the given text, style, and language. Respond only with the synthesized speech output, without any additional text. Text: {text} Style: {style} Language: {language}",
                }
            ],
            "store": True,
        }
    )

    headers = {
        "Content-Type": "application/json",
        "Authorization": "tpsg-w0E9986Cslw6tkQEDEhbjLCDh2IE2XH",
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    response = response.json()

    file = response["choices"][0]["message"]["audio"]["data"]

    filepath = os.path.join(os.getcwd(), file_name)

    decoded_bytes = base64.b64decode(file)
    with open(filepath, "wb") as f:
        f.write(decoded_bytes)

    return file
