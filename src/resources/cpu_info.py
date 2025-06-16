import psutil
import cpuinfo

_cpu_info = cpuinfo.get_cpu_info()
_cpu_name = _cpu_info.get('brand_raw', 'CPU')
_max_freq = psutil.cpu_freq().max
_sockets = 1 # psutil does not provide a direct way to get this.
_cores = psutil.cpu_count(logical=False)
_logical_processors = psutil.cpu_count(logical=True)

# L1 and L2 cache sizes are not straightforward to get with psutil or cpuinfo on Linux
# This is a placeholder and might require more advanced methods or tools to get accurately
_l1_cache_str = _cpu_info.get('l1_data_cache_size', 'N/A')
_l2_cache_str = _cpu_info.get('l2_cache_size', 'N/A')


def get_cpu_name():
    return _cpu_name

def get_static_cpu_info():
    return {
        "Maximum speed": f"{_max_freq / 1000:.2f} GHz",
        "Sockets": str(_sockets),
        "Cores": str(_cores),
        "Logical processors": str(_logical_processors),
        "L1 cache": f"{_l1_cache_str // 1024} KB" if isinstance(_l1_cache_str, int) else "N/A",
        "L2 cache": f"{_l2_cache_str // 1024 / 1024:.1f} MB" if isinstance(_l2_cache_str, int) else "N/A"
    }

_dynamic_info_cache = {}

def update_dynamic_info():
    global _dynamic_info_cache
    utilization = psutil.cpu_percent(interval=None, percpu=False)
    speed = psutil.cpu_freq().current / 1000
    processes = len(psutil.pids())
    
    # Summing up threads from all processes
    threads = 0
    for p in psutil.process_iter():
        try:
            threads += p.num_threads()
        except psutil.NoSuchProcess:
            continue # Process may have terminated

    _dynamic_info_cache = {
        "Utilization": f"{utilization:.0f}%",
        "Speed": f"{speed:.2f} GHz",
        "Processes": str(processes),
        "Threads": str(threads),
        "utilization_float": utilization
    }

def get_dynamic_cpu_info():
    info = _dynamic_info_cache.copy()
    info.pop('utilization_float', None) # Don't show this in the UI grid
    return info


def get_cpu_percent():
    return _dynamic_info_cache.get('utilization_float', 0.0)

# Call once to initialize and populate the cache.
# The first call to psutil.cpu_percent() returns 0.0.
update_dynamic_info() 