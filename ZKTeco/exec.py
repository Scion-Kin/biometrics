#!/usr/bin/env python3
from zk import ZK

def exec(device, func, *args, **kwargs):
    """
    Executes a function on the ZK connection object.
    
    :param device: The device configuration dictionary containing connection details.
    :param func: The name of the function to execute on the ZK connection.
    :param args: Positional arguments to pass to the function.
    :param kwargs: Keyword arguments to pass to the function.
    """
    conn = None

    try:
        zk = ZK(
            device["ip"],
            port=device.get("port", 4370),
            timeout=device.get("timeout", 5),
            password=device.get("password", 0),
            force_udp=device.get("force_udp", False),
            ommit_ping=device.get("ommit_ping", False)
        )
        conn = zk.connect()
        if not hasattr(conn, func):
            raise AttributeError(f"ZK object has no attribute '{func}'")

        return getattr(conn, func)(*args, **kwargs)
    
    except Exception as e:
        raise Exception(f"An error occurred while executing '{func}': {e}")

    finally:
        if conn:
            try:
                conn.enable_device()  # Re-enable the device after operations
                conn.disconnect()
            except Exception as e:
                print(f"An error occurred while disconnecting: {e}")
