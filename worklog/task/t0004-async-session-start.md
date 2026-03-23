+++
id = "t0004"
title = "Make SessionStart hook async and show system message on update"
status = "pending"
tags = ["hooks", "performance", "ux"]
modifies = ["s0003"]
blocked_by = []
+++

The `SessionStart` hook that runs `ensure-deps.py` blocks the entire session until venv creation and `pip install` finish (~40s on first install). Make the hook async so it doesn't block startup.

Changes:

1. In `plugin/hooks/hooks.json`, add `"async": true` to the SessionStart hook.
2. In `plugin/scripts/ensure-deps.py`, emit a JSON response with a `systemMessage` field when an update actually happens, so Claude is informed on the next conversation turn that deps were installed. When deps are already up to date, emit nothing (current behavior).

Note: async hooks deliver JSON responses (systemMessage / additionalContext) only after the background process exits, on the next conversation turn. There is no way to show the user a real-time "installing..." message while pip is running.
