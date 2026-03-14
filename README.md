# hal-surface

Headless Raspberry Pi voice surface runtime designed for Raspberry Pi OS Lite (64-bit).

This project keeps the Pi as a **surface adapter** (audio I/O + optional LED/TFT rendering) and avoids embedding hardware-specific business logic. Behavior is driven by `config.json` so you can switch runtime modes without code changes.

## Features

- Python-only runtime
- Headless operation (no keyboard/monitor required)
- Config-driven mode switching
- Optional Aviary integration behind mode switch
- Optional LED/TFT modules that safely no-op when disabled or missing
- Local admin web panel (`hal-admin`) separated from voice runtime concerns
- systemd units + install/update scripts for Git-based maintenance
- Boring, debuggable defaults with clear logging
- No required third-party Python packages for baseline runtime

## Repository layout

```text
hal-surface/
  README.md
  requirements.txt
  config.example.json
  main.py
  admin/
    app.py
    templates/
      index.html
    services/
      config_store.py
      supervisor.py
      logs.py
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
    restart_service.sh
    run_mode_once.sh
    update_and_restart.sh
  systemd/
    hal-surface.service
    hal-admin.service
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
cp config.example.json config.json
```

3. Install both services:

```bash
./scripts/install_service.sh
```

## Voice runtime

Run manually:

```bash
source .venv/bin/activate
python main.py --config config.json
```

List ALSA-compatible devices:

```bash
python main.py --list-devices
```

## Admin panel (hal-admin)

Run manually:

```bash
source .venv/bin/activate
HAL_SURFACE_REPO=$PWD HAL_SURFACE_CONFIG=$PWD/config.json python admin/app.py --host 0.0.0.0 --port 8787
```

Open from LAN browser: `http://<pi-ip>:8787`

### Admin endpoints

Read endpoints:
- `GET /status`
- `GET /config`
- `GET /logs`
- `GET /devices`

Write endpoints:
- `POST /config`
- `POST /mode`
- `POST /restart`
- `POST /git-pull`
- `POST /test/audio`
- `POST /test/tts`

### Security notes

- Keep admin panel LAN-only.
- Do not expose to public internet.
- Optional simple PIN via env var: `HAL_ADMIN_PIN=1234`.
- No arbitrary shell execution is exposed in the UI.

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

## Logs

```bash
journalctl -u hal-surface.service -f
journalctl -u hal-admin.service -f
```

## Update workflow

```bash
./scripts/update_and_restart.sh
```
