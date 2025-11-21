from plugin_base import MCPPlugin
from typing import Dict, Any, List
from crawler import WebCrawler
import asyncio


class SearchPlugin(MCPPlugin):
    """
    Advanced Web Search Plugin with SearXNG - High Performance Edition

    Features:
    - High volume search (up to 60 results)
    - Parallel batch processing for speed
    - Customizable result limit
    - Search categories (general, news, images, etc.)
    - Language filtering
    - Time range filtering
    - Safe search toggle
    - 🔥 CAPTCHA detection and retry
    """

    def __init__(self):
        try:
            self.crawler = WebCrawler()
            print("   🔍 SearchPlugin: Crawler initialized")
        except Exception as e:
            print(f"   ⚠️ SearchPlugin: Crawler init error: {e}")
            self.crawler = None

    @property
    def name(self) -> str:
        return "search"

    @property
    def description(self) -> str:
        return "High-performance web search via SearXNG. Params: query, limit=10 (max: 60), category=general."

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "limit": {"type": "integer", "default": 10},
                "category": {"type": "string", "default": "general"},
            },
            "required": ["query"],
        }

    @property
    def version(self) -> str:
        return "3.0.1"  # 🔥 CAPTCHA retry version

    @property
    def author(self) -> str:
        return "damin25soka7"

    async def search_batch(
        self,
        query: str,
        batch_size: int,
        category: str,
        language: str,
        time_range: str,
        safe_search: int,
        batch_num: int,
        total_batches: int,
    ) -> Dict[str, Any]:
        """Search a single batch in parallel"""
        try:
            print(
                f"      📦 Batch {batch_num}/{total_batches}: Fetching {batch_size} results..."
            )

            results = await self.crawler.search_searxng(
                query=query,
                limit=batch_size,
                category=category,
                language=language,
                time_range=time_range,
                safe_search=safe_search,
            )

            if isinstance(results, dict):
                if results.get("success") is False:
                    print(
                        f"      ❌ Batch {batch_num} failed: {results.get('error', 'Unknown')}"
                    )
                    return {
                        "success": False,
                        "results": [],
                        "error": results.get("error"),
                    }

                result_list = results.get("results", [])
            elif isinstance(results, list):
                result_list = results
            else:
                result_list = []

            print(f"      ✅ Batch {batch_num}: {len(result_list)} results")
            return {"success": True, "results": result_list}

        except Exception as e:
            print(f"      ❌ Batch {batch_num} error: {str(e)[:50]}")
            return {"success": False, "results": [], "error": str(e)}

    async def search_parallel(
        self,
        query: str,
        limit: int,
        category: str,
        language: str,
        time_range: str,
        safe_search: int,
    ) -> List[Dict[str, Any]]:
        """
        Search with parallel batch processing for high volume

        Splits large searches into batches and runs them concurrently
        """
        # SearXNG typically returns ~10 results per page
        # For 60 results, we need 6 batches of 10
        batch_size = 10
        num_batches = (limit + batch_size - 1) // batch_size

        print(f"\n   🚀 Parallel Search Mode")
        print(f"   🎯 Target: {limit} results")
        print(f"   📦 Batches: {num_batches} × {batch_size} results")
        print(f"   {'='*50}")

        # Create batch tasks
        tasks = []
        for i in range(num_batches):
            batch_limit = min(batch_size, limit - (i * batch_size))
            if batch_limit > 0:
                task = self.search_batch(
                    query,
                    batch_limit,
                    category,
                    language,
                    time_range,
                    safe_search,
                    i + 1,
                    num_batches,
                )
                tasks.append(task)

        # Execute all batches in parallel
        import time

        start_time = time.time()

        batch_results = await asyncio.gather(*tasks)

        elapsed = time.time() - start_time

        # Combine results from all batches
        all_results = []
        successful_batches = 0
        failed_batches = 0

        for batch_result in batch_results:
            if batch_result.get("success"):
                all_results.extend(batch_result.get("results", []))
                successful_batches += 1
            else:
                failed_batches += 1

        print(f"   {'='*50}")
        print(f"   ⏱️ Parallel execution: {elapsed:.2f}s")
        print(f"   ✅ Successful batches: {successful_batches}/{num_batches}")
        if failed_batches > 0:
            print(f"   ⚠️ Failed batches: {failed_batches}/{num_batches}")
        print(f"   📊 Total unique results: {len(all_results)}")

        return all_results

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute high-performance web search with parallel processing

        Args:
            query: Search query string
            limit: Number of results (1-60, default: 10)
            category: Search category (default: general)
            language: Language preference (default: auto)
            time_range: Filter by time (default: none)
            safe_search: Safe search level (default: 1)

        Returns:
            {
                "success": bool,
                "query": str,
                "results_count": int,
                "results": [...],
                "parameters": {...},
                "performance": {...}
            }
        """
        query = arguments.get("query", "").strip()
        limit = arguments.get("limit", 10)
        category = arguments.get("category", "general")
        language = arguments.get("language", "auto")
        time_range = arguments.get("time_range", "")
        safe_search = arguments.get("safe_search", 1)

        # Validation
        if not query:
            return {
                "success": False,
                "error": "Query parameter is required and cannot be empty",
                "query": "",
                "results_count": 0,
            }

        # Clamp limit to valid range (now supports up to 60)
        limit = max(1, min(60, limit))

        print(f"\n🔍 search v3.0.1 (High-Performance + CAPTCHA Retry)")
        print(f"   Query: '{query}'")
        print(f"   Limit: {limit} results")
        print(f"   Category: {category}")
        if language != "auto":
            print(f"   Language: {language}")
        if time_range:
            print(f"   Time range: {time_range}")

        import time

        start_time = time.time()

        try:
            # Use parallel search for large requests (>15 results)
            if limit > 15:
                result_list = await self.search_parallel(
                    query, limit, category, language, time_range, safe_search
                )
            else:
                # Single request for small searches
                print(f"\n   🔍 Single Search Mode")

                # 🔥 First attempt with original settings
                results = await self.crawler.search_searxng(
                    query=query,
                    limit=limit,
                    category=category,
                    language=language,
                    time_range=time_range,
                    safe_search=safe_search,
                )

                # Check if results were successful
                if isinstance(results, dict) and results.get("success") is False:
                    error_msg = results.get("error", "Unknown error")
                    print(f"   ⚠️ First attempt failed: {error_msg}")

                    # 🔥 CAPTCHA detected? Try with different language (avoid kr-kr)
                    if "captcha" in error_msg.lower() or "kl" in error_msg.lower():
                        print(
                            f"   🔄 CAPTCHA detected, retrying with language='en-US'..."
                        )

                        # Retry with English to avoid regional blocks
                        results = await self.crawler.search_searxng(
                            query=query,
                            limit=limit,
                            category=category,
                            language="en-US",  # 🔥 Force English
                            time_range=time_range,
                            safe_search=safe_search,
                        )

                        if (
                            isinstance(results, dict)
                            and results.get("success") is False
                        ):
                            error_msg = results.get("error", "Unknown error")
                            print(f"   ❌ Retry also failed: {error_msg}")

                            # 🔥 Return structured error with query info
                            return {
                                "success": False,
                                "error": f"Search blocked by CAPTCHA: {error_msg}",
                                "query": query,
                                "results_count": 0,
                                "results": [],
                                "parameters": {
                                    "limit": limit,
                                    "category": category,
                                    "language": language,
                                    "time_range": time_range,
                                    "safe_search": safe_search,
                                },
                                "captcha_blocked": True,
                            }
                        else:
                            print(f"   ✅ Retry succeeded with en-US!")
                    else:
                        # Non-CAPTCHA error
                        return {
                            "success": False,
                            "error": error_msg,
                            "query": query,
                            "results_count": 0,
                            "results": [],
                            "parameters": {
                                "limit": limit,
                                "category": category,
                                "language": language,
                                "time_range": time_range,
                                "safe_search": safe_search,
                            },
                        }

                # Extract result list
                result_list = (
                    results if isinstance(results, list) else results.get("results", [])
                )

            elapsed_time = time.time() - start_time
            result_count = len(result_list)

            # Remove duplicates by URL
            unique_results = []
            seen_urls = set()
            for result in result_list:
                url = result.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    unique_results.append(result)

            unique_count = len(unique_results)

            # 🔥 Zero result warning
            if unique_count == 0:
                print(f"\n   {'⚠️'*25}")
                print(f"   ⚠️ ZERO RESULTS WARNING")
                print(f"   📊 Query: '{query}'")
                print(f"   💡 No results found - possible CAPTCHA or blocking")
                print(f"   {'⚠️'*25}\n")

            print(f"\n   {'='*50}")
            print(f"   {'✅' if unique_count > 0 else '⚠️'} Search Complete!")
            print(f"   📊 Raw results: {result_count}")
            print(f"   🎯 Unique results: {unique_count}")
            print(f"   ⏱️ Total time: {elapsed_time:.2f}s")
            if unique_count > 0 and elapsed_time > 0:
                print(f"   🚀 Speed: {unique_count/elapsed_time:.1f} results/sec")
            print(f"   {'='*50}\n")

            return {
                "success": True,
                "query": query,
                "results_count": unique_count,
                "results": unique_results[:limit],  # Trim to exact limit
                "parameters": {
                    "limit": limit,
                    "category": category,
                    "language": language,
                    "time_range": time_range,
                    "safe_search": safe_search,
                },
                "performance": {
                    "total_time_seconds": round(elapsed_time, 2),
                    "results_per_second": (
                        round(unique_count / elapsed_time, 2)
                        if elapsed_time > 0 and unique_count > 0
                        else 0
                    ),
                    "raw_results": result_count,
                    "duplicates_removed": result_count - unique_count,
                    "parallel_mode": limit > 15,
                },
                "zero_results_warning": unique_count == 0,
            }

        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            print(f"   ❌ Error: {error_msg}")

            return {
                "success": False,
                "error": error_msg,
                "query": query,
                "results_count": 0,
                "results": [],
            }
