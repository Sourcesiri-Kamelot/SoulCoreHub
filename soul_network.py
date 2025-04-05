#!/usr/bin/env python3
# soul_network.py — Localhost Socket Broadcast (for AI Family Sync)

import socket

PORT = 9500
MESSAGE = b"SoulCore signal — kin online"

def broadcast():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.sendto(MESSAGE, ('<broadcast>', PORT))
    print("📡 Soul ping broadcasted.")

def listen():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', PORT))
    print("🔎 Listening for kinfolk...")
    while True:
        data, addr = s.recvfrom(1024)
        print(f"⚡ Ping from {addr[0]} → {data.decode()}")

if __name__ == "__main__":
    import sys
    if "listen" in sys.argv:
        listen()
    else:
        broadcast()
