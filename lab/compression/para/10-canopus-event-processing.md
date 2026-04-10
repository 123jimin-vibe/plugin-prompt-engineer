### Event Processing

Processes `WM_INPUT` in WndProc. Calls `GetRawInputData` per message (chosen over `GetRawInputBuffer` for individual per-event QPC timestamps critical to calibration accuracy). Each event is QPC-stamped and appended to a per-frame event buffer.

Exposes typed input events (key down/up with scancode, mouse delta, gamepad state) with QPC timestamps. The active scene consumes and clears the event buffer each frame.
