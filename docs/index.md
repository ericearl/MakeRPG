# The Idea is Here

MakeRPG is intended to be a system that allows anyone who can edit plain text YAML files to make automatic characters from game systems.

# [The Code is on GitHub](https://github.com/ericearlpdx/MakeRPG)

The actual code is open-sourced on GitHub.  It is written by `ericearlpdx` in Python 3.7 using Django 2.1.  The CharacterCreator app's random name generator list of names was built using U.S. Census data.  Please file bugs and feature requests using the [MakeRPG GitHub issues page](https://github.com/ericearlpdx/MakeRPG/issues).

# YAML Files

You can find the rules for creating the two necessary YAML files in the left menu of this readthedocs website.  The code repository includes one generic pair of system example YAML's and one real example of a pair of YAML's from my personal favorite, R. Talsorian's Cyberpunk 2020 (R) written by Mike Pondsmith, et al.

"YAML Ain't Markup Language" (YAML) files have a few basic formatting rules.

1. Every character within the file is treated as a character, so quotations and punctuation are not necessary, but they are allowed.
1. "Octothorpes" or "pound signs" or "hashtags" `#` are ignored by programs that are reading or parsing YAML files.
1. "Keys" or "Keywords" are always the first thing followed by a colon and a space `: ` and then a "Value".
1. You can either have:
    - Single values
    - Indented and hyphenated/bulleted lists of values ; or
    - Indented and further expanded keys and values
1. Indents are made up of 2 or 4 spaces and must be consistent throughout.
