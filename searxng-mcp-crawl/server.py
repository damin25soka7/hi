from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import StreamingResponse, JSONResponse
import json
import uvicorn
import asyncio
from uuid import uuid4
from plugin_manager import PluginManager
import config

print("=" * 60)
print("🚀 Extensible MCP Server with Plugin System")
print("=" * 60)
print(f"Server: http://{config.HOST}:{config.PORT}")
print("=" * 60)

# 플러그인 매니저 초기화
plugin_manager = PluginManager(plugins_dir="plugins")
active_connections = {}

async def startup():
    print("✅ Server ready")

async def shutdown():
    print("👋 Bye")

async def handle_mcp(msg):
    method = msg.get("method")
    msg_id = msg.get("id")
    params = msg.get("params", {})
    
    print(f"📨 {method}")
    
    # Initialize
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "extensible-mcp-server",
                    "version": "2.0.0"
                }
            }
        }
    
    # Initialized notification
    elif method == "notifications/initialized":
        return None
    
    # List tools (자동으로 플러그인 목록 반환)
    elif method == "tools/list":
        tools = plugin_manager.list_plugins()
        print(f"   → {len(tools)} tools from plugins")
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {"tools": tools}
        }
    
    # Call tool (플러그인 자동 실행)
    elif method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        print(f"   🔧 {tool_name}: {arguments}")
        
        # 플러그인 실행
        result = await plugin_manager.execute_plugin(tool_name, arguments)
        
        # JSON 문자열로 변환
        result_text = json.dumps(result, indent=2, ensure_ascii=False)
        
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "content": [{"type": "text", "text": result_text}]
            }
        }
    
    # Ping
    elif method == "ping":
        return {"jsonrpc": "2.0", "id": msg_id, "result": {}}
    
    # Reload plugins (특수 메서드)
    elif method == "plugins/reload":
        plugin_manager.reload_plugins()
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {"message": "Plugins reloaded", "count": len(plugin_manager.plugins)}
        }
    
    return {
        "jsonrpc": "2.0",
        "id": msg_id,
        "error": {"code": -32601, "message": f"Unknown method: {method}"}
    }

# SSE 엔드포인트
async def sse_connect(request):
    cid = str(uuid4())
    
    async def stream():
        yield f"event: endpoint\ndata: /message/{cid}\n\n"
        q = asyncio.Queue()
        active_connections[cid] = q
        try:
            while True:
                m = await q.get()
                if m is None: break
                yield f"data: {json.dumps(m)}\n\n"
        finally:
            active_connections.pop(cid, None)
    
    return StreamingResponse(stream(), media_type="text/event-stream")

async def message_handler(request):
    cid = request.path_params["connection_id"]
    body = await request.body()
    msg = json.loads(body)
    resp = await handle_mcp(msg)
    if resp and cid in active_connections:
        await active_connections[cid].put(resp)
    return JSONResponse({"ok": 1})

async def post_handler(request):
    body = await request.body()
    msg = json.loads(body)
    resp = await handle_mcp(msg)
    return JSONResponse(resp) if resp else JSONResponse({"ok": 1})

async def health(request):
    return JSONResponse({
        "status": "ok",
        "plugins": len(plugin_manager.plugins),
        "available_tools": list(plugin_manager.plugins.keys())
    })

app = Starlette(
    routes=[
        Route('/', post_handler, methods=['POST']),
        Route('/', sse_connect, methods=['GET']),
        Route('/message/{connection_id}', message_handler, methods=['POST']),
        Route('/health', health, methods=['GET']),
    ],
    on_startup=[startup],
    on_shutdown=[shutdown]
)

if __name__ == "__main__":
    uvicorn.run(app, host=config.HOST, port=config.PORT)