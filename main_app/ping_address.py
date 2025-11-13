import subprocess
import platform
import socket


def ping(ip_address):
    """
    Ping an IP address to check if it's reachable.
    Uses ICMP ping, with a fallback to TCP connection test if ping fails.
    """
    if not ip_address:
        return False
    
    # Use correct param for Windows (-n) or Linux/Mac (-c)
    param = "-n" if platform.system().lower() == "windows" else "-c"
    
    # Set timeout (Windows uses -w for timeout in milliseconds, Linux/Mac uses -W for seconds)
    timeout_param = "-w" if platform.system().lower() == "windows" else "-W"
    timeout_value = "2000" if platform.system().lower() == "windows" else "2"

    try:
        result = subprocess.run(
            ["ping", param, "1", timeout_param, timeout_value, ip_address],
            capture_output=True,
            text=True,
            timeout=5  # Overall timeout for the subprocess
        )

        output = result.stdout.lower()

        # On Windows: success contains "reply from" without "unreachable"
        # On Linux/Mac: success contains "bytes from"
        if ("reply from" in output and "unreachable" not in output) or ("bytes from" in output):
            return True
        
        # If ping failed, try a TCP connection test as fallback (port 80 or 8000)
        # This helps when ICMP is blocked but HTTP is allowed
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            # Try port 8000 first (Django server), then 80 (HTTP)
            result = sock.connect_ex((ip_address, 8000))
            sock.close()
            if result == 0:
                return True
            # Try port 80
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((ip_address, 80))
            sock.close()
            if result == 0:
                return True
        except:
            pass
        
        return False
    except subprocess.TimeoutExpired:
        return False
    except Exception:
        return False
