import asyncio
import random
import pyttsx3
import datetime
import time
import speech_recognition as sr
import smtplib
import os
import pyautogui
import pyscreeze
import base64
import pytesseract
import cv2
from dotenv import load_dotenv
from openai import OpenAI
import whisper
import subprocess
import requests
from AI_Assistant.prompts import WEB_PROMPT_STD
from prompts import SYSTEM_PROMPT_STD
from edge_tts_voice import speak, voice_model_select, speak_async
import json
from telethon import TelegramClient, events
from playwright.async_api import async_playwright
import re
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
load_dotenv()

ASSETS_PATH = os.path.join(os.getcwd(), "assets")

speech_to_text_model = whisper.load_model("small")

CHAT_HISTORY=[]

browser_context = None
page = None
playwright_instance = None

INTERRUPT = False

if os.path.exists("chat_history.json"):
    with open("chat_history.json", "r") as f:
        CHAT_HISTORY = json.load(f)

micInput_status = False #Keeping the track if mic is on or not

Telegram_api = int(os.getenv("tele_api_id"))
Telegram_api_hash = os.getenv("tele_api_hash")
Telegram_chat_id = int(os.getenv("tele_chat_id"))

ai_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key = os.getenv("superman_api")
)

# def speak(msg):
#     engine = pyttsx3.init()
#     if not msg:
#         return
#
#     engine.stop()
#     msg = str(msg)
#
#     if len(msg) > 500:
#         msg = msg[:500]
#     print(msg)
#     rate = engine.getProperty('rate')
#     engine.setProperty('rate', rate+10)
#
#     engine.say(msg)
#     engine.runAndWait()

async def speech_to_text(file_path):
    try:
        print("Input file:", file_path)

        wav_path = await asyncio.to_thread(convert_to_wav, file_path)
        print("Converted to:", wav_path)

        result = await asyncio.to_thread(speech_to_text_model.transcribe, wav_path)

        text = result.get("text", "").strip().lower()
        print("Output:", text)

        if os.path.exists(file_path):
            os.remove(file_path)

        if os.path.exists(wav_path):
            os.remove(wav_path)

        return text

    except Exception as e:
        print("STT Error:", e)
        return ""

def convert_to_wav(input_path):
    base = os.path.splitext(input_path)[0]
    output_path = base + ".wav"

    subprocess.run([
        "ffmpeg",
        "-y",                # overwrite
        "-i", input_path,
        "-ar", "16000",
        "-ac", "1",
        output_path
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return output_path

def micInput():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)
    try:
        print("Processing...")
        query = r.recognize_google(audio, language="en-IN")
        print("You:", query)
    except Exception as e:
        print(e)
        speak("say that again please...")
        return ""
    return query

def extract_json(text):
    import json
    import re

    try:
        text = clean_json(text)

        # Extract JSON block
        match = re.search(r'(\[.*\]|\{.*\})', text, re.DOTALL)
        if not match:
            return None

        parsed = json.loads(match.group())

        if isinstance(parsed, dict):
            return [parsed]

        return parsed

    except Exception as e:
        print("JSON parse error:", e)
        return None

def clean_json(text):
    text = text.replace("{{", "{").replace("}}", "}")
    return text

def find_text_onscr(image_path, target_text):
    img = cv2.imread(image_path)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    data = pytesseract.image_to_data(thresh, output_type=pytesseract.Output.DICT)
    candidates = []

    target_text = target_text.lower().strip()

    screen_h, screen_w = img.shape[:2]
    center_x = screen_w //2
    center_y = screen_h //2

    for i, word in enumerate(data["text"]):
        word = word.strip().lower()
        if not word:
            continue
        try:
            conf = int(data["conf"][i])
        except:
            conf = 0

        if conf < 70:
            continue

        if target_text in word or word in target_text:
            x = data["left"][i]
            y = data["top"][i]
            w = data["width"][i]
            h = data["height"][i]

            cx = x + w //2
            cy = y + h //2

            candidates.append((cx, cy))

    # print("OCR words : " , data["text"])
    if not candidates:
        print(f"❌ : Text not found {target_text}")
        return None

    def distance(pos):
        return ((pos[0] - center_x) ** 2+(pos[1] - center_y)**2)**0.5
    return min(candidates, key=distance)

def ask_ai(prompt, used_for):
    try:
        if used_for == 'mail':
            response = ai_client.chat.completions.create(
                model="openai/gpt-oss-120b:free",
                messages=[
                    {"role": "system", "content": "You are an AI which is supposed to write body of the mail, keep it simple.Dont write the subject it has already been provided"},
                    {"role": "user", "content": prompt}
                ] + CHAT_HISTORY[-4:]
            )

        elif used_for == 'filename':
            response = ai_client.chat.completions.create(
                model = "openai/gpt-oss-120b:free",
                messages=[
                    {"role": "system", "content": "NOTE: DO NOT SAY ANYTHING OTHER THAN THE FILENAME, you have just to extract the name of the file and also put the extension, example : if user says 'send file report.pdf' then your output should be 'report.pdf', AND MOST IMPORTANT OF ALL DO NOT STRICTLY SAY ANYTHING ELSE OR IT WILL BREAK THE PROGRAM."},
                    {"role": "user", "content": prompt}
                ]
            )

        else:
            response = ai_client.chat.completions.create(
                model="openai/gpt-oss-120b:free",
                messages=[
                    {"role": "system", "content": "NOTE: DO NOT USE EMOJIS, You are a helpful AI, you have to generate responses like TARS and make sure they stay under 100 words, humor level=70%"},
                ] + CHAT_HISTORY[-6:] + [
                    {"role" : "user", "content": prompt}
                ]
            )
        reply = response.choices[0].message.content

        if not reply:
            return "I could not generate a response."

        return str(reply)

    except Exception as e:
        return f"Error: {str(e)}"

VISION_MODELS = [
    "openrouter/auto",
    "qwen/qwen2.5-vl-7b:free",
    "meta-llama/llama-3.2-11b-vision-instruct:free",
    "google/gemma-3-4b-it:free"
]

def decide_action(objective, screen_desc):

    if screen_desc == 'web':
        using_prompt = WEB_PROMPT_STD
    else:
        using_prompt = SYSTEM_PROMPT_STD

    for model_name in VISION_MODELS:
        try:
            response = ai_client.chat.completions.create(
                model = model_name,
                messages=[
                    {
                    "role" : "system",
                    "content": using_prompt
                }
                ] + CHAT_HISTORY[-4:] + [
                    {
                        "role": "user",
                        "content": f"""
                                        Main objective : {objective} 
                                        screen : {screen_desc}
                                    """
                    }
                ]
            )

            return response.choices[0].message.content


        except Exception as e:
            print(f"{model_name} failed:", e)
            continue
    return "[]"

async def web_execute_action(action):
    global INTERRUPT, page

    if page is None:
        return {"status": "fail", "error": "Browser not initialized"}

    actions = extract_json(clean_json(action))

    if not actions:
        return {"status": "fail", "error": "Invalid AI output"}

    for act in actions:
        if INTERRUPT:
            INTERRUPT = False
            return {"status": "fail", "error": "Interrupted"}

        op = act.get("operation")

        try:
            if op == "goto":
                await page.goto(act["url"])

            elif op == "click_css":
                await page.click(act["selector"])

            elif op == "type_css":
                await page.fill(act["selector"], act["content"])

            elif op == "press":
                await page.press(act["selector"], act["key"])

            elif op == "wait_for":
                await page.wait_for_selector(act["selector"], timeout=10000)

            elif op == "done":
                return {"status": "done", "summary": act.get("summary")}

        except Exception as e:
            print("Playwright error:", e)
            return {"status": "fail", "error": str(e)}

    return {"status": "fail", "error": "No completion"}

async def execute_action(action):

        global INTERRUPT
        action = clean_json(action)
        actions = extract_json(action)

        if not actions:
            print("❌ Invalid AI output:\n", action)
            return False

        for act in actions:

            if INTERRUPT:
                print("🛑Interrupted!")
                INTERRUPT = False
                return {"status":"fail", "error":"Interrupted"}

            await asyncio.sleep(0.6)
            op = act.get("operation")

            if not op:
                return {"status": "fail", "error": "Missing operation key"}
            try:
                if op == "click":
                    try:
                        x = float(act.get("x"))
                        y = float(act.get("y"))

                        if not (0 <= x <= 1 and 0 <= y <= 1):
                            return {"status": "fail", "error": "Invalid coordinates"}

                        screen_w, screen_h = pyautogui.size()
                        pyautogui.moveTo(x * screen_w, y * screen_h, duration=random.uniform(0.3,1))
                        pyautogui.click()

                    except Exception as e:
                        print("❌ Click error:", e)

                elif op == "write":
                    pyautogui.write(act["content"])

                elif op == "press":
                    keys = act.get("keys", [])

                    if isinstance(keys, list):
                        if len(keys) > 1:
                            pyautogui.hotkey(*keys)
                        else:
                            pyautogui.press(keys[0])
                    else:
                        pyautogui.press(keys)

                elif op == "done":
                    print("done :", act["summary"])
                    return {
                        "status": "done",
                        "summary": act.get("summary", "Task completed")
                    }

                elif op == "click_text":
                    text = act.get("text")

                    if isinstance(text, list):
                        text = " ".join(text)

                    if not isinstance(text, str):
                        return {"status": "fail", "error": "Invalid text format"}

                    screenshot_capture()
                    await asyncio.sleep(1)
                    pos = find_text_onscr("screen_img.png", text)

                    if pos:
                        pyautogui.click(pos[0], pos[1])
                    else:
                        print(f"X : Failed cuz of {text} not found")
                        return {"status": "fail", "error": f"Text '{text}' not found"}

                elif op == "click_image":
                    image = act.get("image")
                    pos = find_image_center(image)

                    if pos:
                        pyautogui.click(pos)
                    else:
                        return {"status": "fail", "error": f"Image '{image}' not found"}

                elif op == "wait":
                    seconds = act.get("seconds", 1)
                    print(f"⏳ Waiting {seconds} seconds")
                    await asyncio.sleep(seconds)

            except Exception as e:
                print("❌ : Error cuz of " , str(e))
                return {"status": "fail" , "error": str(e)}
        print("Continue")
        return {"status": "continue"}

async def web_autonomous_mode(objective):
    global INTERRUPT
    INTERRUPT = False

    while True:
        if INTERRUPT:
            INTERRUPT = False
            print("Interrupted")
            return {"status" : "fail", "error": "Interrupted"}

        action = decide_action(objective, 'web')
        print("ACTION : \n", action)

        await asyncio.sleep(0.5)
        result = await web_execute_action(action)

        if result["status"] == "fail":
            return result
        if result["status"] == "done":
            return result

async def init_browser():
    global browser_context, page, playwright_instance

    if browser_context is not None:
        return  # already initialized

    profile_path = os.path.join(os.getcwd(), "browser_data")

    playwright_instance = await async_playwright().start()

    browser_context = await playwright_instance.chromium.launch_persistent_context(
        user_data_dir=profile_path,
        executable_path=r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
        headless=False
    )

    page = await browser_context.new_page()

async def close_browser():
    global browser_context, playwright_instance

    if browser_context:
        await browser_context.close()
        browser_context = None

    if playwright_instance:
        await playwright_instance.stop()
        playwright_instance = None

async def autonomous_mode(objective):
    global INTERRUPT
    INTERRUPT = False

    while True:
        if INTERRUPT:
            print("🛑 Interrupted")
            INTERRUPT = False
            return {"status": "fail", "error": "Interrupted"}

        screen = await asyncio.to_thread(screenshot_capture)
        screen_desc = await asyncio.to_thread(vision_ai, screen)

        print("\n SCREEN:\n", screen_desc)

        action = decide_action(objective, screen_desc)
        print("\n ACTION:\n", action)
        await asyncio.sleep(0.5)
        result = await execute_action(action)

        if result["status"] == "fail":
            return result

        if result["status"] == "done":
            return result

def vision_ai(image_path):
    base64_image = encode_image(image_path)

    # response = requests.post(
    #     "http://localhost:11434/api/generate",
    #     json={
    #         "model": "llava:7b",
    #         "images": [base64_image],
    #         "prompt": "Describe this screen, describe which apps are open and what things are open, under 400 words",
    #         "stream": False
    #     }
    # )
    # return response.json()["response"]


    #////////////////////////////////////////////////////////////////////#

    for model_name in VISION_MODELS:
        try:
            response = ai_client.chat.completions.create(
                model=model_name,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe this screen, describe which apps are open and what things are open, under 400 words"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }]
            )
            return response.choices[0].message.content

        except Exception as e:
            print(f"{model_name} failed:", e)

    return "All vision models failed"

def find_image_center(image_name):
    image_path = os.path.join(ASSETS_PATH, image_name)

    if not os.path.exists(image_path):
        print(f"❌ Image file missing: {image_path}")
        return None

    try:
        location = pyautogui.locateCenterOnScreen(image_path, confidence=0.8, grayscale=True)
        return location
    except Exception as e:
        print("Image detection Error ", e)
        return None

def send_mail():

    global subject_of_mail, body_of_mail
    speak("Do you want to generate the mail or send it yourself?")


    if micInput_status:

        generate_or_write = micInput().lower()
        if 'generate' in generate_or_write or 'generation' in generate_or_write:

                speak("Enter the subject : ")
                subject_of_mail = micInput()

                speak("What do you want to generate?")
                prompt = micInput()
                body_of_mail = ask_ai(prompt, 'mail')
        elif 'myself' in generate_or_write or 'own' in generate_or_write:
            speak("Enter the subject : ")
            subject_of_mail = micInput()

            speak("Body of the Mail : ")
            body_of_mail = micInput()

    elif not micInput_status:
        generate_or_write = input()
        if 'generate' in generate_or_write or 'generation' in generate_or_write:
            speak("Enter the subject : ")
            subject_of_mail = input()

            speak("What do you want to generate?")
            prompt = input()
            body_of_mail = ask_ai(prompt, 'mail')
        elif 'myself' in generate_or_write or 'own' in generate_or_write:
            speak("Enter the subject : ")
            subject_of_mail = input()

            speak("Body of the Mail : ")
            body_of_mail = input()


    password = os.getenv("e_password")
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login("burrito0770@gmail.com", password)

    message = f"Subject: {subject_of_mail}\n\n {body_of_mail}"
    server.sendmail("burrito0770@gmail.com", "sanskar0780@gmail.com", message.encode('utf-8'))
    speak("Email sent to the user")
    server.close()

def send_mail_tele(subject, body):
    password = os.getenv("e_password")
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login("burrito0770@gmail.com", password)

    message = f"Subject: {subject} \n\n {body}"
    server.sendmail("burrito0770@gmail.com", "sanskar0780@gmail.com", message.encode('utf-8'))
    print("email sent to the user")
    server.close()

def greeting():
    hour = datetime.datetime.now().hour
    if 6 <= hour < 12:
        speak("good morning boss!")
    elif 12 <= hour < 16:
        speak("Good Afternoon boss!")
    elif 16 <= hour < 22:
        speak("Good Evening boss! ")
    else:
        speak("Working overtime huh?")

async def inputmtd_mic():
    global CHAT_HISTORY
    while True:
        query = micInput().lower()

        if 'exit' in query or 'change input' in query:
            break

        elif 'email' in query or 'mail' in query:
            send_mail()
            continue


        elif 'search' in query or 'google' in query or 'youtube' in query:
            await init_browser()
            speak("Entering web mode")
            await web_autonomous_mode(query)
            continue

        elif 'auto' in query or 'do it yourself' in query:
            speak("Enter Auto pilot")
            await autonomous_mode(query)
            continue

        elif 'change language' in query:
            speak("Which model you want english or hindi")
            select_voice = input().lower()
            voice_model_select(select_voice)
            continue

        CHAT_HISTORY.append({
            "role": "user",
            "content": query
        })

        reply = ask_ai(query, 'talk')
        print("AI: ", end="")
        await speak_async(reply)
        CHAT_HISTORY.append({
            "role": "assistant",
            "content" : reply
        })
        CHAT_HISTORY = CHAT_HISTORY[-20:]
        with open("chat_history.json", "w") as f:
            json.dump(CHAT_HISTORY, f)

async def inputmtd_text():
    global CHAT_HISTORY
    while True:
        query = input("You: ")

        if 'exit' in query.lower():
            break

        elif 'email' in query or 'mail' in query:
            send_mail()
            continue

        elif 'search' in query or 'google' in query or 'youtube' in query:
            await init_browser()
            speak("Entering web mode")
            await web_autonomous_mode(query)
            continue

        elif 'auto' in query or 'do it yourself' in query:
            speak("Enter Auto pilot")
            await autonomous_mode(query)
            continue

        elif 'change language' in query:
            speak("Which model you want english or hindi")
            select_voice = input().lower()
            voice_model_select(select_voice)
            continue

        CHAT_HISTORY.append({
            "role": "user",
            "content": query
        })

        reply = ask_ai(query, 'talk')
        print("AI: ",end="")
        await speak_async(reply)

        CHAT_HISTORY.append({
            "role": "assistant",
            "content" : reply
        })
        CHAT_HISTORY = CHAT_HISTORY[-20:]
        with open("chat_history.json", "w") as f:
            json.dump(CHAT_HISTORY, f)

def screenshot_capture():
    path = os.path.join(os.getcwd(), "screen_img.png")
    screenshot = pyautogui.screenshot()
    screenshot.save(path)
    return path

def encode_image(path):
    with open(path, "rb") as img:
        return base64.b64encode(img.read()).decode("utf-8")

def find_send_file(filename):
    filename = filename.lower()
    base_paths = [
        os.path.join(os.path.expanduser("~"), "Desktop"),
        os.path.join(os.path.expanduser("~"), "Downloads"),
        os.path.join(os.path.expanduser("~"), "Documents"),

        #ONEDRIVE locations too cuh
        os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop"),
        os.path.join(os.path.expanduser("~"), "OneDrive", "Documents"),
    ]

    for base in base_paths:
        for root, dirs, files in os.walk(base):
            for file in files:
                if filename in file.lower():
                    return os.path.join(root, file)
    return None

async def handle_command(msg, event):
    if "auto" in msg:
        result = await autonomous_mode(msg)
        return result

    elif "send file" in msg:
        filename = ask_ai(msg,"filename")
        print("filename:", repr(filename))
        return {"status" : "send_file", "file" : filename}

    elif "screenshot" in msg or "screenshot?" in msg:
        path = screenshot_capture()
        return {"status" : "done", "file" : path}

    elif "exit" in msg or "quit" in msg:
        return {"status" : "exit"}

    elif "email" in msg:
        return {"status" : "email", "content": msg}

    return {"status" : "fail", "error" : "Unknown commmand"}

async def handler_common(text, event):

    text = text.lower().strip()

    if is_command(text):
        result = await handle_command(text, event)

        if not isinstance(result, dict):
            await event.reply(f"⚠️ Invalid result: {result}")
            return

        if result["status"] == "fail":
            path = screenshot_capture()
            await event.reply(f"❌ Failed: {result['error']}", file=open(path, "rb"))
            return {"result": "fail", "file": path}

        elif result["status"] == "done":
            if "file" in result:
                await event.reply(file=open(result["file"], "rb"))
            else:
                path = screenshot_capture()
                await event.reply(f"✅ Done: {result['summary']}", file=open(path, "rb"))

        elif result["status"] == "send_file":
            if "file" in result:
                path = find_send_file(result["file"])

                if path:
                    await event.reply("Sending file...")
                    await tg_client.send_file(Telegram_chat_id, path)
                else:
                    await event.reply(f"❌ File not found: {result["file"]}")


        elif result["status"] == "exit":
            path = screenshot_capture()
            await event.reply("Shutting down...", file=open(path, "rb"))
            tg_client.disconnect()

        elif result["status"] == "email":
            await event.reply("Sending Email...")

            try:
                body = ask_ai(text, "mail")
                await asyncio.to_thread(send_mail_tele, "Auto Subject", body)

                path = screenshot_capture()
                with open(path, "rb") as f:
                    await event.reply("Email sent", file = f)
            except Exception as e:
                await event.reply(f"Error : {str(e)}")


    else:
        global CHAT_HISTORY
        CHAT_HISTORY.append({
            "role": "user",
            "content": text
        })
        reply = ask_ai(text, 'talk')
        await event.reply(reply)
        await speak_async(reply)

        CHAT_HISTORY.append({
            "role": "assistant",
            "content": reply
        })
        with open("chat_history.json", "w") as f:
            json.dump(CHAT_HISTORY[-20:], f)

    return

tg_client = TelegramClient("jarvis_session", Telegram_api, Telegram_api_hash)
@tg_client.on(events.NewMessage)
async def handler(event):

    if event.chat_id != Telegram_chat_id:
        return
    global INTERRUPT

    if event.message.voice:
        file_path = await event.download_media()
        text = speech_to_text(file_path).lower()
    else:
        text = event.raw_text

    text_clean = text.strip().lower()
    if text_clean in ["exit", "quit"]:
        path = screenshot_capture()
        await event.reply("Shutting Down...", file=open(path, "rb"))
        await close_browser()
        tg_client.disconnect()
        return

    # CHECKING FOR ANY INTERRUPTS (BEST THING EVER FR)
    elif any(word in text for word in ["stop", "abort", "cancel"]):
        INTERRUPT = True

        # stop speech if running
        try:
            import pygame
            pygame.mixer.music.stop()
        except:
            pass

        await event.reply("🛑 Interrupt received. Stopping all tasks.")
        return

    # THIS IS VOICEEEEEEEEEEEEE ARHHAHAHAEEAEAEAEAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA

    if event.message.voice:
        file_path = await event.download_media()
        print("Voice msg downloaded")

        text = speech_to_text(file_path)
        await event.reply(f"You : {text}")

        if "screenshot" in text:
            path = screenshot_capture()
            with open(path, "rb") as f:
                await event.reply("📸 Screenshot", file=f)
            return

        await handler_common(text, event)
        return

    msg = event.raw_text.lower()
    print("->", msg)

    if "screenshot" in msg:
        path = screenshot_capture()
        with open(path, "rb") as f:
            await event.reply("📸 Screenshot", file=f)
        return

    #TEXXT COMMANFS AIEEHESHEH HERE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    await handler_common(msg, event)


def is_command(msg):
    msg = msg.strip().lower()
    return any(cmd in msg for cmd in ["auto", "screenshot", "open", "click", "quit", "stop", "email", "send file"])

if __name__ == "__main__":
    greeting()
    try:
        while True:
            choice = input("Enter 1 for mic input or 2 for text input or 3 for telegram control or 'q' to quit : ")
            if choice == '1':
                micInput_status = True
                asyncio.run(inputmtd_mic())
                break

            elif choice == '2':
                micInput_status = False
                asyncio.run(inputmtd_text())
                break

            elif choice == '3':
                print("📡 Starting Telegram control...")
                tg_client.start()
                tg_client.run_until_disconnected()
                break

            elif choice == 'q':
                break
    finally:
        asyncio.run(close_browser())
