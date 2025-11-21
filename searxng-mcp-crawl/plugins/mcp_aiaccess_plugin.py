from plugin_base import MCPPlugin
from typing import Dict, Any, List
import httpx
import json


class MCPAIAccessPlugin(MCPPlugin):
    """
    Advanced AI Access Plugin - Direct LLM call with Research Mode v4.0

    Features:
    - Standard mode: 2000 max_tokens output
    - Research mode: 5000 max_tokens output (auto-detected or explicit)
    - Supports large input: up to 15000 tokens
    - 🔥 NEW: Shared customAPI configuration support
    - Automatic fallback to default API
    """

    # Class-level storage for shared API configurations
    _custom_apis = {}
    _plugin_mappings = {}
    _default_api = None

    @property
    def name(self) -> str:
        return "runLLM"

    @property
    def description(self) -> str:
        return "Execute LLM API call. Params: messages, research_mode (optional)."

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Optional: Direct API URL. If not provided, uses shared customAPI.",
                },
                "apiKey": {
                    "type": "string",
                    "description": "Optional: Direct API key. If not provided, uses shared customAPI.",
                },
                "model": {
                    "type": "string",
                    "description": "Optional: Direct model name. If not provided, uses shared customAPI.",
                },
                "messages": {"type": "array", "items": {"type": "object"}},
                "research_mode": {
                    "type": "boolean",
                    "default": False,
                    "description": "Enable research mode (5K output). Auto-detected if not specified.",
                },
            },
            "required": ["messages"],
        }

    @property
    def version(self) -> str:
        return "4.0.0"

    @property
    def author(self) -> str:
        return "damin25soka7"

    @classmethod
    def configure_apis(cls, config: Dict[str, Any]):
        """
        Configure shared customAPI settings

        Expected format:
        {
            "apis": {
                "customAPI1": {"url": "...", "apiKey": "...", "model": "..."},
                "customAPI2": {...},
                ...
            },
            "plugin_mappings": {
                "runLLM": "customAPI1",
                "tool_planner": "customAPI2",
                ...
            },
            "default": "customAPI1"
        }
        """
        cls._custom_apis = {}

        apis = config.get("apis", {})
        for api_name, api_config in apis.items():
            if not api_name.startswith("customAPI"):
                continue

            url = api_config.get("url", "").strip()
            api_key = api_config.get("apiKey", "").strip()
            model = api_config.get("model", "").strip()

            if url and api_key and model:
                cls._custom_apis[api_name] = {
                    "url": url,
                    "apiKey": api_key,
                    "model": model,
                    "name": api_name,
                }

        cls._plugin_mappings = config.get("plugin_mappings", {})
        cls._default_api = config.get("default", "customAPI1")

        if cls._default_api not in cls._custom_apis and cls._custom_apis:
            cls._default_api = list(cls._custom_apis.keys())[0]

        print(f"   💾 Configured {len(cls._custom_apis)} custom APIs for runLLM")
        if cls._default_api:
            print(f"   🎯 Default: {cls._default_api}")

    @classmethod
    def get_api_for_plugin(cls, plugin_name: str) -> Optional[Dict[str, Any]]:
        """Get API configuration for a plugin"""
        if not cls._custom_apis:
            return None

        # Try plugin-specific mapping
        api_name = cls._plugin_mappings.get(plugin_name)
        if api_name and api_name in cls._custom_apis:
            return cls._custom_apis[api_name]

        # Fallback to default
        if cls._default_api and cls._default_api in cls._custom_apis:
            return cls._custom_apis[cls._default_api]

        return None

    def detect_research_mode(self, messages: List[Dict[str, Any]]) -> bool:
        """Auto-detect research mode from messages"""
        research_keywords = [
            "research",
            "comprehensive",
            "detailed analysis",
            "in-depth",
            "thorough",
            "extensive",
            "complete analysis",
            "full report",
        ]

        total_content_length = 0

        for msg in messages:
            content = msg.get("content", "").lower()
            total_content_length += len(content)

            for keyword in research_keywords:
                if keyword in content:
                    return True

        if total_content_length > 30000:
            return True

        return False

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute LLM API call with adaptive token limits"""

        url_direct = arguments.get("url", "").strip()
        api_key_direct = arguments.get("apiKey", "").strip()
        model_direct = arguments.get("model", "").strip()

        if url_direct and api_key_direct and model_direct:
            print("   ℹ️ Using direct API credentials")
            url = url_direct
            api_key = api_key_direct
            model = model_direct
            api_name = "direct"
        else:
            print("   ℹ️ Using shared customAPI config")

            api_config = self.get_api_for_plugin("runLLM")

            if not api_config:
                return {
                    "success": False,
                    "message": "No API configured for runLLM",
                    "hint": "Provide url/apiKey/model or configure customAPIs via configure_apis()",
                }

            url = api_config["url"]
            api_key = api_config["apiKey"]
            model = api_config["model"]
            api_name = api_config.get("name", "unknown")
            print(f"   ✅ Using {api_name}")

        messages = arguments.get("messages", [])
        research_mode_explicit = arguments.get("research_mode", False)

        if not messages or not isinstance(messages, list):
            return {
                "success": False,
                "message": "Invalid messages: must be non-empty array",
            }

        for i, msg in enumerate(messages):
            if not isinstance(msg, dict):
                return {"success": False, "message": f"Message {i} must be an object"}
            if "role" not in msg or "content" not in msg:
                return {
                    "success": False,
                    "message": f"Message {i} missing role or content",
                }
            if msg["role"] not in ["user", "assistant", "system"]:
                return {
                    "success": False,
                    "message": f'Message {i} invalid role: {msg["role"]}',
                }

        research_mode_auto = self.detect_research_mode(messages)
        research_mode = research_mode_explicit or research_mode_auto

        if research_mode:
            max_tokens = 5000
            temperature = 0.3
            mode_label = "🔬 RESEARCH MODE"
            mode_reason = "explicit" if research_mode_explicit else "auto-detected"
        else:
            max_tokens = 2000
            temperature = 0.7
            mode_label = "💬 STANDARD MODE"
            mode_reason = "default"

        total_input_chars = sum(len(msg.get("content", "")) for msg in messages)
        estimated_input_tokens = total_input_chars // 4

        print(f"\n{'='*70}")
        print(f"🤖 runLLM v4.0 {mode_label}")
        print(f"API: {api_name}")
        print(f"Model: {model}")
        print(f"Messages: {len(messages)}")
        print(f"Input: ~{estimated_input_tokens:,} tokens")
        print(f"Output limit: {max_tokens:,} tokens")
        print(f"Research mode: {research_mode} ({mode_reason})")
        print(f"{'='*70}")

        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            }

            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }

            async with httpx.AsyncClient(timeout=180.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()

                if "choices" in data and len(data["choices"]) > 0:
                    content = data["choices"][0]["message"]["content"]
                    usage = data.get("usage", {})

                    total_tokens = usage.get("total_tokens", 0)
                    prompt_tokens = usage.get("prompt_tokens", 0)
                    completion_tokens = usage.get("completion_tokens", 0)

                    print(f"\n✅ Success!")
                    print(f"   Output: {len(content):,} chars")
                    print(f"\n   📊 Token Usage:")
                    print(f"   ┌─────────────────────────────────┐")
                    print(f"   │ Input:    {prompt_tokens:>6,} / 15,000 │")
                    print(
                        f"   │ Output:   {completion_tokens:>6,} / {max_tokens:>6,} │"
                    )
                    print(f"   │ Total:    {total_tokens:>6,}         │")
                    print(f"   └─────────────────────────────────┘")

                    if prompt_tokens > 13500:
                        print(f"   ⚠️ Input near limit ({prompt_tokens:,}/15,000)")
                    if completion_tokens > max_tokens * 0.9:
                        print(
                            f"   ⚠️ Output near limit ({completion_tokens:,}/{max_tokens:,})"
                        )

                    print(f"{'='*70}\n")

                    return {
                        "success": True,
                        "message": content,
                        "model_used": model,
                        "api_used": api_name,
                        "tokens": {
                            "total": total_tokens,
                            "input": prompt_tokens,
                            "output": completion_tokens,
                            "input_limit": 15000,
                            "output_limit": max_tokens,
                        },
                        "research_mode": research_mode,
                    }

                elif "content" in data:
                    content = data["content"]
                    print(f"\n✅ Success ({len(content):,} chars)")
                    print(f"{'='*70}\n")

                    return {
                        "success": True,
                        "message": content,
                        "model_used": model,
                        "api_used": api_name,
                        "research_mode": research_mode,
                    }

                else:
                    raise ValueError(
                        f"Unexpected API response format: {list(data.keys())}"
                    )

        except httpx.HTTPStatusError as e:
            error_text = e.response.text[:500]
            error_msg = f"HTTP {e.response.status_code}: {error_text}"
            print(f"❌ API Error: {error_msg}")
            print(f"{'='*70}\n")

            return {
                "success": False,
                "message": error_msg,
                "status_code": e.response.status_code,
            }

        except httpx.TimeoutException:
            error_msg = "Request timeout (180s)"
            print(f"❌ {error_msg}")
            print(f"{'='*70}\n")

            return {"success": False, "message": error_msg}

        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            print(f"❌ Error: {error_msg}")
            print(f"{'='*70}\n")

            return {"success": False, "message": error_msg}
