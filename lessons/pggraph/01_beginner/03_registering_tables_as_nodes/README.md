# Lesson 3: Registering tables as graph nodes

## Where we left off

Lesson 2 confirmed both containers work and that `graph.status()`
starts empty. This lesson creates the two ordinary Postgres tables
every later lesson in this course builds on, `companies` and `people`,
and registers them with pggraph as node tables.

## The schema: nothing graph-specific about it

```sql
CREATE TABLE companies (id text PRIMARY KEY, name text NOT NULL);
CREATE TABLE people (
  id text PRIMARY KEY,
  name text NOT NULL,
  company_id text REFERENCES companies(id)
);
```

There is nothing here pggraph needs to know about in advance. This is
just two normal tables with a foreign key between them, the kind of
schema that already exists in most applications. pggraph doesn't
require special columns, a graph-shaped schema, or any change to how
you'd otherwise write this.

## `graph.add_table()`: telling pggraph a table is a node type

Registration is a separate, explicit step from creating the table.
pggraph doesn't scan your schema automatically (that's `auto_discover`,
covered in Lesson 17), you tell it which tables to treat as nodes and
which columns to expose for search and filtering:

```sql
SELECT graph.add_table(
  'public.companies'::regclass,
  id_column := 'id',
  columns := ARRAY['name']
);

SELECT graph.add_table(
  'public.people'::regclass,
  id_column := 'id',
  columns := ARRAY['name']
);
```

`id_column` is the business identifier pggraph will use to refer to
each row (here, the same `id` you'd use in a `WHERE` clause). `columns`
is the list of columns pggraph should read and expose when it hydrates
or searches a node, not every column on the table needs to be listed,
only the ones later lessons will search or filter on.

## Checking what's registered

```sql
SELECT * FROM graph.registered_tables();
```

This is metadata only, registering a table doesn't build anything yet,
`graph.status()` would still show `node_count = 0`. Building happens
next lesson, once there's also an edge to register.

## Running it

```bash
docker compose up -d
uv run python lessons/pggraph/01_beginner/03_registering_tables_as_nodes/lesson.py
```

## Expected output

```
Registered tables:
  companies  id_columns=['id']  columns=['name']
  people     id_columns=['id']  columns=['name']
```

## Checkpoint

- **no special schema needed**: `graph.add_table()` works on ordinary
  tables, including ones with foreign keys, with no columns added.
- **`graph.add_table(table, id_column, columns)`**: registers a table as
  a node type, `id_column` is the business ID, `columns` is what gets
  exposed for search/filter/hydration.
- **registration is metadata, not a build**: `graph.registered_tables()`
  shows what's registered; `graph.status()` still reports zero nodes
  until `graph.build()` runs.

If anything here still feels unclear, ask before moving to Lesson 4.
