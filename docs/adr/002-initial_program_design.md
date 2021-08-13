Date: 2021-07-12

# Status
<!-- What is the status? Draft, Proposed, Accepted, Rejected, Deprecated or Superseded?
-->
Accepted

# Context
<!-- What is the issue that we're seeing that is motivating this decision or change? -->
We need to define the architecture of the program to fulfill the goals of
[001](001-high_level_problem_analysis.md).

# Proposals
<!-- What are the possible solutions to the problem described in the context -->

## Storage

For the storage we can use two approaches:

* Use the markup file that is synced between the mobile and the desktop.
* Use an external storage, and use the markup file just as a transport of data
    from the mobile.

The first option is juicy as the code to interact with the storage would be
simpler and with less dependencies. We need to write the parser anyway to get
the data from the file. The side effects are that

* We would need to prevent the collisions between a mobile update and the data
    processed by the desktop client.  For example, imagine that you've made some
    changes in the mobile, but they're not yet synced, you run the inbox
    processing tool and clear some, before the program has any chance to save
    the state, the mobile syncs the file. You'll have some changes in memory,
    and some non imported changes in the file.

* When the inbox grows, you can have performance issues. Having an external
    optimized storage will always be faster.

* There is no concept of temporal state: You'll only have the last picture of
    the inbox, not the progression, which could be interesting to show as part
    of the inbox statistics.

## Inputs

There are two kind of sources: mobile and desktop.

### Mobile

The mobile user will create a markup file that follows
[003](003-markup_definition.md). That file gets synced with Syncthing to the
desktop, which extracts the data from it, ingests it in the storage solution and
then cleans it.

### Desktop

#### Addition of elements

The desktop user will create elements directly in the storage solution. It can
do it through:

* TUI command line arguments.
* REPL interface.
* Using the desktop editor.

The TUI is useful to allow interaction between programs. We could accept an
argument that uses the same markup as with the mobile device. The problem is
that the editing features of the terminal are limited.

The REPL interface could be a step forward in terms of usability from the TUI,
with autocompletion, but it will still lack the editing features of a desktop
editor.

The editor is the quickest way to write in the desktop, but it will lack the
domain specific features, such as autocompletion of the element types.

#### Inbox processing

The user is presented one element at a time selected from a prioritized list of
elements. For each of them it can:

* Do the element.
* Postpone it.

The first will mark the element as done, and won't appear in future inbox
processing sessions. Postponing it will make the item show at the next session.

The element prioritization is done by:

* Element category type: Each category will have a priority.
* Element creation date: Ordered by oldest first.

It will measure the time spent between each element, and if it surpasses
a defined amount, it will warn the user, so it is aware of it and can act
accordingly.

Once the inbox processing session is done, it will show the inbox stats. As
a first approximation, it will show a measure of the done elements compared with
how many are left.

We'll use a REPL interface built with
[questionary](https://lyz-code.github.io/blue-book/questionary/), as it's the
quickest library to build simple REPL, and is based in [Prompt
toolkit](https://lyz-code.github.io/blue-book/coding/python/prompt_toolkit/),
which will give us more flexibility if we need more complex features.

# Decision
<!-- What is the change that we're proposing and/or doing? -->

For the storage we'll use
[Pydantic](https://lyz-code.github.io/blue-book/coding/python/pydantic/) models
managed by [Repository-orm](https://lyz-code.github.io/repository-orm/).

We'll start with the TUI and launching the editor as input methods for the
desktop, and a file following the markup language for mobile devices.

Then we'll develop the inbox processing REPL.

# Consequences
<!-- What becomes easier or more difficult to do because of this change? -->
