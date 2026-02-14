# son-dzai_the-war-on-art

Analysis and reporting on the ongoing war on art.

## Overview

This repository provides access to The War on Art analysis report through a Model Context Protocol (MCP) server, enabling AI assistants like Cursor to access and query the report data.

## Files

- `report.json` - The main analysis report in JSON format
- `mcp_server.py` - Python-based MCP server for report access
- `mcp.json` - MCP server configuration for Cursor
- `requirements.txt` - Python dependencies (none required for basic functionality)

## Quick Start

See [QUICKSTART.md](QUICKSTART.md) for a step-by-step guide to set up and test the MCP server with Cursor.

## Setup for Cursor AI Agent

### Option 1: Using mcp.json (Recommended)

1. Copy the `mcp.json` file to your Cursor settings directory:
   - **macOS/Linux**: `~/.cursor/mcp.json`
   - **Windows**: `%APPDATA%\Cursor\mcp.json`

2. If the file already exists, merge the server configuration:
   ```json
   {
     "mcpServers": {
       "war-on-art-report": {
         "command": "python3",
         "args": ["/absolute/path/to/mcp_server.py"],
         "description": "MCP server providing access to The War on Art analysis report"
       }
     }
   }
   ```

3. Update the path in the `args` field to the absolute path of `mcp_server.py` in this repository.

4. Restart Cursor for the changes to take effect.

### Option 2: Manual Configuration

You can also configure the MCP server directly in Cursor's settings:

1. Open Cursor Settings
2. Navigate to the MCP section
3. Add a new server with:
   - **Name**: `war-on-art-report`
   - **Command**: `python3`
   - **Args**: Path to `mcp_server.py`

## Using the MCP Server

Once configured, Cursor can access the report through the following actions:

### Get Report Summary
```json
{"action": "summary"}
```
Returns the title, date, summary, and author of the report.

### Get Full Report
```json
{"action": "full"}
```
Returns the complete report including all sections.

### Get Specific Section
```json
{"action": "section", "section_id": 1}
```
Returns a specific section by ID (1-4).

## Testing the MCP Server

You can test the MCP server manually from the command line:

```bash
# Make the script executable
chmod +x mcp_server.py

# Test with different actions
echo '{"action": "summary"}' | python3 mcp_server.py
echo '{"action": "full"}' | python3 mcp_server.py
echo '{"action": "section", "section_id": 2}' | python3 mcp_server.py
```

## Report Structure

The report contains:
- **Title**: The War on Art - Analysis Report
- **Date**: 2026-02-14
- **Sections**:
  1. Executive Summary
  2. Key Findings
  3. Recommendations
  4. Conclusion

## Requirements

- Python 3.6 or higher (no additional packages required)

## License

MIT License - See LICENSE file for details.