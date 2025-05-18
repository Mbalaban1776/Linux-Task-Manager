# src/resources/resource_monitor.py

import psutil

def get_cpu_percent():
    return psutil.cpu_percent(interval=None)

def get_memory_percent():
    return psutil.virtual_memory().percent
