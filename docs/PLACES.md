# Places

Every location Equipment Locker looks for, by tool. Generated from `src/equipment_locker/places.json`; edit that file, not this one.

Tokens: `{home}` user home; `{appconfig}` Roaming / Application Support / ~/.config; `{appdata}` Local / Application Support / ~/.local/share; `{appcache}` Local / Caches / ~/.cache; `{roaming}`, `{local}` Windows only; `{project}` a project folder. ⚠ = not yet checked against a source.

Sources: **official** vendor documentation; **community** community guides or package uninstall lists; **observed** seen on a real machine; **unverified** AI model or memory only, not yet checked

## aider (6)

| Path | OS | Scope | Category | Kind | Env | Source |
|---|---|---|---|---|---|---|
| `{home}/.aider.conf.yml` | all | user | config | file |  | [official](https://aider.chat/docs/config/aider_conf.html) |
| `{project}/.aider.conf.yml` | all | project | config | file |  | [official](https://aider.chat/docs/config/aider_conf.html) |
| `{project}/.aider.input.history` | all | project | history | file |  | [official](https://aider.chat/docs/config/aider_conf.html) |
| `{project}/.aider.chat.history.md` | all | project | history | file |  | [official](https://aider.chat/docs/config/aider_conf.html) |
| `{project}/.aider.model.settings.yml` | all | project | config | file |  | [official](https://aider.chat/docs/config/aider_conf.html) |
| `{project}/.aider.model.metadata.json` | all | project | state | file |  | [official](https://aider.chat/docs/config/aider_conf.html) |

## amp (14)

| Path | OS | Scope | Category | Kind | Env | Source |
|---|---|---|---|---|---|---|
| `{home}/.config/amp/settings.json` | darwin | user | mcp | file |  | [official](https://ampcode.com/docs/cli/settings) |
| `{home}/.config/amp/settings.jsonc` | darwin | user | mcp | file |  | [official](https://ampcode.com/docs/cli/settings) |
| `{appconfig}/amp/settings.json` | linux | user | mcp | file |  | [official](https://ampcode.com/docs/cli/settings) |
| `{appconfig}/amp/settings.jsonc` | linux | user | mcp | file |  | [official](https://ampcode.com/docs/cli/settings) |
| `{home}/.config/amp/settings.json` | win32 | user | mcp | file |  | [official](https://ampcode.com/docs/cli/settings) |
| `{home}/.config/amp/settings.jsonc` | win32 | user | mcp | file |  | [official](https://ampcode.com/docs/cli/settings) |
| `{project}/.amp/settings.json` | all | project | config | file |  | [official](https://ampcode.com/docs/cli/settings) |
| `{project}/.amp/settings.jsonc` | all | project | config | file |  | [official](https://ampcode.com/docs/cli/settings) |
| `{home}/.config/amp/skills` | all | user | skills | dir |  | [official](https://ampcode.com/docs/cli/settings) |
| `{home}/.config/agents/skills` | all | user | skills | dir |  | [official](https://ampcode.com/docs/cli/settings) |
| `{home}/.agents/skills` | all | user | skills | dir |  | [official](https://ampcode.com/docs/cli/settings) |
| `/Library/Application Support/ampcode/managed-settings.json` | darwin | system | config | file |  | [official](https://ampcode.com/docs/cli/settings) |
| `/etc/ampcode/managed-settings.json` | linux | system | config | file |  | [official](https://ampcode.com/docs/cli/settings) |
| `{programdata}/ampcode/managed-settings.json` | win32 | system | config | file |  | [official](https://ampcode.com/docs/cli/settings) |

## antigravity (28)

| Path | OS | Scope | Category | Kind | Env | Source |
|---|---|---|---|---|---|---|
| `{home}/.gemini/GEMINI.md` | all | user | instructions | file |  | official |
| `{home}/.gemini/skills` | all | user | skills | dir |  | official |
| `{home}/.gemini/antigravity-cli` | all | user | state | dir |  | official |
| `{home}/.gemini/antigravity-cli/settings.json` | all | user | config | file |  | official |
| `{home}/.gemini/antigravity-cli/keybindings.json` | all | user | config | file |  | official |
| `{home}/.gemini/antigravity-cli/skills` | all | user | skills | dir |  | official |
| `{home}/.gemini/config` | all | user | config | dir |  | community |
| `{home}/.gemini/config/mcp_config.json` | all | user | mcp | file |  | official |
| `{home}/.gemini/config/hooks.json` | all | user | hooks | file |  | official |
| `{home}/.gemini/config/plugins` | all | user | plugins | dir |  | official |
| `{home}/.gemini/antigravity` | all | user | history | dir |  | community |
| `{home}/.antigravity` | all | user | instructions | dir |  | community |
| `{home}/.antigravity_tools` | all | user | logs | dir |  | community |
| `{appconfig}/Antigravity` | all | user | state | dir |  | community |
| `{appconfig}/Antigravity/User/settings.json` | all | user | config | file |  | community |
| `{appcache}/com.google.antigravity` | darwin | user | cache | dir |  | community |
| `{applogs}/Antigravity` | all | user | logs | dir |  | community |
| `{local}/antigravity-updater` | all | user | install | dir |  | observed |
| `{local}/Programs/antigravity` | all | user | install | dir |  | community |
| `{home}/.local/bin/agy` | linux, darwin | user | install | file |  | community |
| `{project}/.agents` | all | project | config | dir |  | official |
| `{project}/.agents/skills` | all | project | skills | dir |  | official |
| `{project}/.agents/mcp_config.json` | all | project | mcp | file |  | official |
| `{project}/.agents/hooks.json` | all | project | hooks | file |  | official |
| `{project}/.agents/plugins` | all | project | plugins | dir |  | official |
| `{project}/GEMINI.md` | all | project | instructions | file |  | official |
| `{project}/AGENTS.md` | all | project | agents | file |  | official |
| `{appcache}/antigravity` | linux | user | cache | dir |  | observed |

## chatgpt-desktop (2)

| Path | OS | Scope | Category | Kind | Env | Source |
|---|---|---|---|---|---|---|
| `{appsupport}/com.openai.chat` ⚠ | all | user | history | dir |  | unverified |
| `{local}/Packages/OpenAI.ChatGPT*` ⚠ | all | user | history | glob |  | unverified |

## claude-code (58)

| Path | OS | Scope | Category | Kind | Env | Source |
|---|---|---|---|---|---|---|
| `{home}/.claude` | all | user | config | dir | CLAUDE_CONFIG_DIR | official |
| `{home}/.claude.json` | all | user | mcp | file | CLAUDE_CONFIG_DIR | official |
| `{home}/.claude/settings.json` | all | user | config | file | CLAUDE_CONFIG_DIR | official |
| `{home}/.claude/CLAUDE.md` | all | user | instructions | file | CLAUDE_CONFIG_DIR | official |
| `{home}/.claude/rules` | all | user | instructions | dir | CLAUDE_CONFIG_DIR | official |
| `{home}/.claude/skills` | all | user | skills | dir | CLAUDE_CONFIG_DIR | official |
| `{home}/.claude/agents` | all | user | agents | dir | CLAUDE_CONFIG_DIR | official |
| `{home}/.claude/commands` | all | user | commands | dir | CLAUDE_CONFIG_DIR | official |
| `{home}/.claude/workflows` | all | user | commands | dir | CLAUDE_CONFIG_DIR | official |
| `{home}/.claude/output-styles` | all | user | config | dir | CLAUDE_CONFIG_DIR | official |
| `{home}/.claude/keybindings.json` | all | user | config | file | CLAUDE_CONFIG_DIR | official |
| `{home}/.claude/plugins` | all | user | plugins | dir | CLAUDE_CONFIG_DIR | official |
| `{home}/.claude/plugins/installed_plugins.json` | all | user | plugins | file | CLAUDE_CONFIG_DIR | observed |
| `{home}/.claude/plugins/marketplaces` | all | user | plugins | dir | CLAUDE_CONFIG_DIR | observed |
| `{home}/.claude/plugins/cache` | all | user | plugins | dir | CLAUDE_CONFIG_DIR | observed |
| `{home}/.claude/plugins/synced` | all | user | plugins | dir | CLAUDE_CONFIG_DIR | observed |
| `{home}/.claude/hooks` | all | user | hooks | dir | CLAUDE_CONFIG_DIR | observed |
| `{home}/.claude/projects` | all | user | history | dir | CLAUDE_CONFIG_DIR | official |
| `{home}/.claude/history.jsonl` | all | user | history | file | CLAUDE_CONFIG_DIR | observed |
| `{home}/.claude/sessions` | all | user | history | dir | CLAUDE_CONFIG_DIR | observed |
| `{home}/.claude/plans` | all | user | state | dir | CLAUDE_CONFIG_DIR | observed |
| `{home}/.claude/file-history` | all | user | history | dir | CLAUDE_CONFIG_DIR | observed |
| `{home}/.claude/shell-snapshots` | all | user | state | dir | CLAUDE_CONFIG_DIR | observed |
| `{home}/.claude/todos` ⚠ | all | user | state | dir | CLAUDE_CONFIG_DIR | unverified |
| `{home}/.claude/ide` | all | user | state | dir | CLAUDE_CONFIG_DIR | observed |
| `{home}/.claude/cache` | all | user | cache | dir | CLAUDE_CONFIG_DIR | observed |
| `{home}/.claude/backups` | all | user | config | dir | CLAUDE_CONFIG_DIR | observed |
| `{home}/.claude/downloads` | all | user | config | dir | CLAUDE_CONFIG_DIR | observed |
| `{home}/.claude/state` | all | user | state | dir | CLAUDE_CONFIG_DIR | observed |
| `{home}/.claude/usage-data` | all | user | state | dir | CLAUDE_CONFIG_DIR | observed |
| `{appdata}/claude` | all | user | install | dir |  | observed |
| `{appstate}/claude` | all | user | state | dir |  | observed |
| `{appcache}/claude` | all | user | cache | dir |  | observed |
| `{appcache}/claude-cli-nodejs` | all | user | cache | dir |  | observed |
| `{home}/.local/bin/claude` | linux, darwin | user | install | file |  | community |
| `/Library/Application Support/ClaudeCode/managed-settings.json` | darwin | system | config | file |  | official |
| `/etc/claude-code/managed-settings.json` | linux | system | config | file |  | official |
| `{programfiles}/ClaudeCode/managed-settings.json` | win32 | system | config | file |  | official |
| `/Library/Application Support/ClaudeCode/CLAUDE.md` | darwin | system | instructions | file |  | official |
| `/etc/claude-code/CLAUDE.md` | linux | system | instructions | file |  | official |
| `{programfiles}/ClaudeCode/CLAUDE.md` | win32 | system | instructions | file |  | official |
| `/etc/claude-code/managed-mcp.json` | linux | system | mcp | file |  | official |
| `/Library/Application Support/ClaudeCode/managed-mcp.json` | darwin | system | mcp | file |  | official |
| `{programfiles}/ClaudeCode/managed-mcp.json` | win32 | system | mcp | file |  | official |
| `{project}/CLAUDE.md` | all | project | instructions | file |  | official |
| `{project}/CLAUDE.local.md` | all | project | instructions | file |  | official |
| `{project}/.mcp.json` | all | project | mcp | file |  | official |
| `{project}/.worktreeinclude` | all | project | config | file |  | official |
| `{project}/.claude` | all | project | config | dir |  | official |
| `{project}/.claude/settings.json` | all | project | config | file |  | official |
| `{project}/.claude/settings.local.json` | all | project | config | file |  | official |
| `{project}/.claude/CLAUDE.md` | all | project | instructions | file |  | official |
| `{project}/.claude/rules` | all | project | instructions | dir |  | official |
| `{project}/.claude/skills` | all | project | skills | dir |  | official |
| `{project}/.claude/agents` | all | project | agents | dir |  | official |
| `{project}/.claude/commands` | all | project | commands | dir |  | official |
| `{project}/.claude/workflows` | all | project | commands | dir |  | official |
| `{home}/.claude.json.*` | all | user | config | glob |  | observed |

## claude-desktop (8)

| Path | OS | Scope | Category | Kind | Env | Source |
|---|---|---|---|---|---|---|
| `{appconfig}/Claude` | darwin, win32 | user | state | dir |  | official |
| `{appconfig}/Claude/claude_desktop_config.json` | darwin, win32 | user | mcp | file |  | official |
| `{appconfig}/Claude` | linux | user | state | dir |  | community |
| `{appconfig}/Claude/claude_desktop_config.json` | linux | user | mcp | file |  | community |
| `{applogs}/Claude` | all | user | logs | dir |  | community |
| `{roaming}/Claude/logs` | all | user | logs | dir |  | community |
| `{local}/Packages/Claude_*` | all | user | install | glob |  | community |
| `{local}/Claude-Data` | all | user | state | dir |  | observed |

## cline (13)

| Path | OS | Scope | Category | Kind | Env | Source |
|---|---|---|---|---|---|---|
| `{home}/.cline` | all | user | hooks | dir | CLINE_DIR | [official](https://docs.cline.bot/getting-started/config) |
| `{home}/.cline/data/settings` | all | user | auth | dir | CLINE_DATA_DIR | [official](https://docs.cline.bot/getting-started/config) |
| `{home}/.cline/data/sessions` | all | user | history | dir | CLINE_DATA_DIR | [official](https://docs.cline.bot/getting-started/config) |
| `{home}/.cline/data/db` | all | user | history | dir | CLINE_DATA_DIR | [official](https://docs.cline.bot/getting-started/config) |
| `{home}/.cline/data/logs/cline.log` | all | user | logs | file | CLINE_LOG_PATH | [official](https://docs.cline.bot/getting-started/config) |
| `{home}/Documents/Cline` | all | user | hooks | dir |  | [official](https://docs.cline.bot/customization/cline-rules) |
| `{home}/.agents/AGENTS.md` | all | user | skills | file |  | [official](https://docs.cline.bot/getting-started/config) |
| `{home}/.agents/skills` | all | user | skills | file |  | [official](https://docs.cline.bot/getting-started/config) |
| `{project}/.cline` | all | project | config | dir |  | [official](https://docs.cline.bot/getting-started/config) |
| `{project}/.clinerules` | all | project | hooks | dir |  | [official](https://docs.cline.bot/customization/cline-rules) |
| `{roaming}/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json` | win32 | user | mcp | file |  | [community](https://alphaonedev.github.io/ai-memory-mcp/integrations/cline.html) |
| `{home}/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json` | darwin | user | mcp | file |  | [community](https://alphaonedev.github.io/ai-memory-mcp/integrations/cline.html) |
| `{appconfig}/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json` | linux | user | mcp | file |  | [community](https://alphaonedev.github.io/ai-memory-mcp/integrations/cline.html) |

## codex (21)

| Path | OS | Scope | Category | Kind | Env | Source |
|---|---|---|---|---|---|---|
| `{home}/.codex` | all | user | skills | dir | CODEX_HOME | official |
| `{home}/.codex/config.toml` | all | user | mcp | file | CODEX_HOME | official |
| `{home}/.codex/*.config.toml` | all | user | config | glob | CODEX_HOME | official |
| `{home}/.codex/AGENTS.md` | all | user | agents | file | CODEX_HOME | official |
| `{home}/.codex/auth.json` | all | user | auth | file | CODEX_HOME | community |
| `{home}/.codex/sessions` | all | user | history | dir | CODEX_HOME | official |
| `{home}/.codex/log` ⚠ | all | user | logs | dir | CODEX_HOME | unverified |
| `{home}/.codex/skills` | all | user | skills | dir | CODEX_HOME | official |
| `{home}/.codex/prompts` ⚠ | all | user | commands | dir | CODEX_HOME | unverified |
| `{home}/.codex/history.jsonl` ⚠ | all | user | history | file | CODEX_HOME | unverified |
| `{home}/.codex/AGENTS.override.md` | all | user | agents | file | CODEX_HOME | official |
| `{home}/.codex/agents` | all | user | agents | dir | CODEX_HOME | official |
| `{home}/.codex/packages/standalone` | all | user | cache | dir | CODEX_HOME | official |
| `{home}/.local/bin/codex` | linux, darwin | user | install | file | CODEX_INSTALL_DIR | official |
| `{local}/Programs/OpenAI/Codex` | all | user | install | dir | CODEX_INSTALL_DIR | official |
| `/etc/codex/config.toml` | linux, darwin | system | config | file |  | official |
| `{project}/AGENTS.md` | all | project | agents | file |  | official |
| `{project}/AGENTS.override.md` | all | project | agents | file |  | official |
| `{project}/.codex/agents` | all | project | agents | dir |  | official |
| `{project}/.codex` | all | project | config | dir |  | official |
| `{project}/.codex/config.toml` | all | project | config | file |  | official |

## continue (3)

| Path | OS | Scope | Category | Kind | Env | Source |
|---|---|---|---|---|---|---|
| `{home}/.continue/config.yaml` | all | user | mcp | file |  | [official](https://docs.continue.dev/cli/configuration) |
| `{project}/.continue/rules` | all | project | instructions | dir |  | [official](https://docs.continue.dev/customize/deep-dives/rules) |
| `{project}/.continue/mcpServers` | all | project | mcp | dir |  | [official](https://docs.continue.dev/customize/deep-dives/mcp) |

## copilot (15)

| Path | OS | Scope | Category | Kind | Env | Source |
|---|---|---|---|---|---|---|
| `{project}/.github/copilot-instructions.md` | all | project | instructions | file |  | [official](https://code.visualstudio.com/docs/agents/reference/custom-instructions-reference.md) |
| `{project}/.github/instructions` | all | project | instructions | dir |  | [official](https://code.visualstudio.com/docs/agents/reference/custom-instructions-reference.md) |
| `{project}/AGENTS.md` | all | project | agents | file |  | [official](https://code.visualstudio.com/docs/agents/reference/custom-instructions-reference.md) |
| `{project}/CLAUDE.md` | all | project | instructions | file |  | [official](https://code.visualstudio.com/docs/agents/reference/custom-instructions-reference.md) |
| `{project}/.claude/CLAUDE.md` | all | project | instructions | file |  | [official](https://code.visualstudio.com/docs/agents/reference/custom-instructions-reference.md) |
| `{project}/.claude/rules` | all | project | instructions | file |  | [official](https://code.visualstudio.com/docs/agents/reference/custom-instructions-reference.md) |
| `{project}/.mcp.json` | all | project | mcp | file |  | [official](https://code.visualstudio.com/docs/agents/reference/mcp-configuration.md) |
| `{project}/.vscode/mcp.json` | all | project | mcp | file |  | [official](https://code.visualstudio.com/docs/agents/reference/mcp-configuration.md) |
| `{project}/.github/agents` | all | project | agents | dir |  | [official](https://code.visualstudio.com/docs/agents/reference/custom-agent-file-reference.md) |
| `{home}/.copilot/agents` | all | user | agents | dir | COPILOT_HOME | [official](https://code.visualstudio.com/docs/agents/reference/custom-agent-file-reference.md) |
| `{project}/.github/prompts` | all | project | commands | dir |  | [official](https://code.visualstudio.com/docs/agent-customization/prompt-files.md) |
| `{project}/.github/hooks` | all | project | hooks | dir |  | [official](https://code.visualstudio.com/docs/agent-customization/hooks.md) |
| `{home}/.copilot/hooks` | all | user | hooks | dir | COPILOT_HOME | [official](https://code.visualstudio.com/docs/agent-customization/hooks.md) |
| `{project}/.github/skills` | all | project | skills | dir |  | [official](https://code.visualstudio.com/docs/agent-customization/agent-skills.md) |
| `{home}/.copilot/skills` | all | user | skills | dir |  | [official](https://code.visualstudio.com/docs/agent-customization/agent-skills.md) |

## copilot-cli (23)

| Path | OS | Scope | Category | Kind | Env | Source |
|---|---|---|---|---|---|---|
| `{home}/.copilot` | all | user | config | dir | COPILOT_HOME | [official](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-config-dir-reference) |
| `{home}/.copilot/settings.json` | all | user | config | file | COPILOT_HOME | [official](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-config-dir-reference) |
| `{home}/.copilot/config.json` | all | user | auth | file | COPILOT_HOME | [official](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-config-dir-reference) |
| `{home}/.copilot/mcp-config.json` | all | user | mcp | file | COPILOT_HOME | [official](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-config-dir-reference) |
| `{home}/.copilot/copilot-instructions.md` | all | user | history | file | COPILOT_HOME | [official](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-config-dir-reference) |
| `{home}/.copilot/instructions` | all | user | instructions | dir | COPILOT_HOME | [official](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-config-dir-reference) |
| `{home}/.copilot/agents` | all | user | agents | dir | COPILOT_HOME | [official](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-config-dir-reference) |
| `{home}/.copilot/skills` | all | user | skills | dir | COPILOT_HOME | [official](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-config-dir-reference) |
| `{home}/.copilot/hooks` | all | user | hooks | dir | COPILOT_HOME | [official](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-config-dir-reference) |
| `{home}/.copilot/extensions` | all | user | plugins | dir | COPILOT_HOME | [official](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-config-dir-reference) |
| `{home}/.copilot/installed-plugins` | all | user | plugins | dir | COPILOT_HOME | [official](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-config-dir-reference) |
| `{home}/.copilot/session-state` | all | user | history | dir | COPILOT_HOME | [official](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-config-dir-reference) |
| `{home}/.copilot/session-store.db` | all | user | history | file | COPILOT_HOME | [official](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-config-dir-reference) |
| `{home}/.copilot/command-history-state` | all | user | commands | dir | COPILOT_HOME | [official](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-config-dir-reference) |
| `{home}/.copilot/logs` | all | user | history | dir | COPILOT_HOME | [official](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-config-dir-reference) |
| `{home}/.copilot/permissions-config.json` | all | user | config | file | COPILOT_HOME | [official](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-config-dir-reference) |
| `{home}/.copilot/providers.json` | all | user | config | file | COPILOT_PROVIDERS_CONFIG | [official](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-config-dir-reference) |
| `{home}/.copilot/mcp-oauth-config` | all | user | auth | dir | COPILOT_HOME | [official](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-config-dir-reference) |
| `{home}/.copilot/mcp-secrets` | all | user | auth | dir | COPILOT_HOME | [official](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-config-dir-reference) |
| `{home}/.copilot/lsp-config.json` | all | user | config | file | COPILOT_HOME | [official](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-config-dir-reference) |
| `{home}/.copilot/ide` | all | user | state | file | COPILOT_HOME | [official](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-config-dir-reference) |
| `{project}/.github/copilot/settings.json` | all | project | config | file |  | [official](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-config-dir-reference) |
| `{project}/.github/copilot/settings.local.json` | all | project | config | file |  | [official](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-config-dir-reference) |

## cursor (25)

| Path | OS | Scope | Category | Kind | Env | Source |
|---|---|---|---|---|---|---|
| `{home}/.cursor/mcp.json` | all | user | mcp | file |  | [official](https://cursor.com/docs/mcp) |
| `{project}/.cursor/mcp.json` | all | project | mcp | file |  | [official](https://cursor.com/docs/mcp) |
| `{project}/.cursor/rules` | all | project | instructions | dir |  | [official](https://cursor.com/docs/rules) |
| `{project}/AGENTS.md` | all | project | agents | file |  | [official](https://cursor.com/docs/rules) |
| `{home}/.cursor/cli-config.json` | darwin | user | config | file | CURSOR_CONFIG_DIR | [official](https://cursor.com/docs/cli/reference/configuration) |
| `{home}/.cursor/cli-config.json` | linux | user | config | file | CURSOR_CONFIG_DIR | [official](https://cursor.com/docs/cli/reference/configuration) |
| `{home}/.cursor/cli-config.json` | win32 | user | config | file | CURSOR_CONFIG_DIR | [official](https://cursor.com/docs/cli/reference/configuration) |
| `{project}/.cursor/cli.json` | all | project | config | file |  | [official](https://cursor.com/docs/cli/reference/configuration) |
| `{home}/.cursor/hooks.json` | all | user | hooks | file |  | [official](https://cursor.com/docs/hooks) |
| `{home}/.cursor/hooks` | all | user | hooks | dir |  | [official](https://cursor.com/docs/hooks) |
| `{project}/.cursor/hooks.json` | all | project | hooks | file |  | [official](https://cursor.com/docs/hooks) |
| `/Library/Application Support/Cursor/hooks.json` | darwin | system | hooks | file |  | [official](https://cursor.com/docs/hooks) |
| `/etc/cursor/hooks.json` | linux | system | hooks | file |  | [official](https://cursor.com/docs/hooks) |
| `{programdata}/Cursor/hooks.json` | win32 | system | hooks | file |  | [official](https://cursor.com/docs/hooks) |
| `{home}/.cursor/managed/team_*/hooks` | all | user | hooks | glob |  | [official](https://cursor.com/docs/hooks) |
| `{home}/.cursor/skills` | all | user | skills | dir |  | [official](https://cursor.com/docs/skills) |
| `{home}/.agents/skills` | all | user | skills | dir |  | [official](https://cursor.com/docs/skills) |
| `{project}/.cursor/skills` | all | project | skills | dir |  | [official](https://cursor.com/docs/skills) |
| `{project}/.agents/skills` | all | project | skills | dir |  | [official](https://cursor.com/docs/skills) |
| `{home}/.claude/skills` | all | user | skills | dir |  | [official](https://cursor.com/help/customization/skills) |
| `{home}/.codex/skills` | all | user | skills | dir |  | [official](https://cursor.com/help/customization/skills) |
| `{home}/.cursor/agents` | all | user | agents | dir |  | [official](https://cursor.com/docs/subagents) |
| `{project}/.cursor/agents` | all | project | agents | dir |  | [official](https://cursor.com/docs/subagents) |
| `{home}/.cursor/subagents` | all | user | agents | dir |  | [official](https://cursor.com/docs/subagents) |
| `{home}/.cursor/plugins/local` | all | user | plugins | dir |  | [official](https://cursor.com/docs/plugins) |

## gemini-cli (16)

| Path | OS | Scope | Category | Kind | Env | Source |
|---|---|---|---|---|---|---|
| `{home}/.gemini` | all | user | config | dir |  | official |
| `{home}/.gemini/settings.json` | all | user | mcp | file |  | official |
| `{home}/.gemini/GEMINI.md` | all | user | instructions | file |  | official |
| `{home}/.gemini/extensions` ⚠ | all | user | plugins | dir |  | unverified |
| `{home}/.gemini/commands` | all | user | commands | dir |  | official |
| `{home}/.gemini/tmp` ⚠ | all | user | history | dir |  | unverified |
| `/etc/gemini-cli/settings.json` | linux | system | config | file | GEMINI_CLI_SYSTEM_SETTINGS_PATH | official |
| `/etc/gemini-cli/system-defaults.json` | linux | system | config | file | GEMINI_CLI_SYSTEM_DEFAULTS_PATH | official |
| `{programdata}/gemini-cli/settings.json` | win32 | system | config | file | GEMINI_CLI_SYSTEM_SETTINGS_PATH | official |
| `{programdata}/gemini-cli/system-defaults.json` | win32 | system | state | file | GEMINI_CLI_SYSTEM_DEFAULTS_PATH | official |
| `/Library/Application Support/GeminiCli/settings.json` | darwin | system | config | file | GEMINI_CLI_SYSTEM_SETTINGS_PATH | official |
| `/Library/Application Support/GeminiCli/system-defaults.json` | darwin | system | config | file | GEMINI_CLI_SYSTEM_DEFAULTS_PATH | official |
| `{project}/.gemini` | all | project | config | dir |  | official |
| `{project}/.gemini/settings.json` | all | project | config | file |  | official |
| `{project}/GEMINI.md` | all | project | instructions | file |  | official |
| `{project}/.geminiignore` ⚠ | all | project | config | file |  | unverified |

## goose (9)

| Path | OS | Scope | Category | Kind | Env | Source |
|---|---|---|---|---|---|---|
| `{home}/.config/goose/config.yaml` | darwin | user | mcp | file | GOOSE_PATH_ROOT | [official](https://goose-docs.ai/docs/guides/config-files/) |
| `{appconfig}/goose/config.yaml` | linux | user | config | file | GOOSE_PATH_ROOT | [official](https://goose-docs.ai/docs/guides/config-files/) |
| `{roaming}/Block/goose/config/config.yaml` | win32 | user | config | file | GOOSE_PATH_ROOT | [official](https://goose-docs.ai/docs/guides/config-files/) |
| `{home}/Library/Application Support/Block/goose` | darwin | user | state | dir | GOOSE_PATH_ROOT | [official](https://goose-docs.ai/docs/guides/environment-variables/) |
| `{appdata}/goose` | linux | user | state | dir | GOOSE_PATH_ROOT | [official](https://goose-docs.ai/docs/guides/environment-variables/) |
| `{roaming}/Block/goose` | win32 | user | state | dir | GOOSE_PATH_ROOT | [official](https://goose-docs.ai/docs/guides/environment-variables/) |
| `{home}/.config/goose/.goosehints` | all | user | instructions | file | CONTEXT_FILE_NAMES | [official](https://goose-docs.ai/docs/guides/context-engineering/using-goosehints/) |
| `{project}/.goosehints` | all | project | instructions | file | CONTEXT_FILE_NAMES | [official](https://goose-docs.ai/docs/guides/context-engineering/using-goosehints/) |
| `{project}/AGENTS.md` | all | project | agents | file | CONTEXT_FILE_NAMES | [official](https://goose-docs.ai/docs/guides/context-engineering/using-goosehints/) |

## gpt4all (3)

| Path | OS | Scope | Category | Kind | Env | Source |
|---|---|---|---|---|---|---|
| `{local}/nomic.ai/GPT4All` | win32 | user | config | dir |  | [official](https://docs.gpt4all.io/gpt4all_desktop/settings.html) |
| `{home}/Library/Application Support/nomic.ai/GPT4All` | darwin | user | config | dir |  | [official](https://docs.gpt4all.io/gpt4all_desktop/settings.html) |
| `{appdata}/nomic.ai/GPT4All` | linux | user | state | dir |  | [official](https://docs.gpt4all.io/gpt4all_desktop/settings.html) |

## huggingface (5)

| Path | OS | Scope | Category | Kind | Env | Source |
|---|---|---|---|---|---|---|
| `{home}/.cache/huggingface` | all | user | auth | dir | HF_HOME | [official](https://huggingface.co/docs/huggingface_hub/package_reference/environment_variables) |
| `{home}/.cache/huggingface/hub` | all | user | cache | dir | HF_HUB_CACHE | [official](https://huggingface.co/docs/huggingface_hub/package_reference/environment_variables) |
| `{home}/.cache/huggingface/xet` | all | user | cache | dir | HF_XET_CACHE | [official](https://huggingface.co/docs/huggingface_hub/package_reference/environment_variables) |
| `{home}/.cache/huggingface/assets` | all | user | cache | dir | HF_ASSETS_CACHE | [official](https://huggingface.co/docs/huggingface_hub/package_reference/environment_variables) |
| `{home}/.cache/huggingface/token` | all | user | auth | file | HF_TOKEN_PATH | [official](https://huggingface.co/docs/huggingface_hub/package_reference/environment_variables) |

## jan (4)

| Path | OS | Scope | Category | Kind | Env | Source |
|---|---|---|---|---|---|---|
| `{roaming}/Jan/data` | win32 | user | skills | dir |  | [official](https://docs.jan.ai/desktop/data-folder) |
| `{home}/Library/Application Support/Jan/data` | darwin | user | state | dir |  | [official](https://docs.jan.ai/desktop/data-folder) |
| `{appdata}/Jan/data` | linux | user | state | dir | XDG_DATA_HOME | [official](https://docs.jan.ai/desktop/data-folder) |
| `{home}/.jan` | all | user | skills | dir |  | [official](https://docs.jan.ai/desktop/data-folder) |

## kiro (8)

| Path | OS | Scope | Category | Kind | Env | Source |
|---|---|---|---|---|---|---|
| `{home}/.kiro/settings/mcp.json` | all | user | mcp | file |  | [official](https://kiro.dev/docs/mcp/configuration/) |
| `{project}/.kiro/settings/mcp.json` | all | project | mcp | file |  | [official](https://kiro.dev/docs/mcp/configuration/) |
| `{home}/.kiro/steering` | all | user | instructions | dir |  | [official](https://kiro.dev/docs/steering/) |
| `{project}/.kiro/steering` | all | project | instructions | dir |  | [official](https://kiro.dev/docs/steering/) |
| `{project}/.kiro/hooks` | all | project | hooks | dir |  | [official](https://kiro.dev/docs/hooks/) |
| `{home}/.kiro/hooks` | all | user | hooks | dir |  | [official](https://kiro.dev/docs/hooks/) |
| `{home}/.kiro/skills` | all | user | skills | dir |  | [official](https://kiro.dev/docs/skills/) |
| `{project}/.kiro/skills` | all | project | skills | dir |  | [official](https://kiro.dev/docs/skills/) |

## lmstudio (4)

| Path | OS | Scope | Category | Kind | Env | Source |
|---|---|---|---|---|---|---|
| `{home}/.lmstudio/models` | darwin | user | models | dir |  | [official](https://lmstudio.ai/docs/app/advanced/import-model) |
| `{home}/.lmstudio/models` | linux | user | models | dir |  | [official](https://lmstudio.ai/docs/app/advanced/import-model) |
| `{home}/.lmstudio/models` | win32 | user | models | dir |  | [community](https://tensorarchive.ai/wiki/lm-studio-model-location/) |
| `{home}/.lmstudio/mcp.json` | all | user | mcp | file |  | [community](https://mcneel.github.io/RhinoAI/docs/getting-started/lm-studio/) |

## npm (4)

| Path | OS | Scope | Category | Kind | Env | Source |
|---|---|---|---|---|---|---|
| `{home}/.npm` | darwin | user | cache | dir |  | [official](https://docs.npmjs.com/cli/v11/configuring-npm/folders/) |
| `{home}/.npm` | linux | user | cache | dir |  | [official](https://docs.npmjs.com/cli/v11/commands/npm-exec/) |
| `{local}/npm-cache` | win32 | user | cache | dir |  | [official](https://docs.npmjs.com/cli/v11/configuring-npm/folders/) |
| `{roaming}/npm` | win32 | user | install | dir |  | [official](https://docs.npmjs.com/cli/v11/configuring-npm/folders/) |

## ollama (9)

| Path | OS | Scope | Category | Kind | Env | Source |
|---|---|---|---|---|---|---|
| `{home}/.ollama` | all | user | state | dir |  | observed |
| `{home}/.ollama/models` | darwin | user | models | dir | OLLAMA_MODELS | [official](https://docs.ollama.com/faq) |
| `/usr/share/ollama/.ollama/models` | linux | system | models | dir | OLLAMA_MODELS | [official](https://docs.ollama.com/faq) |
| `{home}/.ollama/models` | win32 | user | models | dir | OLLAMA_MODELS | [official](https://docs.ollama.com/faq) |
| `{home}/.ollama/id_ed25519.pub` | darwin | user | config | file |  | [official](https://docs.ollama.com/faq) |
| `{home}/.ollama/server.json` | all | user | config | file |  | [official](https://docs.ollama.com/faq) |
| `{home}/.ollama/logs/server.log` | darwin | user | logs | file | OLLAMA_DEBUG | [official](https://docs.ollama.com/troubleshooting) |
| `{local}/Ollama` | win32 | user | logs | dir |  | [official](https://docs.ollama.com/troubleshooting) |
| `{local}/Programs/Ollama` | win32 | user | install | dir |  | [official](https://docs.ollama.com/troubleshooting) |

## opencode (17)

| Path | OS | Scope | Category | Kind | Env | Source |
|---|---|---|---|---|---|---|
| `{home}/.config/opencode/opencode.json` | all | user | mcp | file |  | [official](https://opencode.ai/docs/config/) |
| `{home}/.config/opencode/opencode.jsonc` | all | user | mcp | file |  | [official](https://opencode.ai/docs/config/) |
| `{project}/opencode.json` | all | project | config | file | OPENCODE_DISABLE_PROJECT_CONFIG | [official](https://opencode.ai/docs/config/) |
| `{project}/opencode.jsonc` | all | project | config | file | OPENCODE_DISABLE_PROJECT_CONFIG | [official](https://opencode.ai/docs/config/) |
| `{project}/.opencode/opencode.json` | all | project | config | file | OPENCODE_DISABLE_PROJECT_CONFIG | [official](https://opencode.ai/docs/config/) |
| `{project}/.opencode/opencode.jsonc` | all | project | config | file | OPENCODE_DISABLE_PROJECT_CONFIG | [official](https://opencode.ai/docs/config/) |
| `/Library/Application Support/opencode` | darwin | system | skills | dir |  | [official](https://opencode.ai/docs/config/) |
| `/etc/opencode` | linux | system | skills | dir |  | [official](https://opencode.ai/docs/config/) |
| `{programdata}/opencode` | win32 | system | skills | dir |  | [official](https://opencode.ai/docs/config/) |
| `{home}/.config/opencode/AGENTS.md` | all | user | agents | file | OPENCODE_DISABLE_CLAUDE_CODE_PROMPT | [official](https://opencode.ai/docs/instructions/) |
| `{project}/AGENTS.md` | all | project | agents | file | OPENCODE_DISABLE_PROJECT_CONFIG | [official](https://opencode.ai/docs/instructions/) |
| `{home}/.config/opencode/agents` | all | user | agents | dir |  | [official](https://opencode.ai/docs/agents/) |
| `{project}/.opencode/agents` | all | project | agents | dir |  | [official](https://opencode.ai/docs/agents/) |
| `{home}/.local/share/opencode/opencode.db` | all | user | history | file | OPENCODE_DB | [official](https://opencode.ai/docs/troubleshooting/) |
| `{home}/.local/share/opencode/log` | all | user | logs | dir |  | [official](https://opencode.ai/docs/troubleshooting/) |
| `{home}/.local/state/opencode/service.json` | all | user | state | file |  | [official](https://opencode.ai/docs/troubleshooting/) |
| `{home}/.config/opencode/service.json` | all | user | config | file |  | [official](https://opencode.ai/docs/troubleshooting/) |

## pipx (5)

| Path | OS | Scope | Category | Kind | Env | Source |
|---|---|---|---|---|---|---|
| `{appdata}/pipx` | linux | user | state | dir | PIPX_HOME | [official](https://pipx.pypa.io/stable/how-to/configure-paths.html) |
| `{home}/Library/Application Support/pipx` | darwin | user | config | dir | PIPX_HOME | [official](https://pipx.pypa.io/stable/how-to/configure-paths.html) |
| `{local}/pipx/pipx` | win32 | user | state | dir | PIPX_HOME | [official](https://pipx.pypa.io/stable/how-to/configure-paths.html) |
| `{home}/.local/bin` | all | user | mcp | dir | PIPX_BIN_DIR | [official](https://pipx.pypa.io/stable/how-to/configure-paths.html) |
| `/opt/pipx` | linux | system | install | dir | PIPX_GLOBAL_HOME | [official](https://pipx.pypa.io/stable/how-to/configure-paths.html) |

## qwen-code (15)

| Path | OS | Scope | Category | Kind | Env | Source |
|---|---|---|---|---|---|---|
| `{home}/.qwen/settings.json` | all | user | mcp | file | QWEN_HOME | [official](https://qwenlm.github.io/qwen-code-docs/en/users/configuration/settings/) |
| `{project}/.qwen/settings.json` | all | project | config | file |  | [official](https://qwenlm.github.io/qwen-code-docs/en/users/configuration/settings/) |
| `/etc/qwen-code/settings.json` | linux | system | config | file | QWEN_CODE_SYSTEM_SETTINGS_PATH | [official](https://qwenlm.github.io/qwen-code-docs/en/users/configuration/settings/) |
| `/etc/qwen-code/system-defaults.json` | linux | system | config | file | QWEN_CODE_SYSTEM_SETTINGS_PATH | [official](https://qwenlm.github.io/qwen-code-docs/en/users/configuration/settings/) |
| `{programdata}/qwen-code/settings.json` | win32 | system | config | file | QWEN_CODE_SYSTEM_SETTINGS_PATH | [official](https://qwenlm.github.io/qwen-code-docs/en/users/configuration/settings/) |
| `{programdata}/qwen-code/system-defaults.json` | win32 | system | state | file | QWEN_CODE_SYSTEM_SETTINGS_PATH | [official](https://qwenlm.github.io/qwen-code-docs/en/users/configuration/settings/) |
| `/Library/Application Support/QwenCode/settings.json` | darwin | system | config | file | QWEN_CODE_SYSTEM_SETTINGS_PATH | [official](https://qwenlm.github.io/qwen-code-docs/en/users/configuration/settings/) |
| `/Library/Application Support/QwenCode/system-defaults.json` | darwin | system | config | file | QWEN_CODE_SYSTEM_SETTINGS_PATH | [official](https://qwenlm.github.io/qwen-code-docs/en/users/configuration/settings/) |
| `{home}/.qwen/QWEN.md` | all | user | instructions | file | QWEN_HOME | [official](https://qwenlm.github.io/qwen-code-docs/en/users/configuration/settings/) |
| `{home}/.qwen/skills` | all | user | skills | dir | QWEN_HOME | [official](https://qwenlm.github.io/qwen-code-docs/en/users/configuration/settings/) |
| `{home}/.qwen/tmp/*/shell_history` | all | user | history | glob | QWEN_HOME | [official](https://qwenlm.github.io/qwen-code-docs/en/users/configuration/settings/) |
| `{home}/.qwen/file-history` | all | user | history | dir | QWEN_HOME | [official](https://qwenlm.github.io/qwen-code-docs/en/users/configuration/settings/) |
| `{home}/.qwen/plans` | all | user | history | dir | QWEN_HOME | [official](https://qwenlm.github.io/qwen-code-docs/en/users/configuration/settings/) |
| `{home}/.qwen/model-registry.json` | all | user | history | dir | QWEN_HOME | [official](https://qwenlm.github.io/qwen-code-docs/en/users/configuration/settings/) |
| `{home}/.qwen/locales` | all | user | history | dir | QWEN_HOME | [official](https://qwenlm.github.io/qwen-code-docs/en/users/configuration/settings/) |

## roo-code (16)

| Path | OS | Scope | Category | Kind | Env | Source |
|---|---|---|---|---|---|---|
| `{project}/.roo/mcp.json` | all | project | mcp | file |  | [official](https://github.com/RooCodeInc/Roo-Code-Docs/blob/main/docs/features/mcp/using-mcp-in-roo.mdx) |
| `{home}/Library/Application Support/Code/User/globalStorage/rooveterinaryinc.roo-cline/settings/mcp_settings.json` | darwin | user | mcp | file |  | [community](https://mcp.gawk.dev/docs/client-roo.html) |
| `{appconfig}/Code/User/globalStorage/rooveterinaryinc.roo-cline/settings/mcp_settings.json` | linux | user | mcp | file |  | [community](https://mcp.gawk.dev/docs/client-roo.html) |
| `{roaming}/Code/User/globalStorage/rooveterinaryinc.roo-cline/settings/mcp_settings.json` | win32 | user | mcp | file |  | [community](https://mcp.gawk.dev/docs/client-roo.html) |
| `{project}/.roomodes` | all | project | config | file |  | [official](https://github.com/RooCodeInc/Roo-Code-Docs/blob/main/docs/features/custom-modes.mdx) |
| `{home}/.roo/rules` | darwin | user | instructions | dir |  | [official](https://github.com/RooCodeInc/Roo-Code-Docs/blob/main/docs/features/custom-instructions.md) |
| `{home}/.roo/rules-*` | darwin | user | instructions | glob |  | [official](https://github.com/RooCodeInc/Roo-Code-Docs/blob/main/docs/features/custom-instructions.md) |
| `{home}/.roo/rules` | linux | user | instructions | dir |  | [official](https://github.com/RooCodeInc/Roo-Code-Docs/blob/main/docs/features/custom-instructions.md) |
| `{home}/.roo/rules-*` | linux | user | instructions | glob |  | [official](https://github.com/RooCodeInc/Roo-Code-Docs/blob/main/docs/features/custom-instructions.md) |
| `{home}/.roo/rules` | win32 | user | instructions | dir |  | [official](https://github.com/RooCodeInc/Roo-Code-Docs/blob/main/docs/features/custom-instructions.md) |
| `{home}/.roo/rules-*` | win32 | user | instructions | glob |  | [official](https://github.com/RooCodeInc/Roo-Code-Docs/blob/main/docs/features/custom-instructions.md) |
| `{project}/.roo/rules` | all | project | instructions | dir | AGENTS | [official](https://github.com/RooCodeInc/Roo-Code-Docs/blob/main/docs/features/custom-instructions.md) |
| `{project}/.roo/rules-*` | all | project | instructions | glob | AGENTS | [official](https://github.com/RooCodeInc/Roo-Code-Docs/blob/main/docs/features/custom-instructions.md) |
| `{project}/.roo/rules-*/.roorules` | all | project | instructions | glob | AGENTS | [official](https://github.com/RooCodeInc/Roo-Code-Docs/blob/main/docs/features/custom-instructions.md) |
| `{project}/.roo/rules-*/.roorules-*` | all | project | instructions | glob | AGENTS | [official](https://github.com/RooCodeInc/Roo-Code-Docs/blob/main/docs/features/custom-instructions.md) |
| `{project}/.roo/rules-*/AGENTS.md` | all | project | agents | glob | AGENTS | [official](https://github.com/RooCodeInc/Roo-Code-Docs/blob/main/docs/features/custom-instructions.md) |

## uv (9)

| Path | OS | Scope | Category | Kind | Env | Source |
|---|---|---|---|---|---|---|
| `{home}/.cache/uv` | darwin | user | cache | dir | XDG_CACHE_HOME | [official](https://docs.astral.sh/uv/reference/storage/) |
| `{appcache}/uv` | linux | user | cache | dir | XDG_CACHE_HOME | [official](https://docs.astral.sh/uv/reference/storage/) |
| `{local}/uv/cache` | win32 | user | cache | dir |  | [official](https://docs.astral.sh/uv/reference/storage/) |
| `{home}/.local/share/uv` | darwin | user | install | dir | XDG_DATA_HOME | [official](https://docs.astral.sh/uv/reference/storage/) |
| `{appdata}/uv` | linux | user | install | dir | XDG_DATA_HOME | [official](https://docs.astral.sh/uv/reference/storage/) |
| `{roaming}/uv/data` | win32 | user | state | dir | UV_TOOL_DIR | [official](https://docs.astral.sh/uv/reference/storage/) |
| `{home}/.local/bin` | all | user | config | dir | XDG_BIN_HOME | [official](https://docs.astral.sh/uv/reference/storage/) |
| `{home}/.config/uv` | all | user | config | dir | XDG_CONFIG_HOME | [official](https://docs.astral.sh/uv/reference/storage/) |
| `/etc/uv` | all | system | config | dir | XDG_CONFIG_DIRS | [official](https://docs.astral.sh/uv/reference/storage/) |

## vscode (7)

| Path | OS | Scope | Category | Kind | Env | Source |
|---|---|---|---|---|---|---|
| `{roaming}/Code/User/settings.json` | win32 | user | config | file |  | [official](https://code.visualstudio.com/docs/configure/settings) |
| `{home}/Library/Application Support/Code/User/settings.json` | darwin | user | config | file |  | [official](https://code.visualstudio.com/docs/configure/settings) |
| `{appconfig}/Code/User/settings.json` | linux | user | config | file |  | [official](https://code.visualstudio.com/docs/configure/settings) |
| `{project}/.vscode/settings.json` | all | project | config | file |  | [official](https://code.visualstudio.com/docs/configure/settings) |
| `{home}/.vscode/extensions` | win32 | user | plugins | dir |  | [official](https://code.visualstudio.com/docs/configure/extensions/extension-marketplace.md) |
| `{home}/.vscode/extensions` | darwin | user | plugins | dir |  | [official](https://code.visualstudio.com/docs/configure/extensions/extension-marketplace.md) |
| `{home}/.vscode/extensions` | linux | user | plugins | dir |  | [official](https://code.visualstudio.com/docs/configure/extensions/extension-marketplace.md) |

## windsurf (19)

| Path | OS | Scope | Category | Kind | Env | Source |
|---|---|---|---|---|---|---|
| `{home}/.codeium/windsurf/mcp_config.json` | all | user | mcp | file |  | [official](https://docs.devin.ai/windsurf/plugins/cascade/mcp) |
| `{home}/.config/devin/mcp_config.json` | darwin | user | mcp | file | XDG_CONFIG_HOME | [official](https://docs.devin.ai/windsurf/plugins/cascade/mcp) |
| `{appconfig}/devin/mcp_config.json` | linux | user | mcp | file | XDG_CONFIG_HOME | [official](https://docs.devin.ai/windsurf/plugins/cascade/mcp) |
| `{roaming}/devin/mcp_config.json` | win32 | user | mcp | file |  | [official](https://docs.devin.ai/windsurf/plugins/cascade/mcp) |
| `{home}/.codeium/windsurf/memories` | all | user | config | dir |  | [official](https://docs.windsurf.com/zh/windsurf/cascade/memories) |
| `{home}/.codeium/windsurf/memories/global_rules.md` | all | user | instructions | file |  | [official](https://docs.windsurf.com/zh/windsurf/cascade/memories) |
| `{project}/.windsurf/rules` | all | project | instructions | dir |  | [official](https://docs.windsurf.com/zh/windsurf/cascade/memories) |
| `/Library/Application Support/Windsurf` | darwin | system | hooks | dir |  | [official](https://docs.windsurf.com/zh/windsurf/cascade/memories) |
| `/etc/windsurf` | linux | system | hooks | dir |  | [official](https://docs.windsurf.com/zh/windsurf/cascade/memories) |
| `{programdata}/Windsurf` | win32 | system | hooks | dir |  | [official](https://docs.windsurf.com/zh/windsurf/cascade/memories) |
| `{home}/.codeium/windsurf/hooks.json` | all | user | hooks | file |  | [official](https://docs.windsurf.com/zh/windsurf/cascade/hooks) |
| `{project}/.windsurf/hooks.json` | all | project | hooks | file |  | [official](https://docs.windsurf.com/zh/windsurf/cascade/hooks) |
| `{home}/.codeium/windsurf/skills` | all | user | skills | dir |  | [official](https://docs.windsurf.com/zh/windsurf/cascade/skills) |
| `{project}/.windsurf/skills` | all | project | skills | dir |  | [official](https://docs.windsurf.com/zh/windsurf/cascade/skills) |
| `{home}/.codeium/windsurf/global_workflows` | all | user | commands | dir |  | [official](https://docs.devin.ai/desktop/cascade.md) |
| `{project}/.windsurf/workflows` | all | project | commands | dir |  | [official](https://docs.devin.ai/desktop/cascade.md) |
| `{home}/.codeium/.codeiumignore` | all | user | instructions | file |  | [official](https://docs.devin.ai/desktop/cascade.md) |
| `{home}/.windsurf/worktrees/*` | all | user | history | glob |  | [official](https://docs.devin.ai/desktop/cascade.md) |
| `{project}/.devin` | all | project | skills | dir |  | [official](https://docs.devin.ai/desktop/devin-local/customizations.md) |

## Gaps (no source found)

- Cursor (all): User Rules (set in Customize > Rules); docs say they are not stored on the file system
- Cursor (all): Editor user settings.json, installed VS Code-style extensions, chat history, logs, install folder: no official Cursor doc found
- GitHub Copilot (VS Code) (all): Editor-managed user MCP config ('servers' format; code --add-mcp writes here) (unparsed path: mcp.json in the VS Code user profile folder)
- GitHub Copilot (VS Code) (all): Copilot Chat extension chat/session history storage location: not found in official docs
- VS Code (all): Per-profile settings (unparsed path: Code/User/profiles/<profile ID>/settings.json)
- Roo Code (all): Global custom modes (unparsed path: settings/custom_modes.yaml in the extension's settings folder)
- Windsurf (Codeium) (all): Editor user settings.json / extensions / logs / install folder: no official doc found
- Continue.dev (all): Session history, logs, index cache under ~/.continue: not documented on pages found
- Aider (all): API keys for all providers (referenced by config docs) (unparsed path: .env)
- Goose (Block) (all): Tool permission levels, file-based secrets, runtime permission decisions, custom prompt templates (unparsed path: permission.yaml)
- Goose (Block) (all): Tool permission levels, file-based secrets, runtime permission decisions, custom prompt templates (unparsed path: secrets.yaml)
- Goose (Block) (all): Tool permission levels, file-based secrets, runtime permission decisions, custom prompt templates (unparsed path: permissions/tool_permissions.json)
- Goose (Block) (all): Tool permission levels, file-based secrets, runtime permission decisions, custom prompt templates (unparsed path: prompts/)
- Ollama (linux): Temporary runner executables; on Windows in %TEMP%\ollama* (unparsed path: temporary executable files dir)
- uv (all): Project virtual environment (unparsed path: .venv)
- pipx (all): pipx cache (pipx run envs) and logs (unparsed path: platformdirs user_cache_dir/pipx)
- pipx (all): pipx cache (pipx run envs) and logs (unparsed path: platformdirs user_cache_dir/user_log_dir)
