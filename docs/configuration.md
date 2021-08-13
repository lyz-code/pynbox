The first time you use `pynbox`, it will create the default configuration in
`~/.local/share/pynbox` or the path of the `-c` command line argument.

# database_url

`pynbox` uses [`repository_orm`](https://lyz-code.github.io/repository-orm/) to
persist the elements. By default, it uses the
[TinyDB](https://tinydb.readthedocs.io/en/latest/usage.html) backend, if you
encounter performance issues, move to
[SQLite](https://lyz-code.github.io/repository-orm/pypika_repository/), and then
to MySQL. Refer to the docs of
[`repository_orm`](https://lyz-code.github.io/repository-orm/) to do so.

# max_time

You should not spend too much time processing your inbox, the idea is that if it
will take you more than 2 minutes to process an element, it's better to create
a task to address it. `max_time` defines the maximum number of seconds to
process an element. A warning will be shown if it takes you longer.

# types

It's where you define the element categories, their regular expressions and
their priority. For example:

```yaml
types:
  task:
    regexp: t\.
    priority: 4
  idea:
    regexp: i\.
```

If the priority is not defined, it's assumed to be `3`.

!!! note "The regular expression needs to be a non capturing one"
    If you use parenthesis use `(?:<regular expression>)` instead of `(<regular
    expression>)`.
