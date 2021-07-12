Date: 2021-07-12

# Status
<!-- What is the status? Draft, Proposed, Accepted, Rejected, Deprecated or Superseded?
-->
Draft

# Context
<!-- What is the issue that we're seeing that is motivating this decision or change? -->
I've been using a markdown file to annotate all the elements of my inbox for
later processing. The file was available both by computer and mobile phone and
synced using [Syncthing](https://lyz-code.github.io/blue-book/linux/syncthing/).

The inbox elements are of different types: events, tasks, ideas, media
suggestions (movies, tv shows, books or music).

The problem is that I'm not able to keep the pace to process the elements and
the file is increasingly growing.

The goal is to have a piece of software that would help in inbox management by:

* Prioritizing a type of element over the others.
* Giving stats on the inbox status.
* Giving feedback on the inbox processing process.
* Making the insertion of new elements as effortless as possible.

# Proposals
<!-- What are the possible solutions to the problem described in the context -->

On the Android side, we can define a markup syntax where the user adds new items
through an editor, such as Markor. That file gets synced to the desktop host
through Syncthing.

On the desktop side, we can have a command line client that:

* Processes the Android markup file to ingest the new elements.
* Has a REPL and TUI interfaces to add new elements.
* Has a REPL interface to process the existing inbox, which allows the user to
    select the order of the elements or a subset of them to process. It will
    monitor the inbox processing to detect improvable behaviours. And will give
    the user an idea of the state of the inbox.

I've done a super quick search to see if there is anything there in the wild
that fulfills the user case, but found none. If you know of a program that might
work, please [contact me](https://lyz-code.github.io/blue-book/contact/).

# Decision
<!-- What is the change that we're proposing and/or doing? -->

Implement the proposed solution.

# Consequences
<!-- What becomes easier or more difficult to do because of this change? -->
