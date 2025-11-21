from plugin_base import MCPPlugin
from typing import Dict, Any, List, Optional
import json


class ExecutorPlugin(MCPPlugin):
    """
    Universal Tool Executor v1.3

    Features:
    - Stores API credentials for all tools
    - Auto-injects API keys when executing tools
    - 🔥 NEW: Rejects ONLY search/fetch_webpage (handled by tool_planner)
    - 🔥 Executes runLLM and all other tools normally
    - 🔥 Plugin chaining (execute multiple tools sequentially)
    - 🔥 Data passing between plugins
    - Passes through data (e.g., fetched content) seamlessly
    - Compatible with any plugin
    - Centralized API management
    """

    # Class-level API storage
    _api_credentials: Dict[str, Dict[str, Any]] = {}
    _tool_api_mappings: Dict[str, str] = {}
    _default_api: str = "api1"

    def __init__(self):
        self.plugin_manager = None

    @property
    def name(self) -> str:
        return "executor"

    @property
    def description(self) -> str:
        return "Execute tools with API injection. Rejects ONLY search/fetch_webpage. Supports all other tools including runLLM."

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["configure", "execute", "chain", "status"],
                    "description": "Action to perform",
                },
                # Configure action
                "api_credentials": {
                    "type": "object",
                    "description": "API credentials to store (for configure action)",
                },
                "tool_api_mappings": {
                    "type": "object",
                    "description": "Tool -> API name mappings (for configure action)",
                },
                "default_api": {
                    "type": "string",
                    "description": "Default API name (for configure action)",
                },
                # Execute action
                "tool_name": {
                    "type": "string",
                    "description": "Tool to execute (for execute action)",
                },
                "arguments": {
                    "type": "object",
                    "description": "Arguments for the tool (for execute action)",
                },
                "passthrough_data": {
                    "type": "object",
                    "description": "Additional data to pass through (for execute action)",
                },
                "inject_api": {
                    "type": "boolean",
                    "default": True,
                    "description": "Whether to inject API credentials",
                },
                # Chain action
                "chain": {
                    "type": "array",
                    "description": "List of tools to execute sequentially (for chain action)",
                    "items": {
                        "type": "object",
                        "properties": {
                            "tool_name": {"type": "string"},
                            "arguments": {"type": "object"},
                            "inject_api": {"type": "boolean", "default": True},
                            "pass_result_to_next": {
                                "type": "boolean",
                                "default": False,
                            },
                            "result_key": {
                                "type": "string",
                                "description": "Key to store result for next tool",
                            },
                        },
                        "required": ["tool_name"],
                    },
                },
            },
            "required": ["action"],
        }

    @property
    def version(self) -> str:
        return "1.3.0"

    @property
    def author(self) -> str:
        return "damin25soka7"

    def set_plugin_manager(self, plugin_manager):
        self.plugin_manager = plugin_manager

    @classmethod
    def configure_credentials(cls, config: Dict[str, Any]):
        """Configure API credentials"""
        cls._api_credentials = config.get("api_credentials", {})
        cls._tool_api_mappings = config.get("tool_api_mappings", {})
        cls._default_api = config.get("default_api", "api1")

        print(f"\n{'='*70}")
        print(f"🔧 EXECUTOR v1.3 - API Credentials Configured")
        print(f"{'='*70}")
        print(f"   APIs: {len(cls._api_credentials)}")
        for api_name in cls._api_credentials.keys():
            print(f"      ✅ {api_name}")
        print(f"\n   Tool Mappings:")
        for tool, api in cls._tool_api_mappings.items():
            print(f"      {tool} → {api}")
        print(f"\n   Default: {cls._default_api}")
        print(f"{'='*70}\n")

    @classmethod
    def get_api_for_tool(cls, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get API credentials for a specific tool"""

        # Try specific mapping
        api_name = cls._tool_api_mappings.get(tool_name)
        if api_name and api_name in cls._api_credentials:
            return cls._api_credentials[api_name]

        # Fallback to default
        if cls._default_api and cls._default_api in cls._api_credentials:
            return cls._api_credentials[cls._default_api]

        return None

    async def execute_single_tool(
        self,
        tool_name: str,
        tool_arguments: Dict[str, Any],
        inject_api: bool = True,
        passthrough_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute a single tool with API injection"""

        if not self.plugin_manager:
            return {"success": False, "error": "Plugin manager not available"}

        # 🔥 Reject ONLY search and fetch_webpage
        if tool_name == "search":
            print(f"\n   🚫 REJECTED: search")
            print(f"      ⚠️ search should be handled by tool_planner, not executor!")
            return {
                "success": False,
                "error": "Tool 'search' cannot be executed by executor",
                "reason": "search should be handled by tool_planner directly",
                "suggestion": "Use tool_planner to execute search",
            }

        if tool_name == "fetch_webpage":
            print(f"\n   🚫 REJECTED: fetch_webpage")
            print(
                f"      ⚠️ fetch_webpage should be handled by tool_planner, not executor!"
            )
            return {
                "success": False,
                "error": "Tool 'fetch_webpage' cannot be executed by executor",
                "reason": "fetch_webpage should be handled by tool_planner directly",
                "suggestion": "Use tool_planner to execute fetch_webpage",
            }

        print(f"\n   ▶️ Executing: {tool_name}")

        # Make copy to avoid modifying original
        args = tool_arguments.copy()

        # 🔥 API 주입
        api_used = None
        if inject_api:
            api_config = self.get_api_for_tool(tool_name)

            if api_config:
                api_used = self._tool_api_mappings.get(tool_name, self._default_api)
                print(f"      🔑 API: {api_used}")

                # API 파라미터가 없을 때만 주입
                if "url" not in args:
                    args["url"] = api_config.get("url")
                if "apiKey" not in args:
                    args["apiKey"] = api_config.get("apiKey")
                if "model" not in args:
                    args["model"] = api_config.get("model")

                print(f"      📱 Model: {args.get('model', 'N/A')}")

        # 🔥 Passthrough data 병합
        if passthrough_data:
            print(f"      📦 Passthrough: {len(passthrough_data)} keys")
            for key, value in passthrough_data.items():
                if key not in args:
                    args[key] = value

        # 실행
        try:
            result = None

            if hasattr(self.plugin_manager, "call_tool"):
                result = await self.plugin_manager.call_tool(tool_name, args)
            elif hasattr(self.plugin_manager, "plugins"):
                plugin = self.plugin_manager.plugins.get(tool_name)
                if plugin:
                    result = await plugin.execute(args)
                else:
                    return {
                        "success": False,
                        "error": f"Plugin '{tool_name}' not found",
                    }
            else:
                return {
                    "success": False,
                    "error": "Cannot execute tool",
                }

            print(f"      ✅ Done")

            return {
                "success": True,
                "tool_name": tool_name,
                "api_used": api_used,
                "result": (
                    result
                    if result is not None
                    else {"success": False, "error": "No result"}
                ),
            }

        except Exception as e:
            print(f"      ❌ Failed: {e}")
            return {
                "success": False,
                "tool_name": tool_name,
                "error": str(e),
            }

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute action"""

        action = arguments.get("action", "").lower()

        # ============================================================
        # ACTION: configure
        # ============================================================
        if action == "configure":
            api_credentials = arguments.get("api_credentials", {})
            tool_api_mappings = arguments.get("tool_api_mappings", {})
            default_api = arguments.get("default_api", "api1")

            if not api_credentials:
                return {
                    "success": False,
                    "error": "api_credentials required for configure action",
                }

            config = {
                "api_credentials": api_credentials,
                "tool_api_mappings": tool_api_mappings,
                "default_api": default_api,
            }

            self.configure_credentials(config)

            return {
                "success": True,
                "message": "API credentials configured successfully",
                "apis_count": len(api_credentials),
                "api_names": list(api_credentials.keys()),
                "tool_mappings": tool_api_mappings,
                "default_api": default_api,
            }

        # ============================================================
        # ACTION: status
        # ============================================================
        elif action == "status":
            return {
                "success": True,
                "configured": len(self._api_credentials) > 0,
                "apis_count": len(self._api_credentials),
                "api_names": list(self._api_credentials.keys()),
                "tool_mappings": self._tool_api_mappings,
                "default_api": self._default_api,
            }

        # ============================================================
        # ACTION: execute (single tool)
        # ============================================================
        elif action == "execute":
            tool_name = arguments.get("tool_name", "").strip()
            tool_arguments = arguments.get("arguments", {})
            passthrough_data = arguments.get("passthrough_data", {})
            inject_api = arguments.get("inject_api", True)

            if not tool_name:
                return {
                    "success": False,
                    "error": "tool_name required for execute action",
                }

            print(f"\n{'🚀'*35}")
            print(f"   🚀 EXECUTOR v1.3 - Single Execution")
            print(f"   {'🚀'*35}")

            result = await self.execute_single_tool(
                tool_name, tool_arguments, inject_api, passthrough_data
            )

            print(f"   {'🚀'*35}\n")

            return result

        # ============================================================
        # ACTION: chain (multiple tools)
        # ============================================================
        elif action == "chain":
            chain = arguments.get("chain", [])

            if not chain:
                return {
                    "success": False,
                    "error": "chain array required for chain action",
                }

            print(f"\n{'🔗'*35}")
            print(f"   🔗 EXECUTOR v1.3 - Plugin Chain")
            print(f"   {'🔗'*35}")
            print(f"   Steps: {len(chain)}")

            results = []
            shared_data = {}  # Data shared between steps

            for idx, step in enumerate(chain, 1):
                tool_name = step.get("tool_name", "").strip()
                tool_arguments = step.get("arguments", {}).copy()
                inject_api = step.get("inject_api", True)
                pass_result_to_next = step.get("pass_result_to_next", False)
                result_key = step.get("result_key", f"step_{idx}_result")

                if not tool_name:
                    error_result = {
                        "success": False,
                        "step": idx,
                        "error": "tool_name missing",
                    }
                    results.append(error_result)
                    continue

                print(f"\n   📌 Step {idx}/{len(chain)}: {tool_name}")

                # 🔥 Check if it's search or fetch_webpage
                if tool_name == "search" or tool_name == "fetch_webpage":
                    print(f"      🚫 SKIPPED: {tool_name} (use tool_planner)")
                    error_result = {
                        "success": False,
                        "step": idx,
                        "tool_name": tool_name,
                        "error": f"{tool_name} should be handled by tool_planner",
                    }
                    results.append(error_result)
                    continue

                # 🔥 Merge shared data from previous steps
                if shared_data:
                    print(f"      📥 Shared data: {list(shared_data.keys())}")
                    for key, value in shared_data.items():
                        if key not in tool_arguments:
                            tool_arguments[key] = value

                # Execute
                result = await self.execute_single_tool(
                    tool_name, tool_arguments, inject_api, None
                )

                results.append(
                    {
                        "step": idx,
                        "tool_name": tool_name,
                        "success": result.get("success", False),
                        "result": result,
                    }
                )

                # 🔥 Pass result to next step if requested
                if pass_result_to_next and result.get("success"):
                    shared_data[result_key] = result.get("result")
                    print(f"      📤 Saved to shared_data['{result_key}']")

                # Stop chain if step failed
                if not result.get("success"):
                    print(f"\n   ❌ Chain stopped at step {idx} due to failure")
                    break

            print(f"\n   {'🔗'*35}")
            print(f"   ✅ Chain complete: {len(results)}/{len(chain)} steps executed")
            print(f"   {'🔗'*35}\n")

            return {
                "success": True,
                "action": "chain",
                "total_steps": len(chain),
                "executed_steps": len(results),
                "results": results,
                "shared_data_keys": list(shared_data.keys()),
            }

        # ============================================================
        # INVALID ACTION
        # ============================================================
        else:
            return {
                "success": False,
                "error": f"Invalid action: '{action}'",
                "valid_actions": ["configure", "execute", "chain", "status"],
            }
