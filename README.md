Instructions
=====

**Documentation** [https://epistemictableau.herokuapp.com](https://epistemictableau.herokuapp.com)

Connectives
-----------

- **propositional symbols** = `[p-s][0-9]*`
- **and** = `^`
- **or** = `v`
- **implication** = `->`
- **negation** = `~`
- **next** = `N`
- **always** = `G`
- **eventually** = `F`
- **until** = `U`
- **weak until** = `W`
- **knowledge** = `ki`, for `i` in `[0..9]*`


Usage
-----

inside *src* folder, to parse formulae from file (one formula per line, no blank lines), run:

`$ python tableauverifier.py parse --file <formula-file> [--nnf]`

to show tableau for a formula, run: 

`$ python tableauverifier.py pctableau <formula> [--per-line]`

to show tableaux branches for formulae from file, run: 

`$ python tableauverifier.py pctableau --file <formula-file> [--per-line] [--belief]`

to show the tableaux graph for formulae from file, run: 

`$ python tableauverifier.py tableau --file <formula-file> [--per-line] [--belief]`

More options can be seen running:

`$ python tableauverifier.py --help`

Dependecies
--------------

- Python2.7
- docopt
- lrparsing
- NetworkX
- pyparsing
- pygraphviz
- graphviz

Restrictions
------------

**Binary and unary formulae must be inside parentheses.**

**Parentheses in atoms are prohibited and will generate parse error**

TODO
-------
