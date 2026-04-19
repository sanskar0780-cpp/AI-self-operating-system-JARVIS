from opcode import cmp_op

import edge_tts
import io
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import asyncio
import pygame

pygame.mixer.init()

hindi_model = "hi-IN-MadhurNeural"
english_model = "en-US-AndrewMultilingualNeural"

model = english_model

def voice_model_select(select_voice):
    global model
    if select_voice == 'english' or select_voice == 'eng':
        model = english_model
    elif select_voice == 'hindi' or select_voice == 'hin':
        model = hindi_model

async def tts_speak(text):
    if not text or not str(text).strip():
        return
    text = str(text)[:200]
    try:
        communicate = edge_tts.Communicate(text, model)
        audio_data = b""

        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]

        if not audio_data:
            print("Error : No audio received")
            return
        pygame.mixer.music.load(io.BytesIO(audio_data))
        pygame.mixer.music.play()
    except Exception as e:
        print("[ERROR] TTS:", e)

# async def tts_speak(text):
#     communicate = edge_tts.Communicate(text , model)
#     audio_data = b""
#     print(text)
#
#     async for chunk in communicate.stream():
#         if chunk["type"] == "audio":
#             audio_data += chunk["data"]
#
#     pygame.mixer.music.stop()
#
#     sound_file = io.BytesIO(audio_data)
#     pygame.mixer.music.load(sound_file)
#     pygame.mixer.music.play()
#     while pygame.mixer.music.get_busy():
#         await asyncio.sleep(0.1)


def speak(text):
    print(text)
    try:
        loop = asyncio.get_running_loop()
        asyncio.create_task(tts_speak(text))  # use existing loop
    except RuntimeError:
        asyncio.run(tts_speak(text))  # no loop → safe to run

async def speak_async(text):
    print(text)
    await tts_speak(text)