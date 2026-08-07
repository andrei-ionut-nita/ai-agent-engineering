# Lesson 22: Running Ollama as a Background Service

## What's actually been running this whole course

Every lesson in this course has assumed something true but unexamined
so far: that Ollama's server is already running in the background,
listening on `localhost:11434`, before your script starts. On most
installs, that's handled automatically:

- **macOS/Windows**: the Ollama app installs a background service that
  starts automatically at login, the same idea as Docker Desktop.
- **Linux**: the installer sets up a `systemd` service (`ollama.service`),
  check its status with `systemctl status ollama`, or start it manually
  in a terminal with `ollama serve` if it isn't already running.

`ollama serve` is the actual command that starts the server, whether
run directly or wrapped by a service manager. Every `ollama` CLI
command and every Python call in this course is really just a client
talking to whatever's listening on that port.

## The real lesson: don't assume a background service is ready

A background service being installed doesn't mean it's instantly
available the moment your program starts, especially right after a
reboot, container start, or service restart, there's a real window
where it's still coming up. A program that calls `ollama.chat()`
immediately on startup, with no check first, will occasionally fail
with a confusing `ConnectionError` that has nothing to do with your
actual code, a real race condition, not a hypothetical one.

## The code, piece by piece

```python
def wait_for_ollama(timeout_seconds: float = 10.0, poll_interval: float = 0.5) -> int:
    deadline = time.time() + timeout_seconds
    attempts = 0

    while time.time() < deadline:
        attempts += 1
        try:
            ollama.list()
            return attempts
        except ConnectionError:
            time.sleep(poll_interval)

    raise TimeoutError(...)
```

A small polling loop: try a cheap, harmless call (`ollama.list()`,
which just asks what's already pulled, no generation involved), and if
it fails with `ConnectionError`, wait briefly and try again, up to a
real deadline. This is a general pattern worth having in your toolkit
for any program that depends on a background service it doesn't fully
control the startup timing of, not specific to Ollama.

```python
attempts = wait_for_ollama()
response = ollama.chat(model="llama3.2", messages=[...])
```

Only after readiness is confirmed does the program do its real work.
On a normal, already-running machine, `attempts` will almost always be
`1`, the check costs almost nothing when the service was already up,
and saves you from a flaky failure on the occasions it wasn't.

## Running it

```bash
uv run python lessons/ollama/03_advanced/22_running_as_a_background_service/lesson.py
```

## Expected output

On a machine where Ollama is already running (true for every prior
lesson in this course):

```
Waiting for Ollama to be ready...
Ready after 1 attempt(s).
First real call succeeded: Hello.
```

If you want to see the retry path fire for real, stop the Ollama
service first (`systemctl stop ollama` on Linux, or quit the app on
macOS/Windows), run this lesson, and start it again partway through,
you should see `attempts` land higher than `1`.

## Checkpoint

- **`ollama serve`**: the actual command that starts the local server,
  usually wrapped by your OS's service manager so it starts
  automatically.
- **Background service ≠ instantly ready**: a real startup race
  condition exists right after boot, container start, or restart.
- **The polling pattern**: try a cheap call, catch the connection
  error, wait, retry, with a real deadline, general-purpose beyond
  Ollama specifically.

If anything here still feels unclear, ask before moving to Lesson 23.
