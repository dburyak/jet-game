# Jet Runner - simple Pygame demo

Run the game:

python run.py

Headless quick smoke test (no window):

python run.py --headless

Controls:
- Left/Right arrows or A/D to move
- Space to fire
- ESC to quit

This repo includes a minimal headless mode useful for CI smoke tests.






# How to run locally
(Optional) Create and activate a Python venv:
```sh
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:
```sh
pip install -r requirements.txt
```
Run the interactive game:
```
python run.py
```

Controls:
```
Left/Right arrows or A/D: move left/right
Space: fire
ESC: quit
```
Headless smoke test (quick, no window):
```
python run.py --headless --duration 2.0
```
Example output from a 2s headless run I executed: Stopping after 2.01s (max_seconds=2.0) - score=0 health=5
Run the pytest-based test (after installing pytest):
```
python -m pytest tests/test_headless.py -q
```
Note: my environment didn't have pytest installed initially, so the pytest run failed until pytest is installed. The headless manual run works with pygame installed.

```sh
python run.py --no-enemy-bullets --max-scenery-alpha 50
```
