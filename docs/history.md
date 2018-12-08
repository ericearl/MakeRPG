# The Rules

To build a valid character history system specifically for this software, use the following rules.

For a fully documented YAML file example, see the `system_history.yaml` in the repository's `Examples` folder.

# Reference Examples

Basic History Event

```
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

```
What do you think of people?:
    dice: 1d6
    roll:
        1-3: Love 'em
        4-6: Hate 'em
    next: Age
```

Dice with an offset AND the `<ROLL X#>` with `reroll` keyword

```
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

```
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

# Required Keywords

`START`



`NPC`



`dice`



`roll`



`next`



# Optional Keywords

`<ROLL X#>`



`reroll`



`<NPC type>`
