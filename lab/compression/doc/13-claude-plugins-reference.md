# Plugins reference

> Complete technical reference for Claude Code plugin system, including schemas, CLI commands, and component specifications.

This reference provides complete technical specifications for the Claude Code plugin system, including component schemas, CLI commands, and development tools.

A **plugin** is a self-contained directory of components that extends Claude Code with custom functionality. Plugin components include skills, agents, hooks, MCP servers, and LSP servers.

## Plugin components reference

### Skills

Plugins add skills to Claude Code, creating `/name` shortcuts that you or Claude can invoke.

**Location**: `skills/` or `commands/` directory in plugin root

**File format**: Skills are directories with `SKILL.md`; commands are simple markdown files

**Skill structure**:

```text
skills/
├── pdf-processor/
│   ├── SKILL.md
│   ├── reference.md (optional)
│   └── scripts/ (optional)
└── code-reviewer/
    └── SKILL.md
```

**Integration behavior**:

* Skills and commands are automatically discovered when the plugin is installed
* Claude can invoke them automatically based on task context
* Skills can include supporting files alongside SKILL.md

### Agents

Plugins can provide specialized subagents for specific tasks that Claude can invoke automatically when appropriate.

**Location**: `agents/` directory in plugin root

**File format**: Markdown files describing agent capabilities

**Agent structure**:

```markdown
---
name: agent-name
description: What this agent specializes in and when Claude should invoke it
model: sonnet
effort: medium
maxTurns: 20
disallowedTools: Write, Edit
---

Detailed system prompt for the agent describing its role, expertise, and behavior.
```

Plugin agents support `name`, `description`, `model`, `effort`, `maxTurns`, `tools`, `disallowedTools`, `skills`, `memory`, `background`, and `isolation` frontmatter fields. The only valid `isolation` value is `"worktree"`. For security reasons, `hooks`, `mcpServers`, and `permissionMode` are not supported for plugin-shipped agents.

**Integration points**:

* Agents appear in the `/agents` interface
* Claude can invoke agents automatically based on task context
* Agents can be invoked manually by users
* Plugin agents work alongside built-in Claude agents

### Hooks

Plugins can provide event handlers that respond to Claude Code events automatically.

**Location**: `hooks/hooks.json` in plugin root, or inline in plugin.json

**Format**: JSON configuration with event matchers and actions

**Hook configuration**:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/scripts/format-code.sh"
          }
        ]
      }
    ]
  }
}
```

Plugin hooks respond to the same lifecycle events as user-defined hooks:

| Event | When it fires |
| :--- | :--- |
| `SessionStart` | When a session begins or resumes |
| `UserPromptSubmit` | When you submit a prompt, before Claude processes it |
| `PreToolUse` | Before a tool call executes. Can block it |
| `PermissionRequest` | When a permission dialog appears |
| `PermissionDenied` | When a tool call is denied by the auto mode classifier. Return `{retry: true}` to tell the model it may retry the denied tool call |
| `PostToolUse` | After a tool call succeeds |
| `PostToolUseFailure` | After a tool call fails |
| `Notification` | When Claude Code sends a notification |
| `SubagentStart` | When a subagent is spawned |
| `SubagentStop` | When a subagent finishes |
| `TaskCreated` | When a task is being created via `TaskCreate` |
| `TaskCompleted` | When a task is being marked as completed |
| `Stop` | When Claude finishes responding |
| `StopFailure` | When the turn ends due to an API error. Output and exit code are ignored |
| `TeammateIdle` | When an agent team teammate is about to go idle |
| `InstructionsLoaded` | When a CLAUDE.md or `.claude/rules/*.md` file is loaded into context |
| `ConfigChange` | When a configuration file changes during a session |
| `CwdChanged` | When the working directory changes |
| `FileChanged` | When a watched file changes on disk. The `matcher` field specifies which filenames to watch |
| `WorktreeCreate` | When a worktree is being created via `--worktree` or `isolation: "worktree"` |
| `WorktreeRemove` | When a worktree is being removed |
| `PreCompact` | Before context compaction |
| `PostCompact` | After context compaction completes |
| `Elicitation` | When an MCP server requests user input during a tool call |
| `ElicitationResult` | After a user responds to an MCP elicitation |
| `SessionEnd` | When a session terminates |

**Hook types**:

* `command`: execute shell commands or scripts
* `http`: send the event JSON as a POST request to a URL
* `prompt`: evaluate a prompt with an LLM (uses `$ARGUMENTS` placeholder for context)
* `agent`: run an agentic verifier with tools for complex verification tasks

### MCP servers

Plugins can bundle Model Context Protocol (MCP) servers to connect Claude Code with external tools and services.

**Location**: `.mcp.json` in plugin root, or inline in plugin.json

**Format**: Standard MCP server configuration

**MCP server configuration**:

```json
{
  "mcpServers": {
    "plugin-database": {
      "command": "${CLAUDE_PLUGIN_ROOT}/servers/db-server",
      "args": ["--config", "${CLAUDE_PLUGIN_ROOT}/config.json"],
      "env": {
        "DB_PATH": "${CLAUDE_PLUGIN_ROOT}/data"
      }
    },
    "plugin-api-client": {
      "command": "npx",
      "args": ["@company/mcp-server", "--plugin-mode"],
      "cwd": "${CLAUDE_PLUGIN_ROOT}"
    }
  }
}
```

**Integration behavior**:

* Plugin MCP servers start automatically when the plugin is enabled
* Servers appear as standard MCP tools in Claude's toolkit
* Server capabilities integrate seamlessly with Claude's existing tools
* Plugin servers can be configured independently of user MCP servers

### LSP servers

Plugins can provide Language Server Protocol (LSP) servers to give Claude real-time code intelligence while working on your codebase.

LSP integration provides:

* **Instant diagnostics**: Claude sees errors and warnings immediately after each edit
* **Code navigation**: go to definition, find references, and hover information
* **Language awareness**: type information and documentation for code symbols

**Location**: `.lsp.json` in plugin root, or inline in `plugin.json`

**Format**: JSON configuration mapping language server names to their configurations

**`.lsp.json` file format**:

```json
{
  "go": {
    "command": "gopls",
    "args": ["serve"],
    "extensionToLanguage": {
      ".go": "go"
    }
  }
}
```

**Required fields:**

| Field | Description |
| :--- | :--- |
| `command` | The LSP binary to execute (must be in PATH) |
| `extensionToLanguage` | Maps file extensions to language identifiers |

**Optional fields:**

| Field | Description |
| :--- | :--- |
| `args` | Command-line arguments for the LSP server |
| `transport` | Communication transport: `stdio` (default) or `socket` |
| `env` | Environment variables to set when starting the server |
| `initializationOptions` | Options passed to the server during initialization |
| `settings` | Settings passed via `workspace/didChangeConfiguration` |
| `workspaceFolder` | Workspace folder path for the server |
| `startupTimeout` | Max time to wait for server startup (milliseconds) |
| `shutdownTimeout` | Max time to wait for graceful shutdown (milliseconds) |
| `restartOnCrash` | Whether to automatically restart the server if it crashes |
| `maxRestarts` | Maximum number of restart attempts before giving up |

## Plugin installation scopes

When you install a plugin, you choose a **scope** that determines where the plugin is available and who else can use it:

| Scope | Settings file | Use case |
| :--- | :--- | :--- |
| `user` | `~/.claude/settings.json` | Personal plugins available across all projects (default) |
| `project` | `.claude/settings.json` | Team plugins shared via version control |
| `local` | `.claude/settings.local.json` | Project-specific plugins, gitignored |
| `managed` | Managed settings | Managed plugins (read-only, update only) |

## Plugin manifest schema

The `.claude-plugin/plugin.json` file defines your plugin's metadata and configuration.

The manifest is optional. If omitted, Claude Code auto-discovers components in default locations and derives the plugin name from the directory name.

### Required fields

If you include a manifest, `name` is the only required field.

| Field | Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `name` | string | Unique identifier (kebab-case, no spaces) | `"deployment-tools"` |

### Metadata fields

| Field | Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `version` | string | Semantic version | `"2.1.0"` |
| `description` | string | Brief explanation of plugin purpose | `"Deployment automation tools"` |
| `author` | object | Author information | `{"name": "Dev Team", "email": "dev@company.com"}` |
| `homepage` | string | Documentation URL | `"https://docs.example.com"` |
| `repository` | string | Source code URL | `"https://github.com/user/plugin"` |
| `license` | string | License identifier | `"MIT"`, `"Apache-2.0"` |
| `keywords` | array | Discovery tags | `["deployment", "ci-cd"]` |

### Component path fields

| Field | Type | Description |
| :--- | :--- | :--- |
| `skills` | string\|array | Custom skill directories (replaces default `skills/`) |
| `commands` | string\|array | Custom flat `.md` skill files or directories (replaces default `commands/`) |
| `agents` | string\|array | Custom agent files (replaces default `agents/`) |
| `hooks` | string\|array\|object | Hook config paths or inline config |
| `mcpServers` | string\|array\|object | MCP config paths or inline config |
| `outputStyles` | string\|array | Custom output style files/directories (replaces default `output-styles/`) |
| `lspServers` | string\|array\|object | LSP configs for code intelligence |
| `userConfig` | object | User-configurable values prompted at enable time |
| `channels` | array | Channel declarations for message injection |

### User configuration

The `userConfig` field declares values that Claude Code prompts the user for when the plugin is enabled.

```json
{
  "userConfig": {
    "api_endpoint": {
      "description": "Your team's API endpoint",
      "sensitive": false
    },
    "api_token": {
      "description": "API authentication token",
      "sensitive": true
    }
  }
}
```

Keys must be valid identifiers. Each value is available for substitution as `${user_config.KEY}` in MCP and LSP server configs, hook commands, and (for non-sensitive values only) skill and agent content. Values are also exported to plugin subprocesses as `CLAUDE_PLUGIN_OPTION_<KEY>` environment variables.

### Environment variables

**`${CLAUDE_PLUGIN_ROOT}`**: the absolute path to your plugin's installation directory. Use this to reference scripts, binaries, and config files bundled with the plugin. This path changes when the plugin updates, so files you write here do not survive an update.

**`${CLAUDE_PLUGIN_DATA}`**: a persistent directory for plugin state that survives updates. Use this for installed dependencies such as `node_modules` or Python virtual environments, generated code, caches, and any other files that should persist across plugin versions.

## Plugin directory structure

### Standard plugin layout

```text
enterprise-plugin/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   ├── code-reviewer/
│   │   └── SKILL.md
│   └── pdf-processor/
│       ├── SKILL.md
│       └── scripts/
├── commands/
│   ├── status.md
│   └── logs.md
├── agents/
│   ├── security-reviewer.md
│   ├── performance-tester.md
│   └── compliance-checker.md
├── output-styles/
│   └── terse.md
├── hooks/
│   ├── hooks.json
│   └── security-hooks.json
├── bin/
│   └── my-tool
├── settings.json
├── .mcp.json
├── .lsp.json
├── scripts/
│   ├── security-scan.sh
│   ├── format-code.py
│   └── deploy.js
├── LICENSE
└── CHANGELOG.md
```

### File locations reference

| Component | Default Location | Purpose |
| :--- | :--- | :--- |
| **Manifest** | `.claude-plugin/plugin.json` | Plugin metadata and configuration (optional) |
| **Skills** | `skills/` | Skills with `<name>/SKILL.md` structure |
| **Commands** | `commands/` | Skills as flat Markdown files |
| **Agents** | `agents/` | Subagent Markdown files |
| **Output styles** | `output-styles/` | Output style definitions |
| **Hooks** | `hooks/hooks.json` | Hook configuration |
| **MCP servers** | `.mcp.json` | MCP server definitions |
| **LSP servers** | `.lsp.json` | Language server configurations |
| **Executables** | `bin/` | Executables added to the Bash tool's `PATH` |
| **Settings** | `settings.json` | Default configuration applied when the plugin is enabled |

## CLI commands reference

### plugin install

```bash
claude plugin install <plugin> [options]
```

| Option | Description | Default |
| :--- | :--- | :--- |
| `-s, --scope <scope>` | Installation scope: `user`, `project`, or `local` | `user` |

### plugin uninstall

```bash
claude plugin uninstall <plugin> [options]
```

| Option | Description | Default |
| :--- | :--- | :--- |
| `-s, --scope <scope>` | Uninstall from scope: `user`, `project`, or `local` | `user` |
| `--keep-data` | Preserve the plugin's persistent data directory | |

**Aliases:** `remove`, `rm`

### plugin enable

```bash
claude plugin enable <plugin> [options]
```

### plugin disable

```bash
claude plugin disable <plugin> [options]
```

### plugin update

```bash
claude plugin update <plugin> [options]
```
