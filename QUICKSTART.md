# Quick Start Guide

## For Cursor Users

### Step 1: Clone the Repository
```bash
git clone https://github.com/Ozymandias-vanMokum/son-dzai_the-war-on-art.git
cd son-dzai_the-war-on-art
```

### Step 2: Configure Cursor

Copy and update your Cursor MCP configuration:

**macOS/Linux:**
```bash
# Create/edit the MCP config file
mkdir -p ~/.cursor
cat > ~/.cursor/mcp.json << 'EOF'
{
  "mcpServers": {
    "war-on-art-report": {
      "command": "python3",
      "args": ["REPLACE_WITH_FULL_PATH/mcp_server.py"],
      "description": "MCP server providing access to The War on Art analysis report"
    }
  }
}
EOF
```

**Windows (PowerShell):**
```powershell
# Create/edit the MCP config file
New-Item -ItemType Directory -Force -Path "$env:APPDATA\Cursor"
@"
{
  "mcpServers": {
    "war-on-art-report": {
      "command": "python3",
      "args": ["REPLACE_WITH_FULL_PATH\\mcp_server.py"],
      "description": "MCP server providing access to The War on Art analysis report"
    }
  }
}
"@ | Out-File -FilePath "$env:APPDATA\Cursor\mcp.json" -Encoding UTF8
```

**Important:** Replace `REPLACE_WITH_FULL_PATH` with the absolute path to `mcp_server.py` in your cloned repository.

### Step 3: Get the Full Path

**macOS/Linux:**
```bash
cd /path/to/son-dzai_the-war-on-art
pwd
# Output will be something like: /Users/yourname/son-dzai_the-war-on-art
# Use: /Users/yourname/son-dzai_the-war-on-art/mcp_server.py
```

**Windows:**
```powershell
cd C:\path\to\son-dzai_the-war-on-art
pwd
# Output will be something like: C:\Users\yourname\son-dzai_the-war-on-art
# Use: C:\Users\yourname\son-dzai_the-war-on-art\mcp_server.py
```

### Step 4: Restart Cursor

After updating the configuration, restart Cursor for changes to take effect.

### Step 5: Test the Integration

In Cursor, you can now ask questions like:
- "What is in the war on art report?"
- "Show me the summary of the report"
- "What are the key findings?"
- "Get section 3 from the report"

## Testing Manually

Before configuring Cursor, test that the MCP server works:

```bash
cd /path/to/son-dzai_the-war-on-art

# Test summary
echo '{"action": "summary"}' | python3 mcp_server.py

# Test full report
echo '{"action": "full"}' | python3 mcp_server.py

# Test specific section
echo '{"action": "section", "section_id": 1}' | python3 mcp_server.py
```

Each command should return JSON data without errors.

## Troubleshooting

### Python Not Found
If you get "python3: command not found", try:
- `python` instead of `python3`
- Install Python from python.org
- Check Python is in your PATH

### MCP Server Not Responding in Cursor
1. Check the path in mcp.json is absolute and correct
2. Verify Python 3.6+ is installed: `python3 --version`
3. Test the server manually (see above)
4. Check Cursor's logs for error messages
5. Restart Cursor completely

### Permission Denied
```bash
chmod +x mcp_server.py
```

## Advanced Configuration

### Merging with Existing MCP Servers

If you already have `mcp.json` with other servers:

```json
{
  "mcpServers": {
    "existing-server": {
      "command": "...",
      "args": ["..."]
    },
    "war-on-art-report": {
      "command": "python3",
      "args": ["/absolute/path/to/mcp_server.py"],
      "description": "MCP server providing access to The War on Art analysis report"
    }
  }
}
```

### Custom Report Data

Edit `report.json` to customize the report content. The structure should maintain:
- `title` (string)
- `date` (string)
- `summary` (string)
- `sections` (array of objects with `id`, `title`, `content`)
- `metadata` (object with `author`, `version`, `tags`)

After editing, test manually to ensure JSON is valid.

## Need Help?

- Check the main [README.md](README.md) for more details
- Review [Cursor MCP documentation](https://cursor.com/docs/context/mcp)
- Open an issue on GitHub
