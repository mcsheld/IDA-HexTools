**Languages:** [🇬🇧](./README.md) | [🇷🇺](./README_RU.md)

# HexTools for IDA Pro
**An IDA Pro plugin for copying and patching bytes as HEX directly from the disassembly window.**

A fork of [HexCopy by OALabs](https://github.com/OALabs/hexcopy-ida), extended with **Paste Hex** functionality — patch bytes at the cursor position by pasting a hex string from the clipboard or entering it manually.

## 📖 About the Project

![How to Use](https://github.com/mcsheld/IDA-HexTools/blob/main/Images/HexTools.gif?raw=true)

HexTools adds two complementary actions to IDA Pro's disassembly view: copy selected bytes as a hex string, and patch bytes at the current address by pasting hex data back. If the clipboard doesn't contain valid hex data, an input dialog appears automatically.

### Key Features

| Function | Hotkey | Description |
|---|---|---|
| 📋 **Copy Hex** | `Ctrl+H` | Copy selected bytes to clipboard as uppercase hex string |
| 📥 **Paste Hex** | `Ctrl+Shift+H` | Patch bytes at cursor from clipboard or manual input |
| 🖱️ **Context menu** | Right-click → Hex Tools | Both actions available in disassembly popup menu |
| 🔍 **Smart fallback** | — | If nothing selected, copies the item under cursor |
| 📝 **Input dialog** | — | Opens automatically if clipboard has no valid hex data |
| 🔄 **Auto jump** | — | Cursor moves past patched bytes after paste (configurable) |
| 🪟 **Output log** | — | Copy/paste details printed to IDA Output window (configurable) |

### Supported Hex Formats for Paste

The parser accepts a wide range of common hex formats:

```
A1 B2 C3 D4          space-separated
A1:B2:C3:D4          colon-separated
A1-B2-C3-D4          dash-separated
A1B2C3D4             plain hex string
0xA1 0xB2 0xC3       0x-prefixed
0xA1,0xB2,0xC3       0x-prefixed comma-separated
```

## 🚀 Quick Start

### System Requirements

- **IDA Pro** 9.x or higher
- **Python** 3.x
- **PySide6** — bundled with IDA Pro 9.x

### Installation

1. Download [`HexTools.py`](./HexTools.py)
2. Copy it into your IDA plugins directory:

```
# Windows
%APPDATA%\Hex-Rays\IDA Pro\plugins\

# Linux / macOS
~/.idapro/plugins/
```

3. Restart IDA Pro — the plugin loads automatically

## ⚙️ Configuration

At the top of `HexTools.py` there are options you can adjust:

```python
# Move cursor to the byte after the last patched byte
JUMP_AFTER_PASTE = True

# Print copy/paste details to the IDA Output window
OUTPUT_COPY_INFO = True
OUTPUT_PAST_INFO = True
```

## 🗂️ Usage

**Copy Hex**
1. Select bytes in the disassembly window
2. Press `Ctrl+H` or right-click → **Hex Tools → Copy Hex**
3. The hex string is copied to your clipboard and printed to the Output window

**Paste Hex**
1. Copy a hex string to your clipboard (from any source)
2. Place the cursor at the target address in the disassembly window
3. Press `Ctrl+Shift+H` or right-click → **Hex Tools → Paste Hex**
4. If the clipboard contains valid hex — bytes are patched immediately
5. If not — an input dialog appears for manual entry

## ❗ Compatibility

| Component | Version |
|---|---|
| IDA Pro | 9.x+ |
| Python | 3.x |
| PySide6 | bundled with IDA 9.x |

> Earlier versions of IDA Pro (7.x / 8.x) that ship with PySide2 are **not supported**.  
> For IDA 7+ support use the original [HexCopy](https://github.com/OALabs/hexcopy-ida).

