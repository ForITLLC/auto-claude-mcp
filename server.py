#!/usr/bin/env python3
"""
Auto-Claude MCP Server
======================
Exposes Auto-Claude functionality via Model Context Protocol.
"""

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Auto-Claude backend path
AUTO_CLAUDE_BACKEND = Path(os.environ.get(
    "AUTO_CLAUDE_BACKEND",
    "/Users/benjaminwesleythomas/GitProjects/Auto-Claude/apps/backend"
))

server = Server("auto-claude-mcp")


def run_auto_claude_command(args: list[str], project_dir: str | None = None) -> dict[str, Any]:
    """Run an Auto-Claude CLI command and return the result."""
    cmd = [sys.executable, str(AUTO_CLAUDE_BACKEND / "run.py")] + args

    env = os.environ.copy()
    if project_dir:
        env["PWD"] = project_dir

    try:
        result = subprocess.run(
            cmd,
            cwd=project_dir or os.getcwd(),
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
            env=env
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Command timed out after 5 minutes",
            "stdout": "",
            "stderr": ""
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "stdout": "",
            "stderr": ""
        }


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available Auto-Claude tools."""
    return [
        Tool(
            name="list_specs",
            description="List all specs in an Auto-Claude project with their status",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_dir": {
                        "type": "string",
                        "description": "Project directory path (defaults to current directory)"
                    }
                }
            }
        ),
        Tool(
            name="list_worktrees",
            description="List all spec worktrees and their status (isolated build directories)",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_dir": {
                        "type": "string",
                        "description": "Project directory path"
                    }
                }
            }
        ),
        Tool(
            name="batch_status",
            description="Show status of all specs in a project (comprehensive overview)",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_dir": {
                        "type": "string",
                        "description": "Project directory path"
                    }
                }
            }
        ),
        Tool(
            name="review_spec",
            description="Review what an existing build contains (shows diff/changes)",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_dir": {
                        "type": "string",
                        "description": "Project directory path"
                    },
                    "spec": {
                        "type": "string",
                        "description": "Spec identifier (e.g., '001' or '001-feature-name')"
                    }
                },
                "required": ["spec"]
            }
        ),
        Tool(
            name="qa_status",
            description="Show QA validation status for a spec",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_dir": {
                        "type": "string",
                        "description": "Project directory path"
                    },
                    "spec": {
                        "type": "string",
                        "description": "Spec identifier"
                    }
                },
                "required": ["spec"]
            }
        ),
        Tool(
            name="review_status",
            description="Show human review/approval status for a spec",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_dir": {
                        "type": "string",
                        "description": "Project directory path"
                    },
                    "spec": {
                        "type": "string",
                        "description": "Spec identifier"
                    }
                },
                "required": ["spec"]
            }
        ),
        Tool(
            name="merge_preview",
            description="Preview merge conflicts without actually merging (returns JSON)",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_dir": {
                        "type": "string",
                        "description": "Project directory path"
                    },
                    "spec": {
                        "type": "string",
                        "description": "Spec identifier"
                    },
                    "base_branch": {
                        "type": "string",
                        "description": "Base branch for merge (optional)"
                    }
                },
                "required": ["spec"]
            }
        ),
        Tool(
            name="merge_worktree",
            description="Merge a completed build into the main project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_dir": {
                        "type": "string",
                        "description": "Project directory path"
                    },
                    "spec": {
                        "type": "string",
                        "description": "Spec identifier"
                    },
                    "no_commit": {
                        "type": "boolean",
                        "description": "Stage changes but don't commit (review in IDE first)"
                    },
                    "base_branch": {
                        "type": "string",
                        "description": "Base branch for merge"
                    }
                },
                "required": ["spec"]
            }
        ),
        Tool(
            name="run_build",
            description="Run a spec build (starts autonomous coding session). WARNING: Long-running operation!",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_dir": {
                        "type": "string",
                        "description": "Project directory path"
                    },
                    "spec": {
                        "type": "string",
                        "description": "Spec identifier (e.g., '001')"
                    },
                    "model": {
                        "type": "string",
                        "description": "Claude model to use (default: claude-sonnet-4-20250514)"
                    },
                    "isolated": {
                        "type": "boolean",
                        "description": "Force building in isolated workspace (safer)"
                    },
                    "direct": {
                        "type": "boolean",
                        "description": "Build directly in project (no isolation)"
                    },
                    "skip_qa": {
                        "type": "boolean",
                        "description": "Skip automatic QA validation after build"
                    }
                },
                "required": ["spec"]
            }
        ),
        Tool(
            name="run_qa",
            description="Run QA validation loop on a completed build",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_dir": {
                        "type": "string",
                        "description": "Project directory path"
                    },
                    "spec": {
                        "type": "string",
                        "description": "Spec identifier"
                    },
                    "model": {
                        "type": "string",
                        "description": "Claude model to use"
                    }
                },
                "required": ["spec"]
            }
        ),
        Tool(
            name="run_followup",
            description="Add follow-up tasks to a completed spec",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_dir": {
                        "type": "string",
                        "description": "Project directory path"
                    },
                    "spec": {
                        "type": "string",
                        "description": "Spec identifier"
                    },
                    "model": {
                        "type": "string",
                        "description": "Claude model to use"
                    }
                },
                "required": ["spec"]
            }
        ),
        Tool(
            name="discard_worktree",
            description="Discard an existing build (deletes worktree). Use with caution!",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_dir": {
                        "type": "string",
                        "description": "Project directory path"
                    },
                    "spec": {
                        "type": "string",
                        "description": "Spec identifier"
                    }
                },
                "required": ["spec"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Execute an Auto-Claude tool."""
    project_dir = arguments.get("project_dir")
    spec = arguments.get("spec")

    if name == "list_specs":
        result = run_auto_claude_command(["--list"], project_dir)

    elif name == "list_worktrees":
        result = run_auto_claude_command(["--list-worktrees"], project_dir)

    elif name == "batch_status":
        result = run_auto_claude_command(["--batch-status"], project_dir)

    elif name == "review_spec":
        result = run_auto_claude_command(["--spec", spec, "--review"], project_dir)

    elif name == "qa_status":
        result = run_auto_claude_command(["--spec", spec, "--qa-status"], project_dir)

    elif name == "review_status":
        result = run_auto_claude_command(["--spec", spec, "--review-status"], project_dir)

    elif name == "merge_preview":
        args = ["--spec", spec, "--merge-preview"]
        if arguments.get("base_branch"):
            args.extend(["--base-branch", arguments["base_branch"]])
        result = run_auto_claude_command(args, project_dir)

    elif name == "merge_worktree":
        args = ["--spec", spec, "--merge"]
        if arguments.get("no_commit"):
            args.append("--no-commit")
        if arguments.get("base_branch"):
            args.extend(["--base-branch", arguments["base_branch"]])
        result = run_auto_claude_command(args, project_dir)

    elif name == "run_build":
        args = ["--spec", spec, "--auto-continue"]
        if arguments.get("model"):
            args.extend(["--model", arguments["model"]])
        if arguments.get("isolated"):
            args.append("--isolated")
        if arguments.get("direct"):
            args.append("--direct")
        if arguments.get("skip_qa"):
            args.append("--skip-qa")
        result = run_auto_claude_command(args, project_dir)

    elif name == "run_qa":
        args = ["--spec", spec, "--qa"]
        if arguments.get("model"):
            args.extend(["--model", arguments["model"]])
        result = run_auto_claude_command(args, project_dir)

    elif name == "run_followup":
        args = ["--spec", spec, "--followup"]
        if arguments.get("model"):
            args.extend(["--model", arguments["model"]])
        result = run_auto_claude_command(args, project_dir)

    elif name == "discard_worktree":
        # Force discard - be careful!
        result = run_auto_claude_command(["--spec", spec, "--discard", "--force"], project_dir)

    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

    # Format response
    output = []
    if result.get("success"):
        output.append(f"✓ Command succeeded")
    else:
        output.append(f"✗ Command failed")
        if result.get("error"):
            output.append(f"Error: {result['error']}")

    if result.get("stdout"):
        output.append(f"\n{result['stdout']}")
    if result.get("stderr"):
        output.append(f"\nStderr:\n{result['stderr']}")

    return [TextContent(type="text", text="\n".join(output))]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
