# The Rules

To build a valid character history system specifically for this software, use the following rules.

For a fully documented YAML file example, see the `system_history.yaml` in the repository's `Examples` folder.

# Reference Examples

`START` and `NPC` keywords

```yaml
START: Usual Clothing
NPC:
    - Usual Clothing
    - What do you think of people?
```

Basic History Event

```yaml
Usual Clothing:
    dice: 1d4
    roll:
        1: Clean
        2: Dirty
        3: No real pants. Never real pants.
        4: Trendy/fashionable
    next: What do you think of people?
```

Hyphenated rolls

```yaml
What do you think of people?:
    dice: 1d6
    roll:
        1-3: Love 'em
        4-6: Hate 'em
    next: Age
```

Dice with an offset AND the `<ROLL X#>` with `reroll` keyword

```yaml
Age:
    dice: 1d4 + 18
    roll:
        19:
            next: Life
        20:
            next: <ROLL X2> Life
        21:
            next: <ROLL X3> Life
        22:
            next: <ROLL X4> Life
    next: Siblings
Life:
    dice: 1d10
    roll:
        1-3: Friends and good things
        4-6: Enemies and bad things
        7-8: Romance!
        9-10: Nothing eventful
    reroll: Life
```

The `<NPC type>` and `<ROLL X#>` keywords

```yaml
Siblings:
    dice: 1d4
    roll:
        1:
            next: <NPC sibling> Sibling binary gender
        2:
            next: <ROLL X2> <NPC sibling> Sibling binary gender
        3-4: Only child
    next: Love affairs
```

# Required

`START`

The START key's value MUST match a `[History event name]`.

`NPC`

The NPC key's hyphenated list MUST match a `[History event name]` for each bulleted point.

`[History event name]`

Replace `[History event name]` here with your history event's name.  It is a single event which you would roll to choose in character creation during a regular character creation.  The order that history events appear does not matter as long as every named event has a matching definition.  History events MUST have at least a `dice` and a `roll` key.

`dice`

Any dice definition of the form `<QUANTITY>d<SIDES> <OPTIONAL + or -> <OPTIONAL OFFSET>`, where `<QUANTITY>` MUST be an integer/whole number value of dice to throw, `<SIDES>` MUST be an integer/whole number greater than 1 representing the number of sides or possibilities of the dice, `<OPTIONAL + or ->` is an optional addition or subtraction to be used with `<OPTIONAL OFFSET>` which MUST be an integer/whole number.  Examples:

- `1d2`
- `5d17`
- `1d8 + 4`
- `3d6 - 2`

`roll`

The `roll` keyword's values must themselves be key-value pairs where all the possible dice rolls are represented in the keys.  For example, let's say a history event has a `dice: 1d6`.  This means all values between 1 and 6 must have some sort of `outcome value`.  The following formats are supported:

1. `EVEN` and `ODD` pair format

    ```yaml
    EVEN: Even-numbered outcome
    ODD: Odd-numbered outcome
    ```

1. Single format

    ```yaml
    1: Outcome A
    2: Outcome B
    3: Outcome C
    4: Outcome D
    5: Outcome E
    6: Outcome F
    ```

1. Hyphenated format

    ```yaml
    1-2: Outcome A
    3-4: Outcome B
    5-6: Outcome C
    ```

1. Comma-separated format

    ```yaml
    1,2: Outcome A
    3,5: Outcome B
    4,6: Outcome C
    ```
`
1. Mixed format

    ```yaml
    1-2,4: Outcome A
    3,5: Outcome B
    6: Outcome C
    ```

# Optional

`[Outcome value]`

Replace `[Outcome value]` here with your roll's outcome.  Outcomes can be either a string describing the outcome of a roll OR a `next: [History event name]` key-value pair.

`next`

Controls what history event to roll next.

`<ROLL X#>`

The `#` in `<ROLL X#>` indicates how many times you would reroll this outcome value, which should be a `next: [History event name]` key-value pair.  For every `<ROLL X#>` tag there has to be a `reroll` key down the line.

`reroll`

The follow-up to a `<ROLL X#>` tag.  This tells the history event rolling queue to go back to the last `<ROLL X#>` tag.

`<NPC type>`

The `<NPC type>` tag triggers an NPC history events list roll for an NPC tied to the character with the name tag `type`.
