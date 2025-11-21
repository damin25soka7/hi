# MCP Client Configuration Examples

## For Legacy HTTP MCP Clients

### Basic Configuration

If your MCP client uses HTTP/SSE (most legacy clients), use this configuration:

```json
{
  "searxng-enhanced": {
    "url": "http://127.0.0.1:32769",
    "type": "http",
    "method": "sse"
  }
}
```

### If Using Different Port

If you changed the port in `.env` file (e.g., PORT=8080):

```json
{
  "searxng-enhanced": {
    "url": "http://127.0.0.1:8080",
    "type": "http",
    "method": "sse"
  }
}
```

### If Using Different Host

If your server is on another machine (e.g., 192.168.1.100):

```json
{
  "searxng-enhanced": {
    "url": "http://192.168.1.100:32769",
    "type": "http",
    "method": "sse"
  }
}
```

## For Modern MCP Clients (stdio)

If your MCP client supports stdio mode (Claude Desktop, Cline):

### Windows

```json
{
  "mcpServers": {
    "searxng-enhanced": {
      "command": "python",
      "args": ["C:\\path\\to\\searxng-mcp-crawl\\mcp_stdio_server.py"],
      "env": {
        "SEARXNG_BASE_URL": "http://localhost:32768",
        "DESIRED_TIMEZONE": "Asia/Seoul"
      }
    }
  }
}
```

### Mac/Linux

```json
{
  "mcpServers": {
    "searxng-enhanced": {
      "command": "python3",
      "args": ["/absolute/path/to/searxng-mcp-crawl/mcp_stdio_server.py"],
      "env": {
        "SEARXNG_BASE_URL": "http://localhost:32768",
        "DESIRED_TIMEZONE": "Asia/Seoul"
      }
    }
  }
}
```

## Common Configuration Options

### Full Configuration (All Options)

```json
{
  "searxng-enhanced": {
    "url": "http://127.0.0.1:32769",
    "type": "http",
    "method": "sse",
    "timeout": 60,
    "headers": {
      "User-Agent": "MCP-Client/1.0"
    }
  }
}
```

### Multiple Servers

If you want to run multiple instances:

```json
{
  "searxng-main": {
    "url": "http://127.0.0.1:32769",
    "type": "http",
    "method": "sse"
  },
  "searxng-backup": {
    "url": "http://127.0.0.1:32770",
    "type": "http",
    "method": "sse"
  }
}
```

## Testing Your Configuration

### 1. Check Server is Running

Open browser or use curl:
```bash
http://127.0.0.1:32769/health
```

Should return:
```json
{
  "status": "ok",
  "plugins": 8,
  "available_tools": ["search_web", "get_website", ...]
}
```

### 2. Test Tools List

```bash
curl -X POST http://127.0.0.1:32769 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

### 3. Test a Tool

```bash
curl -X POST http://127.0.0.1:32769 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "get_current_datetime",
      "arguments": {}
    }
  }'
```

## Troubleshooting

### "Connection refused"
- Server not running? Start with `start.bat` or `start.sh`
- Wrong port? Check `.env` file
- Firewall blocking? Allow port 32769

### "Timeout"
- Increase timeout in configuration
- Check server logs for errors

### "Unknown method"
- Check server is running with `curl http://127.0.0.1:32769/health`
- Verify JSON format is correct

## Different MCP Client Types

### 1. Legacy HTTP/SSE (Most Common)
```json
{
  "url": "http://127.0.0.1:32769",
  "type": "http",
  "method": "sse"
}
```

### 2. Simple HTTP POST
```json
{
  "url": "http://127.0.0.1:32769",
  "type": "http",
  "method": "post"
}
```

### 3. WebSocket (If Supported)
```json
{
  "url": "ws://127.0.0.1:32769",
  "type": "websocket"
}
```

Note: This server uses HTTP+SSE by default. WebSocket not supported yet.

## Need Help?

1. Check if server is running: http://127.0.0.1:32769/health
2. Check server logs in terminal window
3. See `시작하기.md` or `GETTING_STARTED.md` for basics
4. Open GitHub issue with error details
