
To add new elements into pynbox, you need to use the defined [markup
language](#pynbox-markup-language) either through the [command
line](#command-line) or through a [file](#parse-file).

# Pynbox markup language

It's designed to use the minimum number of friendly keystrokes both for a mobile
and a laptop. The format of each element is:

```
{{ type_identifier }} {{ description }}
{{ body }}
```

Where:

* `type_identifier`: Is a case insensitive string of the fewest letters as
    possible, that identifies the type of the element. It can be for example
    `t.` for a task, or `i.` for an idea. The identifiers are defined in the
    [configuration file](configuration.md).
* `description`: A short sentence that defines the element.
* `body`: An optional group of paragraphs with more information of the element.

For example:

```
T. buy groceries
* milk
* tofu
i. to have an inbox management tool would be awesome!
```

# Command line

You can use the `add` subcommand to put new items into the inbox.

```bash
pynbox add t. buy milk
```

# Parse a file

If you need to add elements with a body, more than one element, or want to
import them from other device, using a file might be easier.

Write the elements one after the other in the file and then use the `parse`
command.

```bash
pynbox parse file.txt
```
