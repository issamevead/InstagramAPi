import functools
import time
from random import randint
from threading import Thread
from typing import Any, List


def create_thread(function):
    @functools.wraps(function)
    def wrapper_timer(*args, **kwargs):
        t = Thread(target=function, args=args, kwargs=kwargs)
        t.daemon = True
        t.start()

    return wrapper_timer


def get_random_proxy():
    proxies = (
        "1.1",
        "1.2",
        "1.3",
        "1.4",
        "3.1",
        "3.2",
        "4.1",
        "1.5",
        "3.3",
        "8.110",
        "78.48",
        "78.48",
        "3.5",
        "4.4",
        "4.6",
    )
    p = proxies[randint(0, len(proxies) - 1)]
    return {
        "https": f"socks5://10.10.{p}:8081",
        "http": f"socks5://10.10.{p}:8081",
    }


def go_sleep(seconds: int) -> None:
    """Sleep for a given number of seconds"""
    time.sleep(randint(3, seconds))


def json_extract(obj, key) -> List[Any]:
    """Recursively fetch values from nested JSON."""
    arr = []

    def extract(obj, arr, key):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, val in obj.items():
                if isinstance(val, (list, dict)) and k != key:
                    extract(val, arr, key)
                elif k == key:
                    arr.append(val)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr

    values = extract(obj, arr, key)
    return values


def read_text_file(file_path: str) -> str:
    with open(file_path, "r") as f:
        return f.read().splitlines()


def get_proxy():
    proxies = read_text_file("app/proxies.txt")
    p = proxies[randint(0, len(proxies) - 1)]
    return {"socks5": f"{p}", "socks5": f"{p}"}
