# The Rules

To build a valid stats and skills system specifically for this software, use the following rules.

For a fully documented YAML file example, see the `system_stats_skills.yaml` in the repository's `Examples` folder.

# Reference Examples

## `roles` keyword

```
roles:
    Warrior:
        special:
            Hit hard: 1-8
        common:
            - Buffness
            - Melee
            - Hand-to-hand
```

## `stats` keyword

```
stats:
    THINK:
        stat: 1-18
        skills:
            Read: 0-4
            Look cool: 0-6
            Be scary: 0-4
            Talk fast: 0-10
            Tell bad jokes: 0-8
```

# Required Keywords

## `roles`

The `roles` indented keyword list is made of roles or what some systems call classes or types.  Each role listed after the roles key is the name of that role and each role has two necessary keywords, `special` and `common`.

The role distributes `role` skill points among these two categories.  Any other skills require a separate set of `other` skill points.

### `special`

The `special` keyword list is a list of skills that only that `role` has available.

### `common`

The `common` keyword bulleted list is skills pulled from the broader pool of skills.

## `stats`

The `stats` indented keyword list is an indented list of character statistics in the gaming system you're defining.  Indented under `stats` are the stat names as you want them to appear in character sheets.  Under each stat are the keywords `stat` and `skills`.

In skill and stat ranges, a minimum value greater than `0` means that minimum number of points will always be spent on that stat or skill from the stat or skill points.

### `stat`

The minimum to maximum range of possible values of that stat.

### `skills`

An indented list of keys and values where the key is the skill name and the value is the minimum to maximum range of possible values of that skill.
