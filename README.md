# 🧠 AI Self Operating System

A personal AI assistant that can **see, think, and act** on your computer — combining automation, voice interaction, web control, and file handling into one system.

---

## 🚀 What is this?

This project is an attempt to build a **Jarvis-like assistant** that doesn’t just answer questions, but actually **does things for you**.

It can:

* understand commands (text / voice / Telegram)
* analyze your screen
* take actions (click, type, open apps)
* control the browser
* send files from your PC to your phone
* automate workflows

---

## ✨ Features

### 🎙️ Voice + Text Interaction

* Speak or type commands
* Uses speech recognition + TTS for natural interaction

### 🖥️ Screen Awareness

* Takes screenshots
* Uses AI + OCR to understand what's on screen
* Can click buttons or text dynamically

### 🌐 Web Automation

* Built using Playwright
* Can:

  * open websites
  * search YouTube/Google
  * interact with pages

### 📲 Telegram Control

* Control your system remotely from your phone
* Send commands and receive:

  * screenshots
  * files
  * responses

### 📂 File System Intelligence

* “send file report.pdf” → finds and sends it
* Searches:

  * Desktop
  * Downloads
  * Documents
  * OneDrive folders

### 🧠 Autonomous Mode

* Give a goal → AI decides step-by-step actions
* Executes tasks without manual scripting

---

## 🛠️ Tech Stack

* Python
* Playwright (browser automation)
* PyAutoGUI (system control)
* OpenRouter / LLM APIs
* Whisper (speech-to-text)
* Tesseract OCR
* Telethon (Telegram integration)

---

## ⚙️ Setup

### 1. Clone the repo

```bash
git clone https://github.com/your-username/AI-Self-operating-system.git
cd AI-Self-operating-system
```

---

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 3. Install additional tools

* Install **Tesseract OCR**
* Install **FFmpeg**
* Install **Playwright browsers**

```bash
playwright install
```

---

### 4. Create `.env`

Create a `.env` file and add:

```env
superman_api=YOUR_API_KEY
tele_api_id=YOUR_TELEGRAM_API_ID
tele_api_hash=YOUR_TELEGRAM_API_HASH
tele_chat_id=YOUR_CHAT_ID
e_password=YOUR_EMAIL_PASSWORD
```

---

### 5. Run

```bash
python main.py
```

---

## 🧪 Example Commands

* `search youtube latest mrbeast video`
* `send file report.pdf`
* `take screenshot`
* `auto open chrome and search google`
* `send email`
* `stop`

---

## ⚠️ Notes

* This project is experimental and still evolving
* Some actions may fail depending on UI changes
* AI outputs are not always perfectly reliable

---

## 💡 Why I Built This

I wanted something more than a chatbot —
something that can **actually interact with the real world (my computer)**.

This project is a step toward building a **true personal AI system**, not just a conversational one.

---

## 📌 Future Improvements

* Faster vision models (local + optimized)
* Better file search (fuzzy matching)
* Multi-model routing (local + cloud)
* GUI interface
* Task memory and planning improvements

---

## 🤝 Contributing

Feel free to fork, experiment, or suggest improvements.

---

## 📄 License

This project is for educational and experimental purposes.
