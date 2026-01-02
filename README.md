# Auto-Claude MCP Server

MCP server that exposes Auto-Claude functionality to Claude Code and other MCP clients.

## Features

- **list_specs** - List all specs in a project with status
- **list_worktrees** - List isolated build directories
- **batch_status** - Comprehensive project overview
- **review_spec** - See what a build contains
- **qa_status** - QA validation status
- **review_status** - Human review/approval status
- **merge_preview** - Preview merge conflicts
- **merge_worktree** - Merge completed build
- **run_build** - Start autonomous build (long-running)
- **run_qa** - Run QA validation
- **run_followup** - Add follow-up tasks
- **discard_worktree** - Delete a build

## Installation

```bash
cd /Users/benjaminwesleythomas/GitProjects/MacMini/mcp-servers/auto-claude-mcp
pip install -e .
```

## Configuration

Add to Claude Code settings (`~/.claude/settings.json`):

```json
{
  "mcpServers": {
    "auto-claude": {
      "command": "python",
      "args": ["/Users/benjaminwesleythomas/GitProjects/MacMini/mcp-servers/auto-claude-mcp/server.py"],
      "env": {
        "AUTO_CLAUDE_BACKEND": "/Users/benjaminwesleythomas/GitProjects/Auto-Claude/apps/backend"
      }
    }
  }
}
```

## Usage

Once configured, Claude Code can use Auto-Claude tools:

```
# List specs in current project
mcp__auto-claude__list_specs

# Check build status
mcp__auto-claude__batch_status --project_dir /path/to/project

# Review what was built
mcp__auto-claude__review_spec --spec 001

# Merge a completed build
mcp__auto-claude__merge_worktree --spec 001-feature-name
```

## Environment Variables

- `AUTO_CLAUDE_BACKEND` - Path to Auto-Claude backend (default: `/Users/benjaminwesleythomas/GitProjects/Auto-Claude/apps/backend`)
- `CLAUDE_CODE_OAUTH_TOKEN` - Required for build operations
