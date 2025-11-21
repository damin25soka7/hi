# SearXNG MCP Server - Enhanced Edition

An enhanced Model Context Protocol (MCP) server for SearXNG with advanced features, plugin system, and flexible deployment options.

## 🌟 Features

### Core Capabilities
- 🔍 **Category-Aware Search**: Search across different categories (general, images, videos, files, map, social media)
- 📄 **PDF Reading**: Automatic PDF detection and conversion to Markdown
- 💾 **Smart Caching**: In-memory caching with TTL and freshness validation
- 🚦 **Rate Limiting**: Domain-based rate limiting to prevent service abuse
- 🔧 **Plugin System**: Extensible architecture for adding new tools
- 📜 **Enhanced Content Extraction**: Uses Trafilatura for clean text extraction
- 🌐 **Reddit Support**: Automatically converts Reddit URLs to old.reddit.com for better scraping

### Advanced Features from OvertliDS/mcp-searxng-enhanced
- ✅ Category-specific search results (images, videos, files, maps, social media)
- ✅ PDF document processing with PyMuPDF
- ✅ Trafilatura-based content extraction
- ✅ Caching with configurable TTL
- ✅ Domain-based rate limiting
- ✅ Reddit URL conversion
- ✅ Timezone-aware datetime tool
- ✅ Enhanced error handling

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or newer (3.11 recommended)
- A running SearXNG instance (self-hosted or accessible endpoint)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd hi/searxng-mcp-crawl
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Create a `.env` file:
   ```env
   SEARXNG_BASE_URL=http://localhost:32768
   HOST=0.0.0.0
   PORT=32769
   CONTENT_MAX_LENGTH=10000
   SEARCH_RESULT_LIMIT=10
   DESIRED_TIMEZONE=America/New_York
   ```

## 📦 Usage Modes

### Mode 1: NPX (Recommended - Works with Legacy HTTP MCP Clients)

**NEW!** Run the server instantly with npx - perfect for legacy HTTP MCP clients:

```bash
# Run directly with npx
npx @damin25soka7/searxng-mcp-server

# Or from local directory
cd searxng-mcp-crawl
npx .
```

**With environment variables:**
```bash
SEARXNG_BASE_URL="http://localhost:32768" DESIRED_TIMEZONE="Asia/Seoul" npx .
```

**For legacy HTTP MCP clients, configure:**
```json
{
  "searxng-enhanced": {
    "url": "http://localhost:32769",
    "type": "http",
    "method": "sse"
  }
}
```

The npx script:
- ✅ Auto-checks Python installation
- ✅ Auto-installs dependencies if needed
- ✅ Starts HTTP server with SSE support
- ✅ Works with legacy MCP clients

See [NPX_USAGE.md](NPX_USAGE.md) for detailed npx usage instructions.

### Mode 2: JSON Block Configuration (For Modern MCP Clients)

This mode allows you to use the server with MCP clients like Claude Desktop, Cline, etc., without running Docker.

**Configuration for Claude Desktop (`claude_desktop_config.json`):**

```json
{
  "mcpServers": {
    "searxng-enhanced": {
      "command": "python",
      "args": ["/absolute/path/to/searxng-mcp-crawl/mcp_stdio_server.py"],
      "env": {
        "SEARXNG_BASE_URL": "http://localhost:32768",
        "CONTENT_MAX_LENGTH": "10000",
        "DESIRED_TIMEZONE": "America/New_York"
      }
    }
  }
}
```

**Configuration for Cline in VS Code (`cline_mcp_settings.json`):**

```json
{
  "mcpServers": {
    "searxng-enhanced": {
      "command": "python",
      "args": ["/absolute/path/to/searxng-mcp-crawl/mcp_stdio_server.py"],
      "env": {
        "SEARXNG_BASE_URL": "http://localhost:32768",
        "CONTENT_MAX_LENGTH": "10000",
        "DESIRED_TIMEZONE": "America/New_York"
      },
      "timeout": 60
    }
  }
}
```

**Key Points:**
- Use absolute paths for the Python script
- Make sure Python is in your PATH or use the full path to Python executable
- The server reads from stdin and writes to stdout (JSON-RPC protocol)
- No separate server process needed - it starts/stops with the client

### Mode 3: HTTP Server Mode (Traditional)

Run as a standalone HTTP server with SSE support:

```bash
python server.py
```

Or using npx (auto-handles dependencies):

```bash
npx .
```

The server will start at `http://localhost:32769` (or configured HOST:PORT).

## 🔧 Available Tools

### 1. search_web
Enhanced web search with category support.

**Parameters:**
- `query` (required): Search query string
- `limit` (optional, default: 10): Number of results (1-60)
- `category` (optional, default: "general"): Search category
  - `general`: Web pages with full content extraction
  - `images`: Image search results
  - `videos`: Video search results
  - `files`: File search results
  - `map`: Location/map search results
  - `social media`: Social media posts
- `language` (optional, default: "auto"): Language preference
- `time_range` (optional): Filter by time ("day", "month", "year")
- `safe_search` (optional, default: 1): Safe search level (0-2)
- `engines` (optional): Comma-separated list of engines

**Example:**
```json
{
  "name": "search_web",
  "arguments": {
    "query": "machine learning tutorials",
    "limit": 10,
    "category": "general"
  }
}
```

**Image Search Example:**
```json
{
  "name": "search_web",
  "arguments": {
    "query": "mountains landscape",
    "limit": 10,
    "category": "images"
  }
}
```

### 2. get_website
Fetch and extract content from webpages with enhanced features.

**Parameters:**
- `url` (required): URL of the webpage
- `max_length` (optional, default: 10000): Maximum content length
- `timeout` (optional, default: 30): Request timeout in seconds
- `use_cache` (optional, default: true): Whether to use caching

**Example:**
```json
{
  "name": "get_website",
  "arguments": {
    "url": "https://example.com/article",
    "max_length": 10000,
    "use_cache": true
  }
}
```

**Features:**
- Automatically detects and converts PDFs to Markdown
- Caches results for faster repeat access
- Converts Reddit URLs to old.reddit.com
- Uses Trafilatura for clean content extraction

### 3. get_current_datetime
Get the current date and time in the configured timezone.

**Example:**
```json
{
  "name": "get_current_datetime",
  "arguments": {}
}
```

**Returns:**
```json
{
  "success": true,
  "datetime": "2025-11-21T00:52:45-05:00",
  "formatted": "Thursday, November 21, 2025 at 12:52 AM (EST)",
  "timezone": "America/New_York"
}
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SEARXNG_BASE_URL` | SearXNG instance URL | `http://localhost:32768` |
| `HOST` | Server host (HTTP mode) | `0.0.0.0` |
| `PORT` | Server port (HTTP mode) | `32769` |
| `CONTENT_MAX_LENGTH` | Max content length per page | `10000` |
| `SEARCH_RESULT_LIMIT` | Default search result limit | `10` |
| `DESIRED_TIMEZONE` | Timezone for datetime tool | `America/New_York` |

### Cache Configuration

The caching system can be configured in `enhanced_crawler.py`:
- `cache_maxsize`: Maximum number of cached entries (default: 100)
- `cache_ttl_minutes`: Cache time-to-live in minutes (default: 5)
- `cache_max_age_minutes`: Maximum age for cache validation (default: 30)

### Rate Limiting Configuration

Rate limiting can be configured in `enhanced_crawler.py`:
- `rate_limit_requests_per_minute`: Max requests per domain per minute (default: 10)
- `rate_limit_timeout_seconds`: Rate limit tracking window (default: 60)

## 🔌 Plugin System

The server uses an extensible plugin system. Each plugin is a Python file in the `plugins/` directory.

**Available Plugins:**
- `enhanced_search_plugin.py`: Enhanced web search with categories
- `enhanced_crawl_plugin.py`: Enhanced webpage fetching
- `datetime_plugin.py`: Current date/time tool
- `search_plugin.py`: Original search plugin (legacy)
- `crawl_plugin.py`: Original crawl plugin (legacy)

**Creating Custom Plugins:**
1. Create a new Python file in `plugins/`
2. Inherit from `MCPPlugin` base class
3. Implement required properties: `name`, `description`, `input_schema`
4. Implement `execute()` method

Example:
```python
from plugin_base import MCPPlugin
from typing import Dict, Any

class MyPlugin(MCPPlugin):
    @property
    def name(self) -> str:
        return "my_tool"
    
    @property
    def description(self) -> str:
        return "Description of my tool"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "param": {"type": "string"}
            },
            "required": ["param"]
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        # Tool implementation
        return {"result": "success"}
```

## 📚 Architecture

### Stdio Mode (mcp_stdio_server.py)
- Communicates via stdin/stdout using JSON-RPC 2.0
- Perfect for integration with MCP clients
- No network ports required
- Automatic process lifecycle management by the client

### HTTP Mode (server.py)
- Starlette-based async HTTP server
- Server-Sent Events (SSE) for streaming responses
- Supports multiple concurrent connections
- Traditional REST-like API

### Plugin System
- Dynamic plugin loading from `plugins/` directory
- Each plugin is a self-contained MCP tool
- Hot-reload support (HTTP mode)

### Enhanced Crawler
- Unified crawler with category-aware search
- Built-in caching layer (TTLCache)
- Domain-based rate limiting
- PDF detection and processing
- Trafilatura-based content extraction

## 🐛 Troubleshooting

### Cannot connect to SearXNG
- Ensure SearXNG is running: `curl http://localhost:32768/search?q=test&format=json`
- Check `SEARXNG_BASE_URL` environment variable
- Verify firewall/network settings

### ModuleNotFoundError
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Activate your virtual environment if using one

### PDF processing fails
- Ensure `pymupdf` and `pymupdf4llm` are installed
- Check if the PDF is accessible and not corrupted

### Rate limit errors
- Adjust `rate_limit_requests_per_minute` in enhanced_crawler.py
- Wait for the rate limit window to expire (default: 60 seconds)

### MCP client can't find the server
- Use absolute paths in JSON configuration
- Ensure Python is in your PATH
- Check that `mcp_stdio_server.py` is executable: `chmod +x mcp_stdio_server.py` (Unix)

## 🙏 Acknowledgements

This project integrates features from:
- [OvertliDS/mcp-searxng-enhanced](https://github.com/OvertliDS/mcp-searxng-enhanced) - Enhanced MCP server for SearXNG
- [SearXNG](https://github.com/searxng/searxng) - Privacy-respecting metasearch engine
- [Trafilatura](https://github.com/adbar/trafilatura) - Web scraping and content extraction
- [PyMuPDF](https://pymupdf.readthedocs.io/) - PDF processing library

## 📄 License

MIT License

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues and questions:
- Open an issue on GitHub
- Check existing issues for similar problems
- Review the troubleshooting section above
