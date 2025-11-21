# Using SearXNG MCP Server with npx

## Quick Start with npx

You can now run the SearXNG MCP Server directly using npx without any installation:

```bash
npx @damin25soka7/searxng-mcp-server
```

Or if running from the local directory:

```bash
cd searxng-mcp-crawl
npx .
```

## Environment Variables

Configure the server using environment variables:

```bash
# Set SearXNG URL
export SEARXNG_BASE_URL="http://localhost:32768"

# Set server host and port
export HOST="0.0.0.0"
export PORT="32769"

# Set timezone
export DESIRED_TIMEZONE="Asia/Seoul"

# Run the server
npx .
```

Or inline:

```bash
SEARXNG_BASE_URL="http://localhost:32768" DESIRED_TIMEZONE="Asia/Seoul" npx .
```

## Configuration for Legacy HTTP MCP Clients

For MCP clients that only support legacy HTTP format, the server runs on HTTP with SSE (Server-Sent Events) support.

**Server URL:** `http://localhost:32769` (or your configured HOST:PORT)

### Endpoints

1. **POST /** - Send MCP JSON-RPC requests
2. **GET /** - SSE connection endpoint
3. **POST /message/{connection_id}** - Send messages to SSE connection
4. **GET /health** - Health check endpoint

### Example MCP Client Configuration

If your MCP client supports HTTP configuration, use:

```json
{
  "searxng-enhanced": {
    "url": "http://localhost:32769",
    "type": "http",
    "method": "sse"
  }
}
```

Or for simple HTTP POST:

```json
{
  "searxng-enhanced": {
    "url": "http://localhost:32769",
    "type": "http",
    "method": "post"
  }
}
```

## Testing the Server

1. **Start the server:**
   ```bash
   npx .
   ```

2. **Check health:**
   ```bash
   curl http://localhost:32769/health
   ```

3. **Test MCP protocol:**
   ```bash
   curl -X POST http://localhost:32769 \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
   ```

## Automatic Dependency Installation

The npx script will automatically:
1. Check if Python is installed
2. Check if dependencies are installed
3. Install dependencies if missing (requires pip)

If automatic installation fails, install manually:

```bash
cd searxng-mcp-crawl
pip install -r requirements.txt
```

## Requirements

- **Node.js** 14.0.0 or newer (for npx)
- **Python** 3.9 or newer
- **SearXNG** instance running (default: http://localhost:32768)

## Features

All enhanced features are available via HTTP:
- Category-aware search (general, images, videos, files, map, social media)
- PDF reading with Markdown conversion
- Smart caching (TTL-based)
- Rate limiting (domain-based)
- Enhanced content extraction (Trafilatura)
- Reddit URL conversion
- Timezone-aware datetime tool

## Available Tools

1. **search_web** - Enhanced search with categories
2. **get_website** - Enhanced webpage fetching with PDF support
3. **get_current_datetime** - Timezone-aware datetime
4. **search** - Legacy search
5. **fetch_webpage** - Legacy crawl
6. **runLLM** - AI access
7. **executor** - Tool executor
8. **tool_planner** - Task planner

## Troubleshooting

### Python not found
- Install Python 3.9+ from https://python.org
- Ensure Python is in your PATH

### Dependencies installation failed
- Run manually: `pip install -r requirements.txt`
- Use virtual environment if needed:
  ```bash
  python -m venv .venv
  source .venv/bin/activate  # or .venv\Scripts\activate on Windows
  pip install -r requirements.txt
  ```

### SearXNG connection failed
- Ensure SearXNG is running: `curl http://localhost:32768/search?q=test&format=json`
- Check SEARXNG_BASE_URL environment variable
- Verify firewall/network settings

### Port already in use
- Change the port: `PORT=8080 npx .`
- Or set it permanently: `export PORT=8080`

## Development

To run locally without npx:

```bash
node index.js
```

Or run the Python server directly:

```bash
python server.py
```
