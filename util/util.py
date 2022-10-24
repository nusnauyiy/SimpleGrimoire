import time


def log(*args, **kwargs):
    """Log the fuzzing results"""
    current_time = time.strftime("%H:%M:%S", time.localtime())
    print(f"[{current_time}]", *args, **kwargs)


def bytes_to_str(input_bytes: bytes) -> str:
    # return the 'original input string'
    return input_bytes.decode("utf-8")
