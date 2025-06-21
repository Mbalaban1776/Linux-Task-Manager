import psutil

def bytes_to_gb(b):
    return b / (1000**3)

def bytes_to_mb(b):
    return b / (1000**2)

def get_static_memory_info():
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    return {
        "total_gb": f"{bytes_to_gb(mem.total):.1f} GB",
        "commit_total_gb": bytes_to_gb(mem.total + swap.total)
    }

_dynamic_info_cache = {}

def update_dynamic_memory_info():
    global _dynamic_info_cache
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()

    used_mem = mem.total - mem.available

    _dynamic_info_cache = {
        "In use": f"{bytes_to_gb(used_mem):.1f} GB",
        "Available": f"{bytes_to_gb(mem.available):.1f} GB",
        "Committed": f"{bytes_to_gb(used_mem + swap.used):.1f}",
        "Cached": f"{bytes_to_gb(mem.cached):.1f} GB",
        "percent": mem.percent,
        "composition_used": used_mem,
        "composition_cached": mem.cached,
        "composition_buffers": getattr(mem, 'buffers', 0),
        "composition_free": mem.free,
        "composition_total": mem.total,
    }

def get_dynamic_memory_info():
    info = _dynamic_info_cache.copy()
    for key in list(info.keys()):
        if key.startswith('composition_') or key == 'percent':
            info.pop(key)
    return info

def get_memory_percent():
    return _dynamic_info_cache.get("percent", 0.0)

def get_memory_composition():
    return {k: v for k, v in _dynamic_info_cache.items() if k.startswith('composition_')}

update_dynamic_memory_info() 