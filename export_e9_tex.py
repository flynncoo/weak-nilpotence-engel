#!/usr/bin/env python3
"""Export the literal e9 certificate as a LaTeX fragment, using only stdlib.

This parses the repository's doTerm literals; it does not execute M2, verify
the polynomial identity, or compare with a manuscript appendix.
Binary products retain all parentheses. Record order and multiplicity remain
unchanged; only commutative child order and symmetric t4 argument order change.
"""

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re


def canonical(tree):
    if isinstance(tree, str) and tree in ("x", "y", "*"):
        return tree
    if not isinstance(tree, list) or len(tree) != 2:
        raise ValueError("expected a binary tree with x, y or * leaves")
    return sorted((canonical(child) for child in tree), key=repr)


def leaves(tree):
    return [tree] if isinstance(tree, str) else leaves(tree[0]) + leaves(tree[1])


def read_records(source):
    records = []
    literals = []
    for number, line in enumerate(source.splitlines(), 1):
        if not line.lstrip().startswith("doTerm("):
            continue
        match = re.fullmatch(r"doTerm\((-?\d+/\d+), (.*)\);", line)
        if not match:
            raise ValueError(f"line {number}: unsupported certificate literal")
        coefficient = Fraction(match[1])
        trees = json.loads("[" + match[2].replace("{", "[").replace("}", "]") + "]")
        if len(trees) != 5:
            raise ValueError(f"line {number}: expected context and four arguments")
        context, *args = map(canonical, trees)
        all_leaves = leaves(context) + sum((leaves(a) for a in args), [])
        if leaves(context).count("*") != 1 or sorted(all_leaves) != ["*", "x"] + ["y"] * 9:
            raise ValueError(f"line {number}: invalid context or multidegree")
        records.append((coefficient, context, sorted(args, key=repr)))
        literals.append(line)
    if len(records) != 482:
        raise ValueError(f"expected 482 records, found {len(records)}")
    return records, hashlib.sha256("\n".join(literals).encode()).hexdigest()


def tex_tree(tree, block):
    if isinstance(tree, str):
        return block if tree == "*" else tree
    return r"\left(" + tex_tree(tree[0], block) + r"\cdot " + tex_tree(tree[1], block) + r"\right)"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", nargs="?", type=Path,
                        default=Path(__file__).resolve().with_name("verify_e9.m2"))
    args = parser.parse_args()
    records, digest = read_records(args.source.read_text())
    print("% Derived from repository certificate; this exporter performs no manuscript comparison.")
    print(f"% SHA-256 of literal record lines (joined by LF): {digest}")
    print(r"\begin{align*}")
    for index, (c, context, arguments) in enumerate(records):
        block = r"t_4\left(" + ",".join(tex_tree(a, "") for a in arguments) + r"\right)"
        factor = rf"\frac{{{abs(c.numerator)}}}{{{c.denominator}}}"
        prefix = r"e_9(x,y) &= " if index == 0 else r"&\quad {} "
        sign = "- " if c < 0 else ("" if index == 0 else "+ ")
        print(prefix + sign + factor + r"\," + tex_tree(context, block) + r" \\")
    print(r"\end{align*}")


if __name__ == "__main__":
    main()
