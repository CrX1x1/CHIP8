# CHIP8 Python VM

Another CHIP8 virtual machine and basic dev toolchain written in Python with spite of Texas Instruments' arbitrary display library throttling.

## Features
- **Python VM `(core.py, cpu.py)`**: Designed to run on Python-enabled TI calculators seamlessly.
- **ROM Packager `(tool/package.py)`**: Converts compiled `.ch8` binaries to ready-to-run Python scripts via a template.
- **Visual Sprite Editor `(tool/sprite.py)`**: Zero-dependency GUI app to paint sprites of 8x(1-15) with simple drag coloring and gives it in raw bytes for use in Octo.


## Toolchain Guide

### 1. Package a ROM into Python
Take any compiled binary and wrap it in the template
```
python package.py prog.ch8 prog.py
```
### 2. Draw Sprites Visually
Open up the sprite editor to paint assets for your programs.
```
python sprite.py
```
