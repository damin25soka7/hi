"""
Shared API Configuration - Module Level
모든 플러그인이 import해서 사용
"""

# 🔥 모듈 레벨 변수 (클래스 아님!)
_SHARED_CUSTOM_APIS = {}
_SHARED_PLUGIN_MAPPINGS = {}
_SHARED_DEFAULT_API = "customAPI1"


def configure_shared_apis(config):
    """Configure shared API settings"""
    global _SHARED_CUSTOM_APIS, _SHARED_PLUGIN_MAPPINGS, _SHARED_DEFAULT_API
    
    _SHARED_CUSTOM_APIS = {}
    
    apis = config.get("apis", {})
    for api_name, api_config in apis.items():
        if not api_name.startswith("customAPI"):
            continue
        
        url = api_config.get("url", "").strip()
        api_key = api_config.get("apiKey", "").strip()
        model = api_config.get("model", "").strip()
        
        if url and api_key and model:
            _SHARED_CUSTOM_APIS[api_name] = {
                "url": url,
                "apiKey": api_key,
                "model": model,
                "name": api_name,
            }
    
    _SHARED_PLUGIN_MAPPINGS = config.get("plugin_mappings", {})
    _SHARED_DEFAULT_API = config.get("default", "customAPI1")
    
    print(f"🌐 Shared API Config: {len(_SHARED_CUSTOM_APIS)} APIs")


def get_shared_api_for_plugin(plugin_name):
    """Get API config for plugin"""
    if not _SHARED_CUSTOM_APIS:
        return None
    
    # Try specific mapping
    api_name = _SHARED_PLUGIN_MAPPINGS.get(plugin_name)
    if api_name and api_name in _SHARED_CUSTOM_APIS:
        print(f"   🔑 {plugin_name} → {api_name}")
        return _SHARED_CUSTOM_APIS[api_name]
    
    # Fallback to default
    if _SHARED_DEFAULT_API and _SHARED_DEFAULT_API in _SHARED_CUSTOM_APIS:
        print(f"   🔑 {plugin_name} → {_SHARED_DEFAULT_API} (default)")
        return _SHARED_CUSTOM_APIS[_SHARED_DEFAULT_API]
    
    return None