import pynvml


def log_gpu_metrics():
    try:
        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
        mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
        pynvml.nvmlShutdown()
        return {
            "temperature_C": temp,
            "memory_used_MB": round(mem.used / 1024 / 1024, 2),
            "memory_total_MB": round(mem.total / 1024 / 1024, 2),
        }
    except Exception as e:
        return {"status": "gpu_error", "error": str(e)}
