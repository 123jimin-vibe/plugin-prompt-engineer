+++
id = "t0001"
title = "Add requirements.txt and dependency installation hook"
status = "done"
tags = ["dependencies", "setup"]
modifies = ["s0001"]
blocked_by = []
+++

Add `plugin/requirements.txt` with:

```
anthropic>=0.45
openai>=1.0
tiktoken>=0.7
```

Add a `SessionStart` hook that installs these into a venv at `${CLAUDE_PLUGIN_DATA}`, using the diff-and-reinstall pattern from the plugin docs.
