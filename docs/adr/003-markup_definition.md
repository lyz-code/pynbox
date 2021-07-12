Date: 2021-07-12

# Status
<!-- What is the status? Draft, Proposed, Accepted, Rejected, Deprecated or Superseded?
-->
Draft

# Context
<!-- What is the issue that we're seeing that is motivating this decision or change? -->
We need to define a markup language that allows the introduction of new elements
through a mobile device as effortlessly as possible.

The information to extract from each element is:

* Description.
* Body
* Element type.
* Priority.

# Proposals
<!-- What are the possible solutions to the problem described in the context -->

The format of each element is:

```
{{ type_identifier }} {{ description }}
{{ body }}
```

Where:

* `type_identifier`: Is a case insensitive string of the fewest letters as
    possible, that identifies the type of the element. It can be for example
    `T.` for a task, or `i.` for an idea.
* `description`: A short sentence that defines the element
* `body`: An optional group of paragraphs with more information of the element.

For example:

```
T. buy groceries
* milk
* tofu
i. pynbox report could show progress bars for each element type
```

# Decision
<!-- What is the change that we're proposing and/or doing? -->
Follow the only proposed language

# Consequences
<!-- What becomes easier or more difficult to do because of this change? -->
We'd need to write the parser.
