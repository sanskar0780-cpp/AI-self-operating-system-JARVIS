#  AI Self Operating System

A personal AI assistant that can **see, think, and act** on your computer — combining automation, voice interaction, web control, and file handling into one system.

---

##  What is this?

This project is an attempt to build a **Jarvis-like assistant** that doesn’t just answer questions, but actually **does things for you**.

It can:

* understand commands (text / voice / Telegram)
* analyze your screen
* take actions (click, type, open apps)
* control the browser
* send files from your PC to your phone
* automate workflows

---

## 🎥 Demo

Here’s a quick look at what the system can do in real usage.

###  Telegram Control (PC ↔ Phone)

Control your system remotely and receive results instantly.

* Send commands from your phone
* Get screenshots, files, and responses back

```
You: send file report.pdf
AI: Sending report.pdf...
→ File received on phone ✅
```

---

###  Web Automation

The assistant can browse and interact with websites on its own.

```
You: search youtube latest mrbeast video
AI: Entering web mode...
→ Opens YouTube
→ Searches automatically
→ Plays video
```

---

###  Autonomous Mode

Give a goal, and the AI figures out the steps.

```
You: auto open chrome and search google for weather
AI:
- Opens browser
- Navigates to Google
- Searches "weather"
→ Task completed ✅
```

---

###  File Intelligence

Find and send files using natural language.

```
You: send file resume
AI:
→ Searches Desktop / Downloads / OneDrive
→ Finds best match
→ Sends file
```

---

###  Voice Interaction

Hands-free control using speech.

```
You (voice): take screenshot
AI: Screenshot captured
→ Image sent / saved
```

---

##  Screenshots

<img width="835" height="848" alt="image" src="https://github.com/user-attachments/assets/3235616a-3337-4059-864e-50291fb131d1" />

* Telegram chat with responses
* Browser automation in action
* Screenshot + OCR detection

---

##  Try It Yourself

```bash
python main.py
```

Then choose:

* `1` → mic input
* `2` → text input
* `3` → Telegram control

---

>  Tip: The best way to understand it is to actually try commands like
> `send file`, `search youtube`, or `auto ...`


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

##  Example Commands

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

##  Why I Built This

I wanted something more than a chatbot —
something that can **actually interact with the real world (my computer)**.

This project is a step toward building a **true personal AI system**, not just a conversational one.

---

##  Future Improvements

* Faster vision models (local + optimized)
* Better file search (fuzzy matching)
* Multi-model routing (local + cloud)
* GUI interface
* Task memory and planning improvements

---

##  Contributing

Feel free to fork, experiment, or suggest improvements.

---

## 📄 License

This project is for educational and experimental purposes.
