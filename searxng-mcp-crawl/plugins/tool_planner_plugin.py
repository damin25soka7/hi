from plugin_base import MCPPlugin
from typing import Dict, Any, List, Optional
import httpx
import json
import asyncio
import re


class ToolPlannerPlugin(MCPPlugin):
    """
    Advanced Tool Planner v8.5.3 - Multilingual Backup Keywords

    Features:
    - 🔥 Executes: ANY data-gathering tools (search, fetch_webpage, etc.)
    - 🔥 Plans: ANY LLM tools (runLLM, etc.) for executor
    - 🔥 Multilingual backup keywords (Korean→English, English→Japanese, etc.)
    - 🔥 Recovery limited to 1 attempt (prevents information pollution)
    - 🔥 Smart executor message (only when LLM steps + content exist)
    - Flexible plan patterns
    - Detailed analysis mode
    - Executor-ready output
    """

    def __init__(self):
        self.plugin_manager = None
        self._search_failure_count = {}
        self.MAX_SEARCH_RETRIES = 3

        # 🔥 Tool categories
        self.DATA_GATHERING_TOOLS = [
            "search",
            "fetch_webpage",
            "web_scraper",
            "api_call",
        ]
        self.LLM_TOOLS = ["runLLM", "analyze", "summarize", "generate"]

    @property
    def name(self) -> str:
        return "tool_planner"

    @property
    def description(self) -> str:
        return "Universal planner: executes data tools, prepares LLM tools for executor. Multilingual backup keywords."

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "user_query": {"type": "string"},
                "planner_llm_config": {
                    "type": "object",
                    "description": "API config for planner",
                    "properties": {
                        "url": {"type": "string"},
                        "apiKey": {"type": "string"},
                        "model": {"type": "string"},
                    },
                },
                "max_steps": {"type": "integer", "default": 10},
                "exact_steps": {"type": "integer"},
                "complexity": {
                    "type": "string",
                    "enum": ["simple", "moderate", "detailed"],
                    "default": "detailed",
                },
                "execute_plan": {"type": "boolean", "default": True},
                "enable_auto_recovery": {"type": "boolean", "default": True},
                "show_detailed_preview": {"type": "boolean", "default": False},
            },
            "required": ["user_query"],
        }

    @property
    def version(self) -> str:
        return "8.5.3"

    @property
    def author(self) -> str:
        return "damin25soka7"

    def set_plugin_manager(self, plugin_manager):
        self.plugin_manager = plugin_manager

    def get_available_tools(self) -> List[Dict[str, str]]:
        if not self.plugin_manager:
            return []
        try:
            tools = self.plugin_manager.list_plugins()
            return [t for t in tools if t["name"] not in ["tool_planner", "executor"]]
        except:
            return []

    def is_data_gathering_tool(self, tool_name: str) -> bool:
        """Check if tool is for data gathering"""
        return tool_name in self.DATA_GATHERING_TOOLS

    def is_llm_tool(self, tool_name: str) -> bool:
        """Check if tool is LLM-based"""
        return tool_name in self.LLM_TOOLS

    async def call_planner_llm(self, messages: List[Dict], config: Dict) -> str:
        """Call planner LLM with 403 error retry"""
        url = config.get("url", "").strip()
        api_key = config.get("apiKey", "").strip()
        model = config.get("model", "").strip()

        if not all([url, api_key, model]):
            raise ValueError("Planner LLM config incomplete")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 2000,
        }

        print(f"   🤖 Using model: {model}")

        for attempt in range(1, 4):
            try:
                print(f"   📡 API call attempt {attempt}/3...")

                async with httpx.AsyncClient(timeout=120.0) as client:
                    response = await client.post(url, headers=headers, json=payload)

                    if response.status_code in [403, 429, 503]:
                        error_text = response.text[:200]
                        wait_time = attempt * 3

                        print(f"   ⚠️ HTTP {response.status_code}: {error_text}")

                        if attempt < 3:
                            print(f"   ⏳ Waiting {wait_time}s before retry...")
                            await asyncio.sleep(wait_time)
                            continue
                        else:
                            raise httpx.HTTPStatusError(
                                f"HTTP {response.status_code} after 3 attempts",
                                request=response.request,
                                response=response,
                            )

                    response.raise_for_status()
                    data = response.json()

                    if "choices" in data and len(data["choices"]) > 0:
                        content = data["choices"][0]["message"]["content"]
                        print(f"   ✅ API call successful (attempt {attempt})")
                        return content
                    elif "content" in data:
                        content = data["content"]
                        print(f"   ✅ API call successful (attempt {attempt})")
                        return content
                    else:
                        raise ValueError(f"Unexpected response format")

            except httpx.HTTPStatusError as e:
                if e.response.status_code in [403, 429, 503] and attempt < 3:
                    continue
                raise

            except httpx.TimeoutException:
                if attempt < 3:
                    await asyncio.sleep(attempt * 2)
                    continue
                raise

            except Exception:
                if attempt < 3:
                    await asyncio.sleep(attempt * 2)
                    continue
                raise

        raise Exception("Failed to get planner LLM response after 3 attempts")

    def clean_json_response(self, response: str) -> str:
        response_clean = response.strip()

        if response_clean.startswith("```"):
            lines = response_clean.split("\n")
            if lines[0].strip().lower() in ["```json", "```"]:
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            response_clean = "\n".join(lines)

        response_clean = response_clean.strip()

        if not response_clean.startswith("{"):
            json_start = response_clean.find("{")
            if json_start != -1:
                response_clean = response_clean[json_start:]

        if not response_clean.endswith("}"):
            json_end = response_clean.rfind("}")
            if json_end != -1:
                response_clean = response_clean[: json_end + 1]

        response_clean = re.sub(r"//.*?\n", "\n", response_clean)
        response_clean = re.sub(r"/\*.*?\*/", "", response_clean, flags=re.DOTALL)
        response_clean = re.sub(r",(\s*[}\]])", r"\1", response_clean)

        return response_clean

    async def execute_tool_step(
        self, tool_name: str, args: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute any tool"""

        if not self.plugin_manager:
            return {"success": False, "error": "Plugin manager N/A"}

        try:
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
                return {"success": False, "error": "Cannot execute tool"}

            return result

        except Exception as e:
            return {"success": False, "error": str(e)}

    def detect_language(self, text: str) -> str:
        """Detect primary language of text"""
        # Check for Korean characters (Hangul)
        korean_chars = sum(1 for c in text if 0xAC00 <= ord(c) <= 0xD7A3)

        # Check for Japanese characters (Hiragana, Katakana, Kanji)
        japanese_chars = sum(
            1
            for c in text
            if (0x3040 <= ord(c) <= 0x309F)  # Hiragana
            or (0x30A0 <= ord(c) <= 0x30FF)  # Katakana
            or (0x4E00 <= ord(c) <= 0x9FFF)  # Kanji
        )

        # Check for Chinese characters
        chinese_chars = sum(1 for c in text if 0x4E00 <= ord(c) <= 0x9FFF)

        total_chars = len(text)

        if korean_chars > total_chars * 0.3:
            return "korean"
        elif japanese_chars > total_chars * 0.3:
            return "japanese"
        elif chinese_chars > total_chars * 0.3:
            return "chinese"
        else:
            return "english"

    def generate_multilingual_backup(self, original_query: str) -> str:
        """
        🔥 Generate backup keyword in DIFFERENT language

        Strategy:
        - Korean → English translation
        - English → Japanese/Korean
        - Japanese → English
        - Chinese → English
        """

        print(f"   🌍 Generating multilingual backup...")
        print(f"      Original: {original_query}")

        lang = self.detect_language(original_query)
        print(f"      Detected language: {lang}")

        # Simple keyword mapping for common topics
        korean_to_english = {
            "보잉": "Boeing",
            "항공기": "aircraft",
            "비행기": "airplane",
            "여객기": "passenger aircraft",
            "787": "787",
            "777": "777",
            "드림라이너": "Dreamliner",
            "특징": "features",
            "성능": "performance",
            "사양": "specifications",
            "기술": "technology",
            "분석": "analysis",
            "정보": "information",
            "최신": "latest",
        }

        english_to_japanese = {
            "Boeing": "ボーイング",
            "aircraft": "航空機",
            "airplane": "飛行機",
            "features": "特徴",
            "performance": "性能",
            "specifications": "仕様",
            "technology": "技術",
            "analysis": "分析",
            "latest": "最新",
            "Python": "パイソン",
            "programming": "プログラミング",
        }

        backup = original_query

        if lang == "korean":
            # Korean → English
            words = original_query.split()
            translated_words = []
            for word in words:
                # Try to translate known words
                translated = False
                for ko, en in korean_to_english.items():
                    if ko in word:
                        translated_words.append(en)
                        translated = True
                        break
                if not translated:
                    # Keep original for unknown words
                    translated_words.append(word)

            if translated_words:
                backup = " ".join(translated_words)
            else:
                backup = f"{original_query} in English"

        elif lang == "english":
            # English → Japanese (or Korean as fallback)
            words = original_query.split()
            translated_words = []
            for word in words:
                translated = False
                for en, ja in english_to_japanese.items():
                    if en.lower() in word.lower():
                        translated_words.append(ja)
                        translated = True
                        break
                if not translated:
                    translated_words.append(word)

            if any(ord(c) > 127 for c in "".join(translated_words)):
                backup = " ".join(translated_words)
            else:
                # Fallback: add "日本語" or keep English with modifier
                backup = f"{original_query} detailed"

        elif lang == "japanese":
            # Japanese → English (simple approach)
            backup = f"{original_query} English version"

        elif lang == "chinese":
            # Chinese → English
            backup = f"{original_query} English"

        print(f"      ✅ Backup ({lang}→multilingual): {backup}")
        return backup

    async def execute_data_gathering_steps(
        self,
        plan: List[Dict[str, Any]],
        planner_llm_config: Dict,
        enable_recovery: bool,
    ) -> Dict[str, Any]:
        """Execute all data-gathering steps (flexible pattern)"""

        print(f"\n{'🚀'*35}")
        print(f"   🚀 EXECUTING DATA GATHERING STEPS")
        print(f"   {'🚀'*35}\n")

        results = {}
        last_search_result = None
        original_search_query = None
        backup_search_query = None  # 🔥 Pre-generated multilingual backup
        recovery_attempted = False

        for step in plan:
            tool_name = step.get("tool")

            # Skip LLM tools (will be handled by executor)
            if self.is_llm_tool(tool_name):
                continue

            print(f"\n   ▶️ Step {step.get('step')}: {tool_name}")
            args = step.get("arguments", {}).copy()

            # 🔥 Auto-inject URLs from previous search
            if tool_name == "fetch_webpage" and last_search_result:
                if "urls" not in args and "results" in last_search_result:
                    args["urls"] = [
                        item.get("url")
                        for item in last_search_result.get("results", [])
                        if item.get("url")
                    ]
                    print(
                        f"      📎 Auto-injected {len(args['urls'])} URLs from search"
                    )

            # 🔥 Track search query and generate multilingual backup
            if tool_name == "search":
                original_search_query = args.get("query", "")

                # Generate multilingual backup keyword immediately
                if not backup_search_query:
                    backup_search_query = self.generate_multilingual_backup(
                        original_search_query
                    )

            # Execute
            result = await self.execute_tool_step(tool_name, args)
            results[tool_name] = result

            # Store for next step
            if tool_name == "search":
                last_search_result = result

            print(f"   ✅ {tool_name} done")

            # 🔥 Auto-recovery for fetch_webpage shortage (1회 제한!)
            if (
                tool_name == "fetch_webpage"
                and enable_recovery
                and not recovery_attempted
            ):
                shortage_info = result.get("shortage_info", {})

                if shortage_info.get("shortage_detected"):
                    shortage = shortage_info.get("shortage", 0)

                    print(f"\n   {'⚠️'*25}")
                    print(f"   ⚠️ SHORTAGE DETECTED: {shortage} URLs needed")
                    print(f"   🔧 Starting recovery (1st attempt)...")
                    print(f"   {'='*50}")

                    recovery_attempted = True  # 🔥 Mark as attempted

                    if backup_search_query:
                        print(f"\n   ▶️ Recovery: search (multilingual)")
                        print(f"      🌍 Using backup query: {backup_search_query}")

                        # 🔥 Use pre-generated multilingual backup keyword!
                        recovery_search_result = await self.execute_tool_step(
                            "search",
                            {"query": backup_search_query, "limit": shortage * 5},
                        )
                        print(f"   ✅ Recovery search done")

                        if (
                            recovery_search_result.get("success")
                            and "results" in recovery_search_result
                        ):
                            print(f"\n   ▶️ Recovery: fetch_webpage")

                            recovery_urls = [
                                item.get("url")
                                for item in recovery_search_result["results"]
                                if item.get("url")
                            ]
                            print(f"      📎 Using {len(recovery_urls)} recovery URLs")

                            rec_fetch = await self.execute_tool_step(
                                "fetch_webpage",
                                {"urls": recovery_urls, "limit": shortage},
                            )
                            print(f"   ✅ Recovery fetch done")

                            # Check if recovery was successful
                            if not rec_fetch.get("shortage_info", {}).get(
                                "shortage_detected"
                            ):
                                print(f"\n   {'✅'*25}")
                                print(f"   ✅ RECOVERY SUCCESS!")
                                print(f"   {'✅'*25}\n")
                            else:
                                shortage_after = rec_fetch.get("shortage_info", {}).get(
                                    "shortage", 0
                                )
                                print(f"\n   {'⚠️'*25}")
                                print(
                                    f"   ⚠️ Still {shortage_after} short after recovery"
                                )
                                print(f"   ℹ️ Recovery limit reached (1/1 attempts)")
                                print(f"   {'⚠️'*25}\n")

                    else:
                        print(f"   ⚠️ No backup query available")

                elif shortage_info.get("shortage", 0) == 0:
                    print(f"   ✅ All requested articles fetched successfully")

        print(f"\n{'🏁'*35}")
        print(f"   🏁 DATA GATHERING COMPLETE")
        if recovery_attempted:
            print(f"   ℹ️ Recovery was attempted (1/1)")
        print(f"   {'🏁'*35}\n")

        return {
            "success": True,
            "results": results,
            "recovery_attempted": recovery_attempted,
            "backup_query_used": backup_search_query if recovery_attempted else None,
        }

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        user_query = arguments.get("user_query", "").strip()
        execute_plan = arguments.get("execute_plan", True)
        enable_recovery = arguments.get("enable_auto_recovery", True)

        planner_llm_config = arguments.get("planner_llm_config")

        if not planner_llm_config:
            return {
                "success": False,
                "error": "planner_llm_config required (url, apiKey, model)",
            }

        exact_steps = arguments.get("exact_steps")
        max_steps = arguments.get("max_steps", 10)
        complexity = arguments.get("complexity", "detailed")

        if not user_query:
            return {"success": False, "error": "user_query required"}

        required_steps = exact_steps or max_steps

        print(f"\n{'='*70}")
        print(f"🧠 TOOL PLANNER v8.5.3 (Multilingual Backup Keywords)")
        print(f"Query: {user_query}")
        print(f"Model: {planner_llm_config.get('model', 'N/A')}")
        print(f"Max steps: {required_steps}")
        print(f"Complexity: {complexity}")
        print(f"{'='*70}")

        available_tools = self.get_available_tools()
        tools_text = "\n".join(
            [f"- {t['name']}: {t.get('description', 'N/A')}" for t in available_tools]
        )

        complexity_instructions = {
            "simple": "Use minimal steps, focus on key information only.",
            "moderate": "Balanced approach, gather sufficient information.",
            "detailed": "COMPREHENSIVE ANALYSIS. Gather extensive information. LLM must provide detailed, in-depth analysis with specific examples, data, and thorough explanations. NO SUMMARIZATION.",
        }

        planning_prompt = f"""Create execution plan for: "{user_query}"

Available Tools:
{tools_text}

Complexity: {complexity} - {complexity_instructions.get(complexity)}

📊 TOOL GUIDELINES:

1. search:
   - query: search query (string)
   - limit: number of results (10-60)
   - Use 3x buffer: need 30 articles → limit=90

2. fetch_webpage:
   - limit: articles to fetch (3-30)
   - DO NOT include urls (auto-injected from search)

3. runLLM:
   - messages: conversation array
   - research_mode: boolean (true for detailed analysis)
   - DO NOT include url/apiKey/model (executor provides)
   
   🔥 IMPORTANT for runLLM messages:
   - Use {{{{FETCHED_CONTENT}}}} placeholder for fetched data
   - Request DETAILED, COMPREHENSIVE analysis
   - Specify: "Provide in-depth analysis with specific details, examples, and thorough explanations. Do NOT summarize."

🎯 PLAN PATTERNS (flexible, choose best for query):

Pattern A (Data + Analysis):
  1. search
  2. fetch_webpage
  3. runLLM (detailed analysis)

Pattern B (Multiple Data Sources):
  1. search (topic A)
  2. fetch_webpage
  3. search (topic B)
  4. fetch_webpage
  5. runLLM (combined analysis)

Pattern C (Direct LLM):
  1. runLLM (if no data gathering needed)

Return JSON:
{{
  "main_query": "concise description",
  "plan": [
    {{
      "step": 1,
      "tool": "tool_name",
      "arguments": {{...}},
      "purpose": "why this step",
      "expected_output": "what it produces"
    }}
  ],
  "total_steps": {required_steps}
}}
"""

        try:
            response = await self.call_planner_llm(
                [
                    {
                        "role": "system",
                        "content": f"Expert task planner. Create flexible, optimal plan. Up to {required_steps} steps. Return ONLY valid JSON.",
                    },
                    {"role": "user", "content": planning_prompt},
                ],
                planner_llm_config,
            )

            response_clean = self.clean_json_response(response)
            plan_data = json.loads(response_clean)

            plan = plan_data.get("plan", [])

            if not plan:
                return {"success": False, "error": "Empty plan generated"}

            # Clean parameters
            for step in plan:
                tool_name = step.get("tool")
                args = step.get("arguments", {})

                if tool_name == "search" and "limit" not in args:
                    args["limit"] = 30

                elif tool_name == "fetch_webpage":
                    if "limit" not in args:
                        args["limit"] = 10
                    # Remove unwanted params
                    for unwanted in ["max_length", "urls"]:
                        if unwanted in args:
                            del args[unwanted]

                elif self.is_llm_tool(tool_name):
                    # Remove API params (executor handles)
                    for unwanted in ["url", "apiKey", "model", "max_tokens"]:
                        if unwanted in args:
                            del args[unwanted]

            print(f"\n   📋 Plan: {len(plan)} steps")
            for step in plan:
                tool_name = step.get("tool")
                is_llm = self.is_llm_tool(tool_name)
                marker = "📋" if is_llm else "🔧"
                print(f"      {marker} Step {step['step']}: {tool_name}")

            response_data = {
                "success": True,
                "mode": "universal_executor",
                "main_query": plan_data.get("main_query", user_query),
                "plan": plan,
                "total_steps": len(plan),
                "planner_version": "8.5.3",
                "planner_model_used": planner_llm_config.get("model", "N/A"),
            }

            # Execute data gathering steps
            if execute_plan:
                execution_result = await self.execute_data_gathering_steps(
                    plan, planner_llm_config, enable_recovery
                )

                response_data["execution_result"] = execution_result

                # 🔥 Prepare LLM steps for executor
                llm_steps = [s for s in plan if self.is_llm_tool(s.get("tool"))]

                if llm_steps and execution_result.get("success"):
                    # Collect all fetched content
                    all_fetched_content = []

                    for tool_name, result in execution_result.get(
                        "results", {}
                    ).items():
                        if tool_name == "fetch_webpage" and result.get("results"):
                            for r in result["results"]:
                                if r.get("success"):
                                    url = r.get("url", "N/A")
                                    content = r.get("content", "")
                                    all_fetched_content.append(
                                        f"[Source: {url}]\n{content}"
                                    )

                    # 🔥 Only prepare executor if content was actually fetched
                    if all_fetched_content:
                        combined_content = "\n\n---\n\n".join(all_fetched_content)

                        print(f"\n   📊 Content Stats:")
                        print(f"      Total size: {len(combined_content):,} chars")
                        print(f"      Documents: {len(all_fetched_content)}")

                        # Prepare each LLM step for executor
                        for llm_step in llm_steps:
                            llm_tool_name = llm_step.get("tool")
                            llm_args = llm_step.get("arguments", {}).copy()

                            # Replace {{FETCHED_CONTENT}} placeholder
                            if "messages" in llm_args:
                                for msg in llm_args["messages"]:
                                    if "content" in msg and isinstance(
                                        msg["content"], str
                                    ):
                                        msg["content"] = msg["content"].replace(
                                            "{{FETCHED_CONTENT}}", combined_content
                                        )

                            # 🔥 Enhanced executor_ready with clear instructions
                            response_data["executor_ready"] = {
                                "ready": True,
                                "status": "data_gathering_complete",
                                "next_action": "call_executor_plugin",
                                "instruction": f"⚠️ CRITICAL: Use 'executor' plugin to run '{llm_tool_name}'. DO NOT call tool_planner again.",
                                "why": "Data gathering is complete. Executor will inject API credentials and execute final analysis.",
                                "executor_call": {
                                    "action": "execute",
                                    "tool_name": llm_tool_name,
                                    "arguments": llm_args,
                                    "inject_api": True,
                                },
                                "content_stats": {
                                    "total_size": len(combined_content),
                                    "documents": len(all_fetched_content),
                                },
                                "warning": "⚠️ Calling tool_planner again will duplicate the data gathering process!",
                            }

                            # Add next_action at root level
                            response_data["next_action"] = {
                                "required": True,
                                "plugin": "executor",
                                "action": "execute",
                                "tool": llm_tool_name,
                                "description": f"Execute {llm_tool_name} with fetched content",
                            }

                            break  # Use first LLM step
                    else:
                        # LLM steps exist but no content was fetched
                        print(f"\n   ⚠️ LLM steps planned but no content was fetched.")

            print(f"\n{'='*70}")
            print("✅ PLANNING & EXECUTION COMPLETE")
            print(f"   Model: {planner_llm_config.get('model')}")

            # 🔥 Only show executor instructions if executor_ready exists and has content
            if "executor_ready" in response_data and response_data.get(
                "executor_ready", {}
            ).get("ready"):
                stats = response_data["executor_ready"]["content_stats"]
                tool_name = response_data["executor_ready"]["executor_call"][
                    "tool_name"
                ]

                print(f"\n   {'🎯'*35}")
                print(f"   🎯 NEXT ACTION REQUIRED")
                print(f"   {'🎯'*35}")
                print(f"   ⚠️ DO NOT call tool_planner again!")
                print(f"   ✅ Call executor plugin:")
                print(f"      - action: 'execute'")
                print(f"      - tool_name: '{tool_name}'")
                print(f"      - Content ready: {stats['total_size']:,} chars")
                print(f"   {'🎯'*35}")

                # Summary message
                response_data["summary"] = (
                    f"✅ Data gathering complete: {stats['documents']} documents fetched, "
                    f"{stats['total_size']:,} characters. "
                    f"⚠️ NEXT: Call executor(action='execute', tool_name='{tool_name}') "
                    f"to perform final analysis. DO NOT call tool_planner again!"
                )
            else:
                # No executor needed
                print(f"\n   ✅ All steps complete. No further action needed.")
                response_data["summary"] = (
                    "✅ All steps complete. No further action needed."
                )

            print(f"{'='*70}\n")

            return response_data

        except Exception as e:
            import traceback

            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "planner_model_used": planner_llm_config.get("model", "N/A"),
            }
