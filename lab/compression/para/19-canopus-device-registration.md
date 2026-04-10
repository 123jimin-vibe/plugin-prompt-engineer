### Device Registration

Registers Raw Input devices on the application window:
- **Keyboard:** `RIDEV_NOLEGACY` — suppresses `WM_KEYDOWN`/`WM_CHAR`. Text input is not supported through this path.
- **Mouse:** Without `RIDEV_NOLEGACY` — preserves `WM_MOUSEMOVE`, `WM_LBUTTONDOWN`, etc. for GUI interaction.
