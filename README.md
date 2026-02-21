bulk outbound calls with automatic transcription. places calls via Telnyx, plays a prompt, records the response, downloads the audio, and runs it through OpenAI Whisper. results stream to a TSV file as they complete.

```bash
telnyx-transcribe call numbers.txt
```

also works as a standalone transcriber for local audio files — no Telnyx needed.

[![python](https://img.shields.io/badge/python-3.10+-93450a.svg?style=flat-square)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-93450a.svg?style=flat-square)](https://flask.palletsprojects.com/)
[![license](https://img.shields.io/badge/license-MIT-grey.svg?style=flat-square)](https://opensource.org/licenses/MIT)

---

## how it works

```
numbers.txt
  → telnyx.Call.create() per number (thread pool, concurrent)
  → call answered → playback_start(audio_url) + record_start()
  → Telnyx fires webhook: call.recording.saved
  → download recording → OpenAI Whisper transcription
  → append result to TSV
```

a Flask server handles the Telnyx webhook lifecycle. the whole pipeline is event-driven — calls fan out, webhooks come back, transcriptions stream to disk. nothing is batched at the end.

## what it does

- **concurrent outbound calls** — reads E.164 numbers from a file, fans out via thread pool
- **automatic playback + recording** — plays your audio prompt on answer, starts recording simultaneously
- **webhook-driven pipeline** — Flask server reacts to Telnyx events (`call.answered`, `call.hangup`, `call.recording.saved`)
- **Whisper transcription** — downloads recording, sends to `whisper-1`, writes result immediately
- **standalone file transcription** — skip Telnyx entirely, transcribe local files or directories
- **exponential backoff** — retries transcription up to 10 times with `delay * 2^attempt`
- **thread-safe incremental output** — results written as they complete, not held in memory
- **multi-format output** — TSV (default), CSV, or newline-delimited JSON

## install

```bash
git clone https://github.com/yigitkonur/telnyx-llm-call.git
cd telnyx-llm-call
pip install .
```

this registers two CLI commands: `telnyx-transcribe` and `tt` (short alias).

### configure

copy the example and fill it in:

```bash
cp .env.example .env
```

```env
# required for call mode
TELNYX_API_KEY=your_telnyx_api_key
TELNYX_CONNECTION_ID=your_connection_id
TELNYX_FROM_NUMBER=+1234567890
AUDIO_URL=https://example.com/prompt.mp3

# required always
OPENAI_API_KEY=your_openai_api_key

# optional
WEBHOOK_HOST=0.0.0.0
WEBHOOK_PORT=5000
OUTPUT_FILE=results.tsv
MAX_WORKERS=5
RECORDING_FORMAT=mp3
RECORDING_CHANNELS=single
MAX_RETRIES=10
RETRY_DELAY=2.0
```

## usage

### place calls and transcribe

```bash
telnyx-transcribe call numbers.txt
telnyx-transcribe call numbers.txt --output calls.tsv --workers 10
```

`numbers.txt` is one E.164 phone number per line.

### transcribe local files

```bash
telnyx-transcribe transcribe recording.mp3
telnyx-transcribe transcribe ./recordings/ --workers 3 --language en
```

supports `.mp3`, `.wav`, `.m4a`, `.ogg`, `.flac`, `.webm`, `.mp4`, `.mpeg`, `.mpga`.

### run webhook server standalone

```bash
telnyx-transcribe server --port 5000 --host 0.0.0.0 --output results.tsv
```

### validate config

```bash
telnyx-transcribe validate
```

prints a checklist of which required env vars are set.

## CLI reference

### `call <numbers_file>`

| flag | default | description |
|:---|:---|:---|
| `--output / -o` | `results.tsv` | output file path |
| `--workers / -w` | `5` | concurrent calls |
| `--no-server` | — | skip starting the webhook server |

### `transcribe <source>`

| flag | default | description |
|:---|:---|:---|
| `--output / -o` | `transcriptions.tsv` | output file path |
| `--workers / -w` | `3` | concurrent transcriptions |
| `--language / -l` | auto-detect | BCP-47 language hint for Whisper (e.g. `en`, `es`, `tr`) |

### `server`

| flag | default | description |
|:---|:---|:---|
| `--port / -p` | `5000` | webhook server port |
| `--host / -h` | `0.0.0.0` | webhook server host |
| `--output / -o` | `results.tsv` | output file path |

## webhook endpoints

| method | path | description |
|:---|:---|:---|
| `GET` | `/health` | health check, returns active call count |
| `POST` | `/webhook` | main Telnyx event receiver |
| `POST` | `/webhook/call-recording-saved` | dedicated recording-saved handler |
| `GET` | `/webhook/health` | blueprint health check |

the webhook server must be publicly reachable for Telnyx to deliver events. use ngrok, a reverse proxy, or deploy to a server with a public IP.

## project structure

```
src/telnyx_transcribe/
  __init__.py              — package root
  __main__.py              — python -m support
  app.py                   — Flask app factory + orchestrator
  cli.py                   — Typer CLI (call, transcribe, server, validate)
  config.py                — settings dataclass, env loading, validation
  exceptions.py            — custom exception hierarchy
  models.py                — Call, TranscriptionResult, CallTranscriptionResult
  services/
    call_service.py        — Telnyx call lifecycle + thread pool fan-out
    transcription_service.py — Whisper interface, URL download, directory batch
    output_service.py      — thread-safe TSV/CSV/JSON writer
  utils/
    console.py             — Rich terminal UI
    logging.py             — logging config
  webhooks/
    handlers.py            — webhook dispatch + Flask blueprint
```

## configuration reference

| variable | required | default | description |
|:---|:---|:---|:---|
| `TELNYX_API_KEY` | call mode | — | Telnyx API key |
| `TELNYX_CONNECTION_ID` | call mode | — | Telnyx connection/SIP trunk ID |
| `TELNYX_FROM_NUMBER` | call mode | — | caller ID (E.164) |
| `OPENAI_API_KEY` | always | — | OpenAI API key for Whisper |
| `AUDIO_URL` | call mode | — | URL of audio prompt played on answer |
| `WEBHOOK_HOST` | no | `0.0.0.0` | Flask server host |
| `WEBHOOK_PORT` | no | `5000` | Flask server port |
| `OUTPUT_FILE` | no | `results.tsv` | output file path |
| `MAX_WORKERS` | no | `5` | max concurrent calls/transcriptions |
| `RECORDING_FORMAT` | no | `mp3` | `mp3` or `wav` |
| `RECORDING_CHANNELS` | no | `single` | `single` or `dual` |
| `MAX_RETRIES` | no | `10` | max Whisper retry attempts |
| `RETRY_DELAY` | no | `2.0` | base delay (seconds) for exponential backoff |

## license

MIT
