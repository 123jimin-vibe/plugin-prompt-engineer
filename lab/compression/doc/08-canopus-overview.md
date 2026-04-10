+++
id = "s0001"
title = "Canopus Overview"
tags = ["meta"]
paths = []
+++

## Behavior

Canopus is a calibration and training desktop application for rhythm game players. It runs as a full-screen or windowed application with multiple navigable scenes.

### Scenes

Scene list is not closed/fixed.

**Keyboard Diagnosis** — Tests ghost key, input polling rate, and chord split.

**Input-to-Microphone Calibration** (mic required)
1. User enables microphone and presses a key.
2. Program captures keysound and shows waveform.
3. User adjusts interval and onset time of keypress sound.
4. Program records mic and detects keypresses for user confirmation.
5. Program displays time discrepancy between sound and input event.

**Audio-to-Microphone Calibration** (mic required) — Program plays audio and captures mic simultaneously to compute roundtrip time.

**Input-to-Audio Calibration** (mic optional)
1. On keypress, a beep is played with minimal possible latency.
2. If mic is available, captured keypress sound and captured beep sound are analyzed to calculate latency between them.

**Input-to-Photon Calibration** — Black screen turns white on keypress with minimal possible latency. User may use a high-speed camera externally to deduce input-to-photon latency.

**Input-to-Photon Calibration with Overlay** — Same as above, with an overlay showing microsecond-level timestamps or other indicators, so the user can determine photon-arrival time from high-speed camera footage. Separate non-overlay scene is unnecessary if overlay overhead is negligible.

**VSRG Test Menu** (3D rendering) — Highly customizable vertical scrolling rhythm game playtest. Custom sprites (note/lane/bg/bomb/...), lanespeed, perspective/orthogonal camera. Used to train skills related to eye-based and ear-based judgments. Customizable note patterns. Details TBD.

## Constraints

### Must
- Fully GUI.
- Audio signal analysis (FFT and convolution) from mic.
- Less than 1ms software overhead from theoretically minimal latency on latency-critical paths:
  - Audio playback
  - Microphone recording
  - Input from keyboard, mouse, and/or gamepad — at least OS-level event polling
  - Draw call-to-photon
  - Context-dependent: scenes whose purpose does not involve latency measurement may tolerate much higher overhead, even on the order of hundreds of milliseconds.
- Separate input and graphics threads.
- Runs on Windows x64.
- Monotonic timestamp with 1µs or better resolution.

### Desirable
- Less than 0.1ms total software overhead on latency-critical paths.
- Optional text logging for diagnostics. Any thread can emit log entries without blocking; a background consumer writes them to file.
- Compile-time instrumentation for measuring internal latencies (architecture overhead, FFT computation time). Zero overhead when disabled.
- Runs on Linux x64 and macOS.
- Immediate-mode GUI (e.g., imgui) for simple UIs — not acceptable where it would affect critical latencies (VSRG playtest, display latency calibration).
- Lua scripting for customizing VSRG graphics (future).

### Non-Critical
- Scene transition and loading time.
- Memory usage.
- CPU usage — with the caveat that high CPU consumption on one thread may disrupt other threads via contention, thermal throttling, or scheduling interference. Busy-wait loops are undesirable.

### Technology
- Language: C++.
- Build system: CMake.
- Signal processing: Custom FFT behind a modular interface; swappable with third-party backends.
- Audio API: WASAPI exclusive mode; abstracted for future cross-platform backends.
- Graphics API: DX12 (DXGI flip model + ALLOW_TEARING for lowest latency presentation).
- Windowing: Raw Win32.
- Input: Raw Input API (WM_INPUT + GetRawInputData + RIDEV_NOLEGACY for keyboard only) directly in WndProc. `GetRawInputData` (per-message) chosen over `GetRawInputBuffer` (batch) for individual per-event QPC timestamps critical to calibration accuracy. Mouse does not use `RIDEV_NOLEGACY` — legacy messages preserved for GUI interaction. GameInput under evaluation as a future replacement (lock-free, µs device-level timestamps, render-thread-safe).

## Anticipated Changes

- VSRG test menu details are TBD.
- Additional scenes may be added.
- Lua scripting support for VSRG graphics in the future.

## Dangers

- Achieving <1ms overhead across audio, input, and rendering simultaneously is the central technical challenge.
- Immediate-mode GUI overhead may conflict with latency-critical scenes.
