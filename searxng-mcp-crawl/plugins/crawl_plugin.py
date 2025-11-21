from plugin_base import MCPPlugin
from typing import Dict, Any, List
from crawler import WebCrawler
import asyncio
import time


class CrawlPlugin(MCPPlugin):
    """
    Advanced Web Crawling Plugin v3.4.1

    Features:
    - Smart content validation (min 100 chars)
    - Enhanced smart retry with backup URLs
    - 🔥 Auto-chunking threshold: 30KB (30,000 chars)
    - Parallel batch processing
    - Shortage detection and reporting
    """

    def __init__(self):
        try:
            self.crawler = WebCrawler()
            print("   🕷️ CrawlPlugin: Crawler initialized")
        except Exception as e:
            print(f"   ⚠️ CrawlPlugin: Crawler init error: {e}")
            self.crawler = None

    @property
    def name(self) -> str:
        return "fetch_webpage"

    @property
    def description(self) -> str:
        return "Fetch webpage content with smart retry. Params: urls, limit=10. Auto-chunks if total >30KB."

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {"type": "string"},
                "urls": {"type": "array", "items": {"type": "string"}},
                "limit": {"type": "integer", "default": 10},
                "max_length": {"type": "integer", "default": 20000},
            },
        }

    @property
    def version(self) -> str:
        return "3.4.1"

    @property
    def author(self) -> str:
        return "damin25soka7"

    def validate_url(self, url: str) -> bool:
        if not isinstance(url, str):
            return False
        return url.startswith(("http://", "https://"))

    def validate_content(self, content: str, min_chars: int = 100) -> bool:
        if not content or len(content) < min_chars:
            return False

        error_patterns = [
            "woops",
            "oops",
            "404",
            "not found",
            "page not found",
            "access denied",
            "forbidden",
        ]
        content_lower = content.lower()

        for pattern in error_patterns:
            if pattern in content_lower and len(content) < 500:
                return False

        return True

    def _chunk_text(
        self, text: str, chunk_size: int, overlap: int
    ) -> List[Dict[str, Any]]:
        chunks = []
        text_length = len(text)

        if text_length == 0:
            return chunks

        if chunk_size <= 0:
            chunk_size = 15000  # 15KB per chunk

        if overlap >= chunk_size:
            overlap = chunk_size // 4

        if overlap < 0:
            overlap = 0

        start = 0
        chunk_num = 1
        max_chunks = 100

        print(f"\n   {'✂️'*25}")
        print(f"   ✂️ AUTO-CHUNKING ACTIVATED")
        print(f"   📏 Total: {text_length:,} chars ({text_length/1000:.1f}KB)")
        print(f"   📦 Chunk: {chunk_size:,} chars ({chunk_size/1000:.1f}KB)")
        print(f"   🔗 Overlap: {overlap:,} chars")
        print(f"   {'='*50}")

        while start < text_length and chunk_num <= max_chunks:
            end = min(start + chunk_size, text_length)
            chunk_content = text[start:end]

            chunks.append(
                {
                    "chunk_number": chunk_num,
                    "content": chunk_content,
                    "start_pos": start,
                    "end_pos": end,
                    "length": len(chunk_content),
                }
            )

            progress = (end / text_length) * 100
            bar_length = 30
            filled = int(bar_length * end / text_length)
            bar = "█" * filled + "░" * (bar_length - filled)

            print(
                f"   [{bar}] {progress:.1f}% - Chunk {chunk_num}: {len(chunk_content):,} chars"
            )

            if end >= text_length:
                break

            next_start = end - overlap

            if next_start <= start:
                next_start = start + max(1, chunk_size // 2)

            start = next_start
            chunk_num += 1

        print(f"   {'='*50}")
        print(f"   ✅ Created {len(chunks)} chunks")
        print(
            f"   📊 Avg size: {sum(c['length'] for c in chunks) // len(chunks):,} chars"
        )
        print(f"   {'✂️'*25}\n")

        return chunks

    async def fetch_single_url(
        self,
        url: str,
        max_length: int,
        include_metadata: bool,
        timeout: int,
        index: int = 0,
    ) -> Dict[str, Any]:
        try:
            print(f"      [{index}] Fetching: {url[:60]}...")

            result = await self.crawler.fetch_webpage(
                url=url, max_length=max_length, timeout=timeout
            )

            if isinstance(result, dict):
                if result.get("success") or "content" in result:
                    content = result.get("content", "")
                    content_length = len(content)

                    if not self.validate_content(content):
                        print(f"      [{index}] ⚠️ Invalid ({content_length} chars)")
                        return {
                            "success": False,
                            "url": url,
                            "error": f"Content too short ({content_length} chars)",
                            "content_length": content_length,
                        }

                    print(
                        f"      [{index}] ✅ Success ({content_length:,} chars = {content_length/1000:.1f}KB)"
                    )

                    response = {
                        "success": True,
                        "url": url,
                        "content": content,
                        "content_length": content_length,
                    }

                    if include_metadata:
                        response["metadata"] = {
                            "title": result.get("title", ""),
                            "description": result.get("description", ""),
                            "language": result.get("language", ""),
                            "word_count": len(content.split()),
                        }

                    return response
                else:
                    print(
                        f"      [{index}] ❌ Failed: {result.get('error', 'Unknown')}"
                    )
                    return {
                        "success": False,
                        "url": url,
                        "error": result.get("error", "Unknown error"),
                    }

            return {"success": False, "url": url, "error": "Invalid response"}

        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            print(f"      [{index}] ❌ Exception: {error_msg}")
            return {"success": False, "url": url, "error": error_msg}

    async def fetch_batch(
        self,
        urls: List[str],
        max_length: int,
        include_metadata: bool,
        timeout: int,
        batch_size: int,
    ) -> List[Dict[str, Any]]:
        all_results = []

        for i in range(0, len(urls), batch_size):
            batch = urls[i : i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(urls) + batch_size - 1) // batch_size

            print(f"   📦 Batch {batch_num}/{total_batches}: {len(batch)} URLs")

            tasks = [
                self.fetch_single_url(
                    url, max_length, include_metadata, timeout, i + idx + 1
                )
                for idx, url in enumerate(batch)
            ]

            batch_results = await asyncio.gather(*tasks)
            all_results.extend(batch_results)

            if i + batch_size < len(urls):
                await asyncio.sleep(0.5)

        return all_results

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        single_url = arguments.get("url", "").strip()
        url_list = arguments.get("urls", [])
        limit = arguments.get("limit", 10)
        max_length = arguments.get("max_length", 20000)
        include_metadata = arguments.get("include_metadata", True)
        timeout = arguments.get("timeout", 30)
        batch_size = arguments.get("batch_size", 10)

        # 🔥 청킹 기준: 30KB (30,000 chars)
        auto_chunk = arguments.get("auto_chunk", True)
        chunk_threshold = arguments.get("chunk_threshold", 30000)  # 🔥 30KB
        chunk_size = arguments.get("chunk_size", 15000)  # 15KB per chunk
        chunk_overlap = arguments.get("chunk_overlap", 1000)  # 1KB overlap

        if not single_url and not url_list:
            return {"success": False, "error": "Either 'url' or 'urls' required"}

        if single_url and url_list:
            return {
                "success": False,
                "error": "Provide either 'url' or 'urls', not both",
            }

        is_direct_call = bool(single_url)

        if single_url:
            if not self.validate_url(single_url):
                return {"success": False, "error": f"Invalid URL: {single_url}"}
            urls_to_fetch = [single_url]
            backup_urls = []
        else:
            valid_urls = [url for url in url_list if self.validate_url(url)]
            invalid_urls = [url for url in url_list if not self.validate_url(url)]

            if invalid_urls:
                print(f"   ⚠️ Skipping {len(invalid_urls)} invalid URLs")

            if not valid_urls:
                return {"success": False, "error": "No valid URLs"}

            urls_to_fetch = valid_urls[:limit]
            backup_urls = valid_urls[limit:] if len(valid_urls) > limit else []

        limit = max(1, min(30, limit))
        max_length = max(100, min(50000, max_length))
        timeout = max(5, min(120, timeout))
        batch_size = max(1, min(20, batch_size))

        print(f"\n🕷️ fetch_webpage v3.4.1")
        print(f"   URLs: {len(urls_to_fetch)}")
        print(f"   Max length: {max_length:,} chars ({max_length/1000:.1f}KB)")
        print(f"   Backup URLs: {len(backup_urls)}")
        print(
            f"   🔥 Chunk threshold: {chunk_threshold:,} chars ({chunk_threshold/1000:.0f}KB)"
        )
        print(f"   Direct call: {is_direct_call}")

        start_time = time.time()

        if len(urls_to_fetch) == 1:
            results = [
                await self.fetch_single_url(
                    urls_to_fetch[0], max_length, include_metadata, timeout, 1
                )
            ]
        else:
            results = await self.fetch_batch(
                urls_to_fetch, max_length, include_metadata, timeout, batch_size
            )

        shortage_info = None

        # Smart Retry (only if NOT direct call)
        if not is_direct_call:
            target_count = limit
            current_success = sum(1 for r in results if r.get("success"))

            if current_success < target_count:
                shortage = target_count - current_success

                print(f"\n   {'🔄'*25}")
                print(f"   🔄 SMART RETRY")
                print(f"   📊 Current: {current_success}/{target_count}")
                print(f"   🔁 Need: {shortage} more")
                print(f"   📦 Backup: {len(backup_urls)}")
                print(f"   {'='*50}")

                # Strategy 1: Backup URLs
                if backup_urls:
                    retry_urls = backup_urls[: shortage * 2]
                    print(f"   🚀 Using {len(retry_urls)} backup URLs")

                    retry_results = await self.fetch_batch(
                        retry_urls, max_length, include_metadata, timeout, batch_size
                    )

                    for r in retry_results:
                        if r.get("success") and self.validate_content(
                            r.get("content", "")
                        ):
                            results.append(r)
                            current_success += 1
                            print(f"      ✅ Backup: {r['url'][:60]}")
                            if current_success >= target_count:
                                break

                    print(f"   📊 After backup: {current_success}/{target_count}")

                # Strategy 2: Retry failed
                if current_success < target_count:
                    print(f"\n   🔄 Retrying failed URLs")

                    failed_urls = [r["url"] for r in results if not r.get("success")]

                    if failed_urls:
                        remaining = target_count - current_success
                        retry_urls = failed_urls[: remaining * 2]

                        print(f"   🔁 Retrying {len(retry_urls)} URLs")
                        await asyncio.sleep(3)

                        retry_results = await self.fetch_batch(
                            retry_urls,
                            max_length,
                            include_metadata,
                            timeout,
                            batch_size,
                        )

                        for r in retry_results:
                            if r.get("success") and self.validate_content(
                                r.get("content", "")
                            ):
                                for i, orig in enumerate(results):
                                    if orig["url"] == r["url"] and not orig.get(
                                        "success"
                                    ):
                                        results[i] = r
                                        current_success += 1
                                        print(f"      ✅ Recovered: {r['url'][:60]}")
                                        break
                                if current_success >= target_count:
                                    break

                # Final status
                if current_success < target_count:
                    final_shortage = target_count - current_success
                    print(f"\n   {'⚠️'*25}")
                    print(f"   ⚠️ SHORTAGE: {final_shortage} URLs")
                    print(f"   💡 Need more URLs from search")
                    print(f"   💡 Increase search limit to {target_count * 3}")
                    print(f"   {'⚠️'*25}\n")

                    shortage_info = {
                        "shortage_detected": True,
                        "requested": target_count,
                        "achieved": current_success,
                        "shortage": final_shortage,
                        "recommendation": f"Increase search limit to {target_count * 3} or use different keywords",
                    }
                else:
                    print(
                        f"\n   ✅ TARGET ACHIEVED: {current_success}/{target_count}\n"
                    )
                    shortage_info = {
                        "shortage_detected": False,
                        "requested": target_count,
                        "achieved": current_success,
                    }

        successful = sum(1 for r in results if r.get("success"))
        failed = len(results) - successful
        total_content_size = sum(
            r.get("content_length", 0) for r in results if r.get("success")
        )
        elapsed_time = time.time() - start_time

        chunked = False
        chunk_info = None

        # 🔥 청킹 기준: 30KB (30,000 chars)
        if auto_chunk and total_content_size > chunk_threshold:
            print(f"\n   {'🔥'*25}")
            print(f"   🔥 CHUNKING TRIGGERED!")
            print(
                f"   📊 Total: {total_content_size:,} chars ({total_content_size/1000:.1f}KB)"
            )
            print(
                f"   📊 Threshold: {chunk_threshold:,} chars ({chunk_threshold/1000:.0f}KB)"
            )
            print(f"   ✅ Total > Threshold: {total_content_size > chunk_threshold}")
            print(f"   {'🔥'*25}")

            combined_content = "\n\n---PAGE SEPARATOR---\n\n".join(
                [
                    f"[Source: {r['url']}]\n{r.get('content', '')}"
                    for r in results
                    if r.get("success")
                ]
            )

            chunks = self._chunk_text(combined_content, chunk_size, chunk_overlap)
            chunked = True

            chunk_info = {
                "total_chunks": len(chunks),
                "avg_chunk_size": (
                    sum(c["length"] for c in chunks) // len(chunks) if chunks else 0
                ),
                "total_original_size": total_content_size,
                "chunk_threshold": chunk_threshold,
                "chunk_size_setting": chunk_size,
                "triggered_because": f"Total content ({total_content_size:,} chars) exceeded threshold ({chunk_threshold:,} chars)",
            }

            self._cached_chunks = chunks
        else:
            if total_content_size > 0:
                print(f"\n   ✅ No chunking needed")
                print(
                    f"   📊 Total: {total_content_size:,} chars ({total_content_size/1000:.1f}KB)"
                )
                print(
                    f"   📊 Threshold: {chunk_threshold:,} chars ({chunk_threshold/1000:.0f}KB)"
                )
                print(f"   ✅ Total < Threshold\n")

        response = {
            "success": True,
            "total_urls": len(results),
            "successful": successful,
            "failed": failed,
            "results": results,
            "total_content_size": total_content_size,
            "chunked": chunked,
            "performance": {
                "total_time_seconds": round(elapsed_time, 2),
                "avg_time_per_url": (
                    round(elapsed_time / len(results), 2) if results else 0
                ),
            },
            "parameters": {
                "max_length": max_length,
                "timeout": timeout,
                "chunk_threshold": chunk_threshold,
                "auto_chunk_enabled": auto_chunk,
            },
            "validation": {
                "min_content_chars": 100,
                "retry_enabled": not is_direct_call,
            },
        }

        if shortage_info:
            response["shortage_info"] = shortage_info

        if chunked and chunk_info:
            response["chunk_info"] = chunk_info

        return response
