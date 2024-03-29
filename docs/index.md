[![Actions Status](https://github.com/lyz-code/pynbox/workflows/Tests/badge.svg)](https://github.com/lyz-code/pynbox/actions)
[![Actions Status](https://github.com/lyz-code/pynbox/workflows/Build/badge.svg)](https://github.com/lyz-code/pynbox/actions)
[![Coverage Status](https://coveralls.io/repos/github/lyz-code/pynbox/badge.svg?branch=main)](https://coveralls.io/github/lyz-code/pynbox?branch=main)

`pynbox` aims to help you with the daily [emptying of the
inbox](https://lyz-code.github.io/blue-book/task_tools/#inbox) by:

* Prioritizing the elements by their type.
* Giving insights on the inbox status.
* Giving feedback on the inbox processing process.
* Making the insertion of new elements as effortless as possible.

# Installing

```bash
pip install pynbox
```

# Quick overview

![ ](screencast.gif)

# Proposed workflow

When you're on your desktop you can add elements directly with the [command
line](creating_new_elements.md#command-line), when you're on the go, use any
text editor, such as
[Markor](https://f-droid.org/en/packages/net.gsantner.markor/), and sync the
file with [Syncthing](https://lyz-code.github.io/blue-book/linux/syncthing/) to
your laptop, and then [parse the file](creating_new_elements.md#parse-a-file).

To process the elements, you can daily use `pynbox process`. If you want to
focus on a category, use `pynbox process category`.

# References

As most open sourced programs, `pynbox` is standing on the shoulders of
giants, namely:

[Pytest](https://docs.pytest.org/en/latest)
: Testing framework, enhanced by the awesome
    [pytest-cases](https://smarie.github.io/python-pytest-cases/) library that made
    the parametrization of the tests a lovely experience.

[Mypy](https://mypy.readthedocs.io/en/stable/)
: Python static type checker.

[Flakeheaven](https://github.com/flakeheaven/flakeheaven)
: Python linter with [lots of
    checks](https://lyz-code.github.io/blue-book/devops/flakeheaven#plugins).

[Black](https://black.readthedocs.io/en/stable/)
: Python formatter to keep a nice style without effort.

[Autoimport](https://lyz-code.github.io/autoimport)
: Python formatter to automatically fix wrong import statements.

[isort](https://github.com/timothycrosley/isort)
: Python formatter to order the import statements.

[PDM](https://pdm.fming.dev/)
: Command line tool to manage the dependencies.

[Mkdocs](https://www.mkdocs.org/)
: To build this documentation site, with the
[Material theme](https://squidfunk.github.io/mkdocs-material).

[Safety](https://github.com/pyupio/safety)
: To check the installed dependencies for known security vulnerabilities.

[Bandit](https://bandit.readthedocs.io/en/latest/)
: To finds common security issues in Python code.

[Yamlfix](https://github.com/lyz-code/yamlfix)
: YAML fixer.

# Contributing

For guidance on setting up a development environment, and how to make
a contribution to *pynbox*, see [Contributing to
pynbox](https://lyz-code.github.io/pynbox/contributing).

## Donations

<a href="https://liberapay.com/Lyz/donate"><img alt="Donate using
Liberapay" src="https://liberapay.com/assets/widgets/donate.svg"></a>
or
[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/T6T3GP0V8)

If you are using some of my open-source tools, have enjoyed them, and want to
say "thanks", this is a very strong way to do it.

If your product/company depends on these tools, you can sponsor me to ensure I
keep happily maintaining them.

If these tools are helping you save money, time, effort, or frustrations; or
they are helping you make money, be more productive, efficient, secure, enjoy a
bit more your work, or get your product ready faster, this is a great way to
show your appreciation. Thanks for that!

And by sponsoring me, you are helping make these tools, that already help you,
sustainable and healthy.

