# Integration Summary

## 🎉 Mission Accomplished!

All enhanced features from [OvertliDS/mcp-searxng-enhanced](https://github.com/OvertliDS/mcp-searxng-enhanced) have been successfully integrated into your SearXNG MCP server!

## ✅ What's New

### 1. Category-Aware Search
Search across different content types:
- **General**: Full webpage content extraction
- **Images**: Image URLs with metadata
- **Videos**: Video information and embed URLs
- **Files**: File downloads with format and size
- **Map**: Location data with coordinates
- **Social Media**: Social posts and profiles

### 2. PDF Reading
- Automatic PDF detection
- Conversion to Markdown using PyMuPDF
- Works seamlessly in both search and get_website tools

### 3. Smart Caching
- In-memory TTL cache (100 entries, 5-minute TTL)
- Freshness validation (30-minute max age)
- Automatic cache refresh for stale content
- Significant performance improvement for repeated requests

### 4. Rate Limiting
- Domain-based throttling (10 requests/minute per domain)
- Prevents overwhelming target websites
- Avoids IP blocking

### 5. Enhanced Content Extraction
- Uses Trafilatura for clean text extraction
- Reddit URL conversion (www.reddit.com → old.reddit.com)
- Emoji removal and text normalization
- Better readability

### 6. Additional Tools
- **get_current_datetime**: Timezone-aware date/time (supports Asia/Seoul and other timezones)

## 📦 Two Deployment Modes

### Mode 1: JSON Block Configuration (NEW! ✨)
**No Docker required!** Configure directly in your MCP client.

**For Claude Desktop:**
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

**For Cline (VS Code):**
```json
{
  "mcpServers": {
    "searxng-enhanced": {
      "command": "python3",
      "args": ["/absolute/path/to/searxng-mcp-crawl/mcp_stdio_server.py"],
      "env": {
        "SEARXNG_BASE_URL": "http://localhost:32768",
        "DESIRED_TIMEZONE": "Asia/Seoul"
      },
      "timeout": 60
    }
  }
}
```

### Mode 2: HTTP Server (Traditional)
```bash
cd searxng-mcp-crawl
python server.py
```

Server runs at `http://localhost:32769`

## 🔧 Available Tools

### 1. search_web (Enhanced)
```json
{
  "name": "search_web",
  "arguments": {
    "query": "머신러닝 튜토리얼",
    "limit": 10,
    "category": "general"
  }
}
```

**Categories:**
- `general` - Web pages with full content (default)
- `images` - Image search
- `videos` - Video search
- `files` - File search
- `map` - Location search
- `social media` - Social media search

### 2. get_website (Enhanced)
```json
{
  "name": "get_website",
  "arguments": {
    "url": "https://example.com",
    "max_length": 10000,
    "use_cache": true
  }
}
```

**Features:**
- PDF auto-detection and conversion
- Caching for performance
- Reddit URL conversion
- Clean text extraction

### 3. get_current_datetime (NEW)
```json
{
  "name": "get_current_datetime",
  "arguments": {}
}
```

Returns current date/time in configured timezone.

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   cd searxng-mcp-crawl
   pip install -r requirements.txt
   ```

2. **Make sure SearXNG is running:**
   ```bash
   curl http://localhost:32768/search?q=test&format=json
   ```

3. **Choose your mode:**
   - **JSON Block**: Add configuration to your MCP client
   - **HTTP Server**: Run `python server.py`

## 📚 Documentation

- **README.md**: Complete English documentation
- **README_KR.md**: 한국어 문서
- **examples/**: Sample configurations
  - `claude_desktop_config.json`
  - `cline_mcp_settings.json`
  - `.env.example`

## ✅ Testing Results

All functionality tested and working:
- ✅ Stdio server communication (JSON-RPC)
- ✅ Plugin loading (8 plugins)
- ✅ Tool listing
- ✅ Tool execution
- ✅ Logging to stderr
- ✅ JSON-RPC on stdout (clean)

## 🎯 Key Improvements

| Feature | Before | After |
|---------|--------|-------|
| Search Categories | General only | 6 categories |
| PDF Support | ❌ | ✅ Markdown conversion |
| Caching | ❌ | ✅ TTL cache |
| Rate Limiting | ❌ | ✅ Domain-based |
| Content Extraction | Basic | Trafilatura |
| MCP Client Support | Docker only | JSON block |
| Reddit Scraping | Limited | old.reddit.com |

## 🔌 Plugin System

Your server still has all original plugins plus new enhanced ones:
- `search_web` - Enhanced search (NEW)
- `get_website` - Enhanced crawl (NEW)
- `get_current_datetime` - Datetime tool (NEW)
- `search` - Original search (Legacy)
- `fetch_webpage` - Original crawl (Legacy)
- `runLLM` - AI access
- `executor` - Tool executor
- `tool_planner` - Task planner

## 🛠️ Configuration

### Environment Variables

```bash
# SearXNG
SEARXNG_BASE_URL=http://localhost:32768

# HTTP Server
HOST=0.0.0.0
PORT=32769

# Content
CONTENT_MAX_LENGTH=10000
SEARCH_RESULT_LIMIT=10

# Timezone
DESIRED_TIMEZONE=Asia/Seoul  # or America/New_York, UTC, etc.
```

### Cache Settings (in code)
- `cache_maxsize`: 100 entries
- `cache_ttl_minutes`: 5 minutes
- `cache_max_age_minutes`: 30 minutes

### Rate Limit Settings (in code)
- `rate_limit_requests_per_minute`: 10
- `rate_limit_timeout_seconds`: 60

## 🙏 Credits

Enhanced features integrated from:
- [OvertliDS/mcp-searxng-enhanced](https://github.com/OvertliDS/mcp-searxng-enhanced)
- [SearXNG](https://github.com/searxng/searxng)
- [Trafilatura](https://github.com/adbar/trafilatura)
- [PyMuPDF](https://pymupdf.readthedocs.io/)

## 📝 Next Steps

1. **Try it out**: Add the JSON configuration to your MCP client
2. **Test searches**: Try different categories (images, videos, etc.)
3. **Test PDFs**: Try fetching a PDF URL with get_website
4. **Check caching**: Request the same URL twice and see performance improvement
5. **Adjust settings**: Modify cache and rate limit settings as needed

## 💡 Tips

- Use **search_web** for general web searches with full content extraction
- Use **images** category for image searches
- Use **get_website** to fetch specific URLs (supports PDFs!)
- Use **get_current_datetime** for timezone-aware timestamps
- The cache significantly improves performance for repeated requests
- Rate limiting prevents IP blocking from target websites

## 🎊 Enjoy your enhanced SearXNG MCP server!

If you have any questions or issues, check the README files or open an issue on GitHub.
