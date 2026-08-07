# Lesson 22: `requirepass`, ACLs, TLS between an agent and its cache

## Where we left off

Every lesson so far connected as the default user, with the one
password Lesson 2's compose file set (`requirepass`). That's fine for a
single trusted application, an agent process that owns the whole
Redis instance. It's the wrong shape once more than one piece of code
talks to the same Redis, and each should only be able to touch what it
actually needs.

## `requirepass`: one password, full access

```yaml
REDIS_ARGS: "--requirepass redis"
```

This is what every lesson in this course has authenticated with
already, one shared secret, and whoever has it can run *any* command
against *any* key. It's better than no password, but it's all-or-
nothing.

## ACLs: named users, scoped permissions

```python
r.execute_command(
    "ACL", "SETUSER", "agent", "on", ">agentpass",
    "~session:*", "+get", "+set", "+setex", "+ping",
)
```

`ACL SETUSER` creates or updates a named user. Reading the pieces:
`on` (the user can log in), `>agentpass` (sets its password), `~session:*`
(a key pattern, this user can only touch keys matching it), `+get
+set +setex +ping` (only these commands are allowed, everything else
is denied by default once any `+command` rule is present). A worker
that only manages session state gets a user that literally cannot run
`FLUSHALL` or read another service's keys, not because the application
code promises not to, because Redis itself refuses.

## Connecting as a scoped user

```python
agent_conn = redis.Redis.from_url(
    "redis://agent:agentpass@localhost:6379", decode_responses=True
)
agent_conn.set("session:1", "active")   # allowed, matches ~session:*
agent_conn.set("other:key", "x")        # denied
```

Same `Redis.from_url` as every other lesson, just a DSN with the
scoped user's own credentials instead of the shared `requirepass`
default. `redis-py` doesn't do anything special here, the enforcement
is entirely server-side.

## TLS: encrypting the connection itself

ACLs control *what* an authenticated connection can do; TLS controls
whether the connection (including the password on it) can be read by
anyone on the network path in between. `redis-py` accepts it as
connection options:

```python
redis.Redis(host="...", port=6380, ssl=True, ssl_ca_certs="/path/to/ca.pem")
```

This course's local Docker Compose setup doesn't run Redis with TLS,
setting it up needs real certificates and a `--tls-port` on the
server, worth doing on a real deployment reachable over an untrusted
network, unnecessary complexity for `localhost` during learning.

## Running it

```bash
docker compose up -d redis
uv run python lessons/redis/03_advanced/22_security_auth_and_tls/lesson.py
```

## Expected output

```
Default user: default
Created scoped user 'agent'
agent PING -> True
agent SET session:1 -> allowed
agent SET other:key -> denied: No permissions to access a key
agent FLUSHALL -> denied: User agent has no permissions to run the 'flushall' command
```

## Checkpoint

- **`requirepass`**: one shared password, full access, what this
  course has used until now.
- **`ACL SETUSER`**: named users with a key pattern (`~pattern`) and an
  explicit allowed-command list (`+command`), enforced server-side.
- **TLS**: a separate concern from ACLs, encrypts the connection
  itself, matters once Redis is reachable over an untrusted network.

If anything here still feels unclear, ask before moving to Lesson 23.
