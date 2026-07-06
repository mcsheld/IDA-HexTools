# =============================================================================
# Hex Tools for IDA Pro 9.2+
#
# Copy Hex
# Paste Hex
#
# Ctrl+H         - Copy Hex
# Ctrl+Shift+H   - Paste Hex
# =============================================================================

import re

import idaapi
import ida_bytes
import ida_kernwin
import idc

from PySide6.QtWidgets import QApplication

PLUGIN_NAME = "Hex Tools"
VERSION = "0.2"

ACTION_COPY = "hextools:copy"
ACTION_PASTE = "hextools:paste"

# ----------------------------------------------------------------------------- 
# Options
# -----------------------------------------------------------------------------
"""
    Jump next byte after past       - True
    Stay at start cursor position   - False
"""
JUMP_AFTER_PASTE = True

"""
    Output information about copy/past bytes to Output window
"""
OUTPUT_COPY_INFO = True
OUTPUT_PAST_INFO = True

HEX_PATTERN = re.compile(
    r'^\s*(?:0x)?[0-9A-Fa-f]{2}(?:[\s:\-,]+(?:0x)?[0-9A-Fa-f]{2})*\s*$'
)

# -----------------------------------------------------------------------------
# Clipboard
# -----------------------------------------------------------------------------

def clipboard_get():
    return QApplication.clipboard().text()


def clipboard_set(text):
    QApplication.clipboard().setText(text)


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def get_current_range():
    """
    Returns:
        (start, end)

    If nothing is selected, returns current item.
    """

    start = idc.read_selection_start()
    end = idc.read_selection_end()

    if start == idaapi.BADADDR or end == idaapi.BADADDR:
        ea = ida_kernwin.get_screen_ea()
        start = ida_bytes.get_item_head(ea)
        end = ida_bytes.get_item_end(ea)

    return start, end


# -----------------------------------------------------------------------------
# Copy Hex
# -----------------------------------------------------------------------------

def copy_hex():

    start, end = get_current_range()

    if start == idaapi.BADADDR or end <= start:
        ida_kernwin.msg("[HexTools] Invalid selection.\n")
        return

    data = ida_bytes.get_bytes(start, end - start)

    if not data:
        ida_kernwin.msg("[HexTools] Unable to read bytes.\n")
        return

    text = data.hex(" ").upper()

    clipboard_set(text)

    if OUTPUT_COPY_INFO:
        ida_kernwin.msg(
            f"[HexTools] Copied {len(data)} bytes:\n{text}\n"
        )


# -----------------------------------------------------------------------------
# Paste Hex
# -----------------------------------------------------------------------------

def paste_hex():
    raise NotImplementedError


# -----------------------------------------------------------------------------
# Action handlers
# -----------------------------------------------------------------------------

class CopyHandler(idaapi.action_handler_t):

    def activate(self, ctx):
        copy_hex()
        return 1

    def update(self, ctx):
        return idaapi.AST_ENABLE_ALWAYS


class PasteHandler(idaapi.action_handler_t):

    def activate(self, ctx):
        paste_hex()
        return 1

    def update(self, ctx):
        return idaapi.AST_ENABLE_ALWAYS


# -----------------------------------------------------------------------------
# UI Hooks
# -----------------------------------------------------------------------------

class HexUIHooks(idaapi.UI_Hooks):

    def finish_populating_widget_popup(self, widget, popup):

        if ida_kernwin.get_widget_type(widget) != ida_kernwin.BWN_DISASM:
            return

        ida_kernwin.attach_action_to_popup(
            widget,
            popup,
            ACTION_COPY,
            "Hex Tools/",
            ida_kernwin.SETMENU_APP,
        )

        ida_kernwin.attach_action_to_popup(
            widget,
            popup,
            ACTION_PASTE,
            "Hex Tools/",
            ida_kernwin.SETMENU_APP,
        )


# -----------------------------------------------------------------------------
# Plugin
# -----------------------------------------------------------------------------

class HexToolsPlugin(idaapi.plugin_t):

    flags = idaapi.PLUGIN_PROC

    comment = "Copy / Paste Hex"
    help = ""

    wanted_name = PLUGIN_NAME
    wanted_hotkey = ""

    def init(self):

        idaapi.register_action(
            idaapi.action_desc_t(
                ACTION_COPY,
                "Copy Hex",
                CopyHandler(),
                "Ctrl+H",
                "Copy selected bytes",
                -1,
            )
        )

        idaapi.register_action(
            idaapi.action_desc_t(
                ACTION_PASTE,
                "Paste Hex",
                PasteHandler(),
                "Ctrl+Shift+H",
                "Paste bytes",
                -1,
            )
        )

        self.hooks = HexUIHooks()
        self.hooks.hook()

        ida_kernwin.msg(
            f"[HexTools] v{VERSION} loaded.\n"
        )

        return idaapi.PLUGIN_KEEP

    def run(self, arg):
        pass

    def term(self):

        try:
            self.hooks.unhook()
        except Exception:
            pass

        idaapi.unregister_action(ACTION_COPY)
        idaapi.unregister_action(ACTION_PASTE)

        ida_kernwin.msg("[HexTools] unloaded.\n")

# -----------------------------------------------------------------------------
# Paste Hex
# -----------------------------------------------------------------------------

def parse_hex_string(text: str):
    text = text.strip()

    if re.fullmatch(r'[0-9A-Fa-f]+', text):
        if len(text) & 1:
            raise ValueError("Odd number of hex characters.")
        return bytes.fromhex(text)

    if not HEX_PATTERN.fullmatch(text):
        raise ValueError("Clipboard does not contain valid hex bytes.")

    clean = re.sub(r'0x', '', text, flags=re.IGNORECASE)
    clean = re.sub(r'[\s:\-,]+', '', clean)

    return bytes.fromhex(clean)


def paste_hex():

    ea = ida_kernwin.get_screen_ea()

    if ea == idaapi.BADADDR:
        ida_kernwin.msg("[HexTools] Invalid address.\n")
        return

    text = clipboard_get().strip()

    #
    # If clipboard is empty or have not hex format data will show input form
    #
    try:
        data = parse_hex_string(text)
    except Exception:
        data = None

    if not data:

        text = ida_kernwin.ask_str(
            "",
            0,
            "Paste Hex"
        )

        if text is None:
            return

        try:
            data = parse_hex_string(text)
        except Exception as e:
            ida_kernwin.warning(str(e))
            return

    #
    # Patch bytes
    #
    for i, b in enumerate(data):
        ida_bytes.patch_byte(ea + i, b)

    #
    # Will jump cursor after past from clipboard?
    #
    if JUMP_AFTER_PASTE:
        ida_kernwin.jumpto(ea + len(data))

    if OUTPUT_PAST_INFO:
        ida_kernwin.msg(
            f"[HexTools] Patched {len(data)} bytes at 0x{ea:X}\n"
        )


# -----------------------------------------------------------------------------
# Plugin entry
# -----------------------------------------------------------------------------

def PLUGIN_ENTRY():
    return HexToolsPlugin()
    
