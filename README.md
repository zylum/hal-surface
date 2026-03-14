# hal-surface

Headless Raspberry Pi voice surface runtime designed for Raspberry Pi OS Lite (64-bit).

This project keeps the Pi as a **surface adapter** (audio I/O + optional LED/TFT rendering) and avoids embedding hardware-specific business logic. Behavior is driven by `config.json` so you can switch runtime modes without code changes.

## Features

- Python-only runtime
- Headless operation (no keyboard/monitor required)
- Config-driven mode switching
- Optional Aviary integration behind mode switch
- Optional LED/TFT modules that safely no-op when disabled or missing
- systemd unit + install/update scripts for Git-based maintenance
- Boring, debuggable defaults with clear logging
- No required third-party Python packages for baseline modes

## Repository layout

```text
hal-surface/
  README.md
  requirements.txt
  config.example.json
  main.py
  runtime/
    state.py
    config.py
    audio.py
    tts.py
    aviary_client.py
    transcription.py
    led.py
    tft.py
  modes/
    audio_loopback.py
    tts_only.py
    voice_stub.py
    voice_to_aviary.py
  scripts/
    install_service.sh
    update_and_restart.sh
  systemd/
    hal-surface.service
```

## Setup

1. Install system dependencies on Raspberry Pi:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip espeak ffmpeg alsa-utils
```

2. Clone repo and create virtualenv:

```bash
git clone https://github.com/zylum/hal-surface.git ~/hal-surface
cd ~/hal-surface
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Create config:

```bash
cp config.example.json config.json
# edit config.json values for your environment
```

## Running manually

```bash
source .venv/bin/activate
python main.py --config config.json
```

List ALSA-compatible devices:

```bash
python main.py --list-devices
```

## Modes

### `audio_loopback`
- Record `record_seconds`
- Play recorded audio back immediately

### `tts_only`
- Speak fixed phrase from config (`tts_test_phrase`)

### `voice_stub`
- Record audio
- Use stub transcript provider
- Speak canned response list (`stub_responses`)

### `voice_to_aviary`
- Record audio
- Transcribe via pluggable transcription function (stub by default)
- POST text to Aviary `/v1/ingest/message`
- Speak `audio.speak_text` if present, otherwise `assistant_message`

## States

Core runtime states are hardware-independent and can be rendered by LED/TFT modules later:

- `booting`
- `idle`
- `listening`
- `thinking`
- `speaking`
- `error`

## Config notes

- `run_continuous: false` runs one cycle and exits (useful for test modes).
- `run_continuous: true` runs mode cycles forever with `loop_delay_seconds` pause between cycles.
- `led_enabled` and `tft_enabled` can remain false when hardware is not attached.

## systemd

Install and enable service:

```bash
./scripts/install_service.sh
```

Then inspect logs:

```bash
journalctl -u hal-surface.service -f
```

Update from Git and restart service:

```bash
./scripts/update_and_restart.sh
```
