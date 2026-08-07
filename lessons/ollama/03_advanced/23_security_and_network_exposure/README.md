# Lesson 23: Security and Network Exposure

## Ollama has no built-in authentication

Every lesson in this course has made requests with no API key, no
login, nothing to prove who's calling, because Lesson 3 explained
there's nothing to authenticate against on `localhost`. That design
choice is fine, good even, as long as the server only ever listens on
`localhost`. It stops being fine the moment it listens on a real
network interface: **anyone who can reach that address can call your
models, list them, pull new ones, or delete them, with no login at
all.** Unlike Gemini or any cloud provider, there is no API key layer
protecting a network-exposed Ollama server.

## `OLLAMA_HOST`: the setting that changes everything

By default, Ollama binds to `127.0.0.1` (localhost only): nothing
outside your own machine can reach it, no matter what else is on your
network. Setting the `OLLAMA_HOST` environment variable to `0.0.0.0`
makes it listen on every network interface instead, which is sometimes
genuinely useful (running Ollama on one machine, calling it from
another on the same LAN, say a lightweight laptop talking to a
GPU-equipped desktop), but it also means every device on that network,
and the internet too, if your machine is directly exposed without a
firewall or NAT, can now reach the server unauthenticated.

This is a real, common misconfiguration: someone runs Ollama in a
cloud VM or container, sets `OLLAMA_HOST=0.0.0.0` so a different
service can reach it, and forgets that "reachable by my other service"
and "reachable by the entire internet" are the same setting unless
something else is actively blocking the rest of the world.

## If you do need network access

- **A firewall rule**, restricting port `11434` to only the specific
  IP addresses that legitimately need it, rather than the whole
  internet.
- **A reverse proxy in front of Ollama** (nginx, Caddy, or similar)
  that adds real authentication (an API key, basic auth) before
  forwarding requests through, since Ollama itself won't do that for
  you.
- **Never expose it directly to the public internet** without one of
  the above. A model server with no auth is a genuinely valuable thing
  for someone to find: free compute, and depending on what else is on
  that machine, occasionally more than that.

## The code, piece by piece

```python
ollama_host = os.environ.get("OLLAMA_HOST", "not set (defaults to 127.0.0.1, localhost only)")
```

Reads the actual setting on your machine, `os.environ.get` with a
default that documents what "unset" really means, rather than leaving
you to remember it.

```python
if "0.0.0.0" in ollama_host or "::" in ollama_host:
    print("WARNING: ...")
```

A simple check for the two common "listen on everything" patterns
(`0.0.0.0` for IPv4, `::` for IPv6), not exhaustive, but enough to
catch the configuration that actually matters here.

## Running it

```bash
uv run python lessons/ollama/03_advanced/23_security_and_network_exposure/lesson.py
```

## Expected output

On a default installation (the setup this whole course assumes):

```
OLLAMA_HOST: not set (defaults to 127.0.0.1, localhost only)

Ollama is bound to localhost only: not reachable from other machines.

This machine's hostname resolves to 127.0.1.1, a loopback address, not a real LAN address.
(Run `ip addr` or `ifconfig` to find your actual LAN IP if you want to test this for real.)
```

The exact loopback address and whether your hostname resolves to one
at all depends on your OS's own networking setup; the important line
is the first one, confirming `OLLAMA_HOST` is unset and therefore
localhost-only.

## Checkpoint

- **No built-in auth**: unlike every cloud provider in this repo,
  Ollama has nothing checking who's calling.
- **`OLLAMA_HOST`**: unset means localhost-only (safe by default);
  `0.0.0.0` means every network interface (only safe with something
  else, a firewall or proxy, actively protecting it).
- **If you need network access**: a firewall rule, or a reverse proxy
  adding real authentication, never expose it directly and unauthenticated.

If anything here still feels unclear, ask before moving to Lesson 24,
this course's capstone.
