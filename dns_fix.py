import socket


def patch_dns():
    print("[DNS FIX] Patching socket.getaddrinfo to force IPv4 resolution...")
    _orig_getaddrinfo = socket.getaddrinfo

    def new_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
        if host and host not in ('localhost', '127.0.0.1', '::1'):
            return _orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
        return _orig_getaddrinfo(host, port, family, type, proto, flags)

    socket.getaddrinfo = new_getaddrinfo


patch_dns()
