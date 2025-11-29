<h1 align="center">🎙️ telnyx-transcribe 🎙️</h1>
<h3 align="center">Stop manually transcribing calls. Start automating everything.</h3>

<p align="center">
  <strong>
    <em>The ultimate call-and-transcribe toolkit. It dials your list, plays your audio, records everything, and transcribes it all using OpenAI Whisper — automatically.</em>
  </strong>
</p>

<p align="center">
  <!-- Package Info -->
  <a href="https://pypi.org/project/telnyx-transcribe/"><img alt="pypi" src="https://img.shields.io/pypi/v/telnyx-transcribe.svg?style=flat-square&color=4D87E6"></a>
  <a href="#"><img alt="python" src="https://img.shields.io/badge/python-3.10+-4D87E6.svg?style=flat-square"></a>
  &nbsp;&nbsp;•&nbsp;&nbsp;
  <!-- Features -->
  <a href="https://opensource.org/licenses/MIT"><img alt="license" src="https://img.shields.io/badge/License-MIT-F9A825.svg?style=flat-square"></a>
  <a href="#"><img alt="platform" src="https://img.shields.io/badge/platform-macOS_|_Linux_|_Windows-2ED573.svg?style=flat-square"></a>
</p>

<p align="center">
  <img alt="automated" src="https://img.shields.io/badge/🤖_fully_automated-dial_to_transcript-2ED573.svg?style=for-the-badge">
  <img alt="whisper powered" src="https://img.shields.io/badge/🧠_whisper_powered-state_of_art_STT-2ED573.svg?style=for-the-badge">
</p>

<div align="center">

### 🧭 Quick Navigation

[**⚡ Get Started**](#-get-started-in-60-seconds) •
[**✨ Key Features**](#-feature-breakdown-the-secret-sauce) •
[**🎮 Usage & Examples**](#-usage-fire-and-forget) •
[**⚙️ Configuration**](#%EF%B8%8F-configuration) •
[**🆚 Why This Slaps**](#-why-this-slaps-other-methods)

</div>

---

**telnyx-transcribe** is the automated phone assistant your workflow has been missing. Stop manually calling people, recording conversations, and typing out transcripts. This tool does it all — dials your list, plays your audio message, records the responses, and delivers beautiful transcriptions using OpenAI's Whisper, the most accurate speech-to-text model available.

<div align="center">
<table>
<tr>
<td align="center">
<h3>📞</h3>
<b>Bulk Calling</b><br/>
<sub>Dial hundreds in parallel</sub>
</td>
<td align="center">
<h3>🔊</h3>
<b>Auto Playback</b><br/>
<sub>Play your audio message</sub>
</td>
<td align="center">
<h3>🎙️</h3>
<b>Smart Recording</b><br/>
<sub>Capture every response</sub>
</td>
<td align="center">
<h3>🧠</h3>
<b>Whisper Transcription</b><br/>
<sub>State-of-the-art accuracy</sub>
</td>
</tr>
</table>
</div>

How it slaps:
- **You:** `telnyx-transcribe call numbers.txt`
- **Tool:** Dials all numbers, plays audio, records, transcribes.
- **You:** Check `results.tsv` for all transcriptions.
- **Result:** Hours of work done in minutes. Go grab a coffee. ☕

---

## 💥 Why This Slaps Other Methods

Manually managing calls and transcriptions is a vibe-killer. `telnyx-transcribe` makes other methods look ancient.

<table align="center">
<tr>
<td align="center"><b>❌ The Old Way (Pain)</b></td>
<td align="center"><b>✅ The telnyx-transcribe Way (Glory)</b></td>
</tr>
<tr>
<td>
<ol>
  <li>Manually dial each number.</li>
  <li>Play your message, wait for response.</li>
  <li>Fumble with recording software.</li>
  <li>Upload recordings somewhere.</li>
  <li>Manually transcribe or use slow tools.</li>
  <li>Copy results into a spreadsheet.</li>
</ol>
</td>
<td>
<ol>
  <li><code>telnyx-transcribe call numbers.txt</code></li>
  <li>Wait for completion notification.</li>
  <li>Open <code>results.tsv</code>.</li>
  <li>All transcriptions, ready to go.</li>
  <li>Go do something actually important. 🚀</li>
</ol>
</td>
</tr>
</table>

We're not just making calls. We're building a **fully automated pipeline** with concurrent call handling, automatic webhook processing, intelligent retry logic, and state-of-the-art transcription that handles accents, background noise, and multiple languages like a champ.

---

## 🚀 Get Started in 60 Seconds

### Installation

<div align="center">

| Method | Command |
|:------:|:--------|
| **pip** | `pip install telnyx-transcribe` |
| **pipx** | `pipx install telnyx-transcribe` |
| **From source** | `pip install -e .` |

</div>

### Quick Install

```bash
# Using pip (recommended)
pip install telnyx-transcribe

# Or using pipx for isolated environment
pipx install telnyx-transcribe

# Verify installation
telnyx-transcribe --version
```

### From Source

```bash
# Clone the repo
git clone https://github.com/yigitkonur/telnyx-transcribe.git
cd telnyx-transcribe

# Install in development mode
pip install -e ".[dev]"
```

> **✨ Pro Tip:** Use `tt` as a shorthand for `telnyx-transcribe` — both commands work!

---

## 🎮 Usage: Fire and Forget

### 📞 Make Calls & Transcribe

The main workflow — call a list of numbers, play audio, record, and transcribe:

```bash
# Basic usage
telnyx-transcribe call numbers.txt

# With custom output file
telnyx-transcribe call numbers.txt --output campaign_results.tsv

# With more concurrent workers
telnyx-transcribe call numbers.txt --workers 10
```

Your `numbers.txt` should have one phone number per line (E.164 format):
```
+14155551234
+14155551235
+14155551236
```

### 🎧 Standalone Transcription

Already have audio files? Transcribe them directly:

```bash
# Transcribe a single file
telnyx-transcribe transcribe recording.mp3

# Transcribe all files in a directory
telnyx-transcribe transcribe ./recordings/

# With custom output and language
telnyx-transcribe transcribe ./recordings/ --output results.tsv --language en
```

**Supported formats:** MP3, MP4, WAV, M4A, WEBM, OGG, FLAC, MPEG, MPGA

### 🌐 Run Webhook Server Only

Need just the webhook server for incoming Telnyx events?

```bash
# Start server on default port (5000)
telnyx-transcribe server

# Custom port and host
telnyx-transcribe server --port 8080 --host 0.0.0.0
```

### ✅ Validate Configuration

Check if everything is set up correctly:

```bash
telnyx-transcribe validate
```

---

## ✨ Feature Breakdown: The Secret Sauce

<div align="center">

| Feature | What It Does | Why You Care |
| :---: | :--- | :--- |
| **📞 Bulk Calling**<br/>`Concurrent dialing` | Dials multiple numbers in parallel using thread pool | Process hundreds of calls in the time of one |
| **🔊 Auto Playback**<br/>`Custom audio` | Plays your audio file when call is answered | Deliver consistent messages every time |
| **🎙️ Smart Recording**<br/>`Automatic capture` | Starts recording immediately on answer | Never miss a response |
| **🧠 Whisper AI**<br/>`State-of-the-art STT` | Uses OpenAI's Whisper for transcription | Handles accents, noise, multiple languages |
| **🔄 Auto Retry**<br/>`Exponential backoff` | Automatically retries failed API calls | Resilient to network hiccups |
| **📊 TSV Output**<br/>`Ready for analysis` | Structured output with all call details | Import directly into Excel, Sheets, or scripts |
| **🌐 Webhook Server**<br/>`Flask-powered` | Handles Telnyx events in real-time | Seamless integration with Telnyx platform |
| **⚙️ ENV Config**<br/>`Zero hardcoding` | All secrets via environment variables | Secure, 12-factor app compliant |

</div>

---

## ⚙️ Configuration

All configuration is done via environment variables. Create a `.env` file or set them directly.

### Required Variables

```bash
# Telnyx API credentials
TELNYX_API_KEY=your_telnyx_api_key
TELNYX_CONNECTION_ID=your_connection_id
TELNYX_FROM_NUMBER=+1234567890

# OpenAI API key for Whisper
OPENAI_API_KEY=your_openai_api_key

# Audio file to play during calls
AUDIO_URL=https://example.com/your-message.mp3
```

### Optional Variables

```bash
# Server settings
WEBHOOK_HOST=0.0.0.0
WEBHOOK_PORT=5000

# Output settings
OUTPUT_FILE=results.tsv

# Performance tuning
MAX_WORKERS=5
MAX_RETRIES=10
RETRY_DELAY=2.0

# Recording settings
RECORDING_FORMAT=mp3
RECORDING_CHANNELS=single
```

### Quick Setup

```bash
# Copy the example env file
cp .env.example .env

# Edit with your credentials
nano .env  # or your favorite editor

# Validate configuration
telnyx-transcribe validate
```

---

## 🔑 API Key Setup Guides

<details>
<summary><b>📞 Telnyx API — Pay-as-you-go calling</b></summary>

### What you get
- Programmable voice API for making/receiving calls
- Call control, recording, and webhook events
- Enables the `call` command

### Setup Steps
1. Go to [portal.telnyx.com](https://portal.telnyx.com)
2. Sign up and verify your account
3. Create a **Call Control Application**:
   - Navigate to "Call Control" → "Applications"
   - Create new application
   - Set your webhook URL (e.g., `https://your-server.com/webhook`)
4. Get a phone number:
   - Navigate to "Numbers" → "Buy Numbers"
   - Purchase a number with voice capability
   - Assign it to your Call Control application
5. Get your credentials:
   - **API Key**: "API Keys" section
   - **Connection ID**: Your Call Control application's connection ID
   - **From Number**: The number you purchased

### Add to `.env`:
```bash
TELNYX_API_KEY=KEY0123456789...
TELNYX_CONNECTION_ID=1234567890
TELNYX_FROM_NUMBER=+14155551234
```

</details>

<details>
<summary><b>🧠 OpenAI API — Whisper transcription</b></summary>

### What you get
- Access to Whisper speech-to-text model
- State-of-the-art transcription accuracy
- Multi-language support

### Setup Steps
1. Go to [platform.openai.com](https://platform.openai.com)
2. Sign up or log in
3. Navigate to [API Keys](https://platform.openai.com/api-keys)
4. Click "Create new secret key"
5. Copy the key (starts with `sk-`)

### Add to `.env`:
```bash
OPENAI_API_KEY=sk-...
```

### Pricing
- Whisper API: $0.006 per minute of audio
- A 5-minute recording costs ~$0.03

</details>

---

## 🏗️ Project Structure

```
telnyx-transcribe/
├── src/
│   └── telnyx_transcribe/
│       ├── __init__.py          # Package metadata
│       ├── __main__.py          # Entry point for python -m
│       ├── cli.py               # Typer CLI commands
│       ├── app.py               # Flask application factory
│       ├── config.py            # Settings management
│       ├── models.py            # Data models (Call, TranscriptionResult)
│       ├── exceptions.py        # Custom exceptions
│       ├── services/
│       │   ├── call_service.py          # Telnyx call management
│       │   ├── transcription_service.py # OpenAI Whisper integration
│       │   └── output_service.py        # TSV/CSV output handling
│       ├── webhooks/
│       │   └── handlers.py      # Telnyx webhook processing
│       └── utils/
│           ├── logging.py       # Logging configuration
│           └── console.py       # Rich console output
├── tests/                       # Test suite
├── pyproject.toml              # Project configuration
├── requirements.txt            # Dependencies
├── .env.example                # Example environment file
└── README.md                   # This file
```

---

## 🔥 Common Issues & Quick Fixes

<details>
<summary><b>Expand for troubleshooting tips</b></summary>

| Problem | Solution |
| :--- | :--- |
| **`command not found: telnyx-transcribe`** | Restart your terminal or run `pip install --upgrade telnyx-transcribe` |
| **`TELNYX_API_KEY is required`** | Create a `.env` file with your credentials. Run `telnyx-transcribe validate` to check. |
| **Webhook events not received** | Ensure your webhook URL is publicly accessible. Use ngrok for local testing: `ngrok http 5000` |
| **Transcription fails** | Check your `OPENAI_API_KEY` is valid and has credits. Verify audio format is supported. |
| **Calls not connecting** | Verify `TELNYX_FROM_NUMBER` is assigned to your Call Control application. Check number format (E.164). |
| **Recording URL not available** | Telnyx needs time to process recordings. The webhook handles this automatically with retries. |

**Debugging tips:**
```bash
# Run with verbose logging
telnyx-transcribe --verbose call numbers.txt

# Check your configuration
telnyx-transcribe validate

# Test webhook server locally
telnyx-transcribe server --port 5000
# Then use ngrok: ngrok http 5000
```

</details>

---

## 🛠️ For Developers & Tinkerers

### Running from Source

```bash
# Clone and setup
git clone https://github.com/yigitkonur/telnyx-transcribe.git
cd telnyx-transcribe

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy src/

# Linting
ruff check src/
```

### Using as a Library

```python
from telnyx_transcribe import Settings
from telnyx_transcribe.services import CallService, TranscriptionService

# Configure settings
settings = Settings(
    telnyx_api_key="your_key",
    openai_api_key="your_key",
    # ... other settings
)

# Use services directly
call_service = CallService(settings)
call = call_service.initiate_call("+14155551234")

transcription_service = TranscriptionService(settings)
result = transcription_service.transcribe_file("recording.mp3")
print(result.text)
```

---

## 📜 Backstory

This project started from a simple need — automate phone-based surveys and transcribe the responses. The original tweet that sparked it all:

> https://twitter.com/yigitkonur/status/1654827917845860353

What began as a quick script evolved into a full-featured, production-ready tool that handles thousands of calls with ease.

---

## 📄 License

MIT © [Yiğit Konur](https://github.com/yigitkonur)

---

<div align="center">

**Built with 🔥 because manually transcribing phone calls is a soul-crushing waste of time.**

[Report Bug](https://github.com/yigitkonur/telnyx-transcribe/issues) •
[Request Feature](https://github.com/yigitkonur/telnyx-transcribe/issues) •
[Contribute](https://github.com/yigitkonur/telnyx-transcribe/pulls)

</div>
