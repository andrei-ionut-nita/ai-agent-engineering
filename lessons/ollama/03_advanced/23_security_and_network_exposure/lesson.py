"""
Lesson 23: checking whether Ollama is exposed beyond your own machine.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/ollama/03_advanced/23_security_and_network_exposure/lesson.py
"""

import os
import socket


def main() -> None:
    # OLLAMA_HOST controls what address the server binds to. Unset (the
    # default) means "localhost only", nothing outside this machine can
    # reach it. Set to "0.0.0.0" (all network interfaces), it becomes
    # reachable from other devices on your network, or the internet, if
    # your machine is directly exposed.
    ollama_host = os.environ.get("OLLAMA_HOST", "not set (defaults to 127.0.0.1, localhost only)")
    print(f"OLLAMA_HOST: {ollama_host}")

    if "0.0.0.0" in ollama_host or "::" in ollama_host:
        print(
            "\nWARNING: Ollama appears configured to listen on all network "
            "interfaces. Anyone who can reach this machine over the network "
            "can call your models, unless something else (a firewall, a "
            "reverse proxy with auth) is blocking them. See README for why "
            "this matters."
        )
    else:
        print("\nOllama is bound to localhost only: not reachable from other machines.")

    # A quick, real check: can THIS machine's own hostname/LAN address
    # reach the server, or only "localhost" specifically? This doesn't
    # prove anything about the outside world, but it's a concrete way to
    # see the difference between "listening on localhost" and "listening
    # on every interface" instead of just reading documentation about it.
    hostname = socket.gethostname()
    try:
        lan_ip = socket.gethostbyname(hostname)
        if lan_ip.startswith("127."):
            # Many Linux setups map the hostname to a loopback address in
            # /etc/hosts, which isn't a real LAN address at all, so it's
            # called out explicitly rather than printed as if it were one.
            print(f"\nThis machine's hostname resolves to {lan_ip}, a loopback address, not a real LAN address.")
            print("(Run `ip addr` or `ifconfig` to find your actual LAN IP if you want to test this for real.)")
        else:
            print(f"\nThis machine's LAN address: {lan_ip}")
            print(
                f"If OLLAMA_HOST were 0.0.0.0, another device on your network could "
                f"reach it at http://{lan_ip}:11434. With the default, it can't."
            )
    except socket.gaierror:
        print("\n(Could not resolve this machine's LAN address to demonstrate further.)")


if __name__ == "__main__":
    main()
