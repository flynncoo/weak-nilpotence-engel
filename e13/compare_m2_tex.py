#!/usr/bin/env python3
"""Compare the literal SC table in M2 with the table/registers in LaTeX.

Standard library only. Neither input is executed. This understands the export
formats in this folder, not arbitrary M2 programs or TeX macro expansion. It
does not read algebra.json.gz, the generator, the PDF, or its manifests.
Omitted products/coefficients mean zero; products are commutative.
"""

import argparse
from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
import re
import sys

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)  # These exact integers exceed 4,300 digits.

ROOT = Path(__file__).resolve().parent


class ParseError(ValueError):
    pass


@dataclass
class Table:
    dimension: int
    coefficients: dict = field(default_factory=dict)
    locations: dict = field(default_factory=dict)
    products: set = field(default_factory=set)
    registers: dict = field(default_factory=dict)

    def product(self, i, j, where):
        if not (0 <= i <= j < self.dimension):
            raise ParseError(f"{where}: expected 0 <= i <= j < {self.dimension}")
        pair = (i, j)
        if pair in self.products:
            raise ParseError(f"{where}: duplicate product b_{i} b_{j}")
        self.products.add(pair)
        return pair

    def term(self, pair, k, numerator, denominator, where):
        if not 0 <= k < self.dimension:
            raise ParseError(f"{where}: output basis index {k} out of range")
        if denominator <= 0:
            raise ParseError(f"{where}: denominator must be positive")
        key = (*pair, k)
        if key in self.coefficients:
            raise ParseError(f"{where}: duplicate coefficient of b_{k}")
        self.coefficients[key] = (numerator, denominator)
        self.locations[key] = where


def parse_m2(source):
    source = re.sub(r"--[^\n]*", "", source)
    dimensions = re.findall(r"(?m)^\s*n\s*=\s*(\d+)\s*;", source)
    if len(dimensions) != 1 or int(dimensions[0]) < 1:
        raise ParseError("M2: expected one positive literal dimension n")
    table = Table(int(dimensions[0]))
    assignment = re.compile(
        r"\bSC\s*#\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)\s*=\s*"
        r"hashTable\s*\{([^{}]*)\}\s*;"
    )
    entry = re.compile(r"\s*(\d+)\s*=>\s*([+-]?\d+)\s*/\s*([+-]?\d+)\s*")
    for match in assignment.finditer(source):
        where = f"M2 line {source.count(chr(10), 0, match.start()) + 1}"
        pair = table.product(int(match[1]), int(match[2]), where)
        for item in match[3].split(",") if match[3].strip() else []:
            term = entry.fullmatch(item)
            if not term:
                raise ParseError(f"{where}: invalid structure constant: {item[:80]!r}")
            table.term(pair, *map(int, term.groups()), where)
    remainder = assignment.sub("", source)
    if re.search(r"\bSC\s*#\s*\(", remainder):
        raise ParseError("M2: unparsed SC assignment or unsupported indexed access")
    if not table.products:
        raise ParseError("M2: no structure constants found")
    return table


def uncomment_tex(source):
    # A percent sign starts a comment unless preceded by an odd number of
    # backslashes. Preserve newlines so diagnostics retain source line numbers.
    lines = []
    for line in source.splitlines():
        for match in re.finditer("%", line):
            pos = match.start()
            backslashes = len(line[:pos]) - len(line[:pos].rstrip("\\"))
            if backslashes % 2 == 0:
                line = line[:pos]
                break
        lines.append(line)
    return "\n".join(lines)


def unique_position(source, marker):
    if source.count(marker) != 1:
        raise ParseError(f"TeX: expected exactly one {marker}")
    return source.index(marker)


NUMERATOR_HEADING = re.compile(
    r"\\Needspace\{4\\baselineskip\}\\par\\addvspace\{6pt\}\\noindent"
    r"\\textbf\{\$C_\{(\d+)\}=N_\{(\d+)\}/"
    r"\\hyperref\[D:(\d+)\]\{D_\{(\d+)\}\}\$\."
    r"Numerator\$N_\{(\d+)\}\$:\}\\label\{C:(\d+)\}\\par\\nobreak"
)
DENOMINATOR_HEADING = re.compile(
    r"\\Needspace\{4\\baselineskip\}\\par\\addvspace\{6pt\}\\noindent"
    r"\\textbf\{Denominator\$D_\{(\d+)\}\$:\}"
    r"\\label\{D:(\d+)\}\\par\\nobreak"
)


def parse_register(lines, kind):
    result = {}
    pending = None
    chunks = []
    closed = False

    def finish():
        if pending is None:
            return
        index, denominator, where = pending
        digits = "".join(chunks)
        if not re.fullmatch(r"-?[0-9]+", digits):
            raise ParseError(f"{where}: missing or invalid integer digit rows")
        value = int(digits)
        if kind == "D" and value <= 0:
            raise ParseError(f"{where}: denominator must be positive")
        result[index] = (value, denominator, where)

    heading = NUMERATOR_HEADING if kind == "C" else DENOMINATOR_HEADING
    for number, line in lines:
        compact = re.sub(r"\s+", "", line)
        where = f"TeX line {number} ({kind} register)"
        match = heading.fullmatch(compact)
        if match:
            if closed:
                raise ParseError(f"{where}: register entry after endgroup")
            finish()
            indices = list(map(int, match.groups()))
            index = indices[0]
            if kind == "C":
                c, n, d, printed_d, printed_n, label = indices
                if c != n or c != printed_n or c != label or d != printed_d:
                    raise ParseError(f"{where}: inconsistent numerator/denominator reference")
                denominator = d
            else:
                if indices[0] != indices[1]:
                    raise ParseError(f"{where}: inconsistent denominator label")
                denominator = None
            if index < 1 or index in result:
                raise ParseError(f"{where}: duplicate or invalid {kind}_{index}")
            pending = (index, denominator, where)
            chunks = []
            continue
        digits = re.fullmatch(r"\\digitsrow\{(-?[0-9]+)\}", line.strip())
        if digits:
            if pending is None or closed:
                raise ParseError(f"{where}: digits outside a register entry")
            chunks.append(digits[1])
        elif compact in (r"\endgroup", r"\endgroup\end{document}"):
            finish()
            pending = None
            closed = True
        elif compact:
            # Introductory prose is allowed only before the first entry.
            # Unknown commands or prose inside an integer must never be skipped.
            if pending is not None or closed or any(
                token in compact for token in (r"\digitsrow", r"\Needspace", r"\label", r"\textbf")
            ):
                raise ParseError(f"{where}: unrecognized register content: {line[:80]!r}")
    finish()
    if not result:
        raise ParseError(f"TeX: empty {kind} register")
    return result


TERM = re.compile(
    r"(?P<sign>[+-]?)"
    r"(?:(?P<factor>"
    r"\\hyperref\[C:(?P<link>\d+)\]\{C_\{(?P<printed>\d+)\}\}"
    r"|\\frac\{(?P<num>[+-]?\d+)\}\{(?P<den>\d+)\}"
    r"|(?P<integer>\d+)"
    r")(?:\\,)?)?b_\{(?P<basis>\d+)\}"
)


def parse_tex(source, dimension):
    source = uncomment_tex(source)
    markers = [r"\section{Multiplication table}", r"\end{longtable}",
               r"\section{Numerator register}", r"\section{Denominator register}"]
    positions = [unique_position(source, marker) for marker in markers]
    if positions != sorted(positions):
        raise ParseError("TeX: sections out of order")
    # Strip the clearpage immediately before the next section, preserving lines.
    numerator_text = source[positions[2] + len(markers[2]):positions[3]]
    numerator_text = re.sub(r"\\clearpage\s*$", "", numerator_text)
    denominator_text = source[positions[3] + len(markers[3]):]
    denominator_text = re.sub(r"^\\label\{denominators\}", "", denominator_text)
    numerator_lines = enumerate(numerator_text.splitlines(), source.count("\n", 0, positions[2]) + 1)
    denominator_lines = enumerate(denominator_text.splitlines(), source.count("\n", 0, positions[3]) + 1)
    numerators = parse_register(numerator_lines, "C")
    denominators = parse_register(denominator_lines, "D")
    resolved = {}
    used_d = set()
    for index, (value, d, where) in numerators.items():
        if d not in denominators:
            raise ParseError(f"{where}: undefined D_{d}")
        resolved[index] = (value, denominators[d][0])
        used_d.add(d)
    table = Table(dimension)
    table.registers = {"numerators": len(numerators), "denominators": len(denominators)}
    used_c = set()
    current = None
    row_pattern = re.compile(r"(?:\$(b_\{\d+\}b_\{\d+\})\$)?\s*&\s*\$(.*?)\$\s*\\\\")
    table_text = source[positions[0] + len(markers[0]):positions[1]]
    for number, line in enumerate(table_text.splitlines(), source.count("\n", 0, positions[0]) + 1):
        line = line.strip()
        where = f"TeX line {number}"
        if not line:
            continue
        if line == r"\addlinespace[2pt]":
            current = None
            continue
        if line in (
            r"\begin{longtable}{@{}p{0.14\textwidth}p{0.82\textwidth}@{}}",
            r"\toprule Product & Value \\ \midrule\endfirsthead",
            r"\toprule Product & Value (continued) \\ \midrule\endhead",
            r"\bottomrule\endfoot",
        ):
            continue
        row = row_pattern.fullmatch(line)
        if not row:
            raise ParseError(f"{where}: unrecognized product row: {line[:100]!r}")
        continuation = row[1] is None
        if not continuation:
            i, j = map(int, re.findall(r"\d+", row[1]))
            current = table.product(i, j, where)
        elif current is None:
            raise ParseError(f"{where}: continuation without a product")
        rhs = re.sub(r"\s+", "", row[2])
        pos = 0
        if not rhs:
            raise ParseError(f"{where}: empty product expression")
        while pos < len(rhs):
            term = TERM.match(rhs, pos)
            if term is None or ((pos or continuation) and not term["sign"]):
                raise ParseError(f"{where}: invalid term near {rhs[pos:pos+100]!r}")
            location = where
            if term["link"] is not None:
                c = int(term["link"])
                if c != int(term["printed"]):
                    raise ParseError(f"{where}: coefficient link and printed index disagree")
                if c not in resolved:
                    raise ParseError(f"{where}: undefined C_{c}")
                a, b = resolved[c]
                used_c.add(c)
                location += f", C_{c} / D_{numerators[c][1]}"
            elif term["num"] is not None:
                a, b = int(term["num"]), int(term["den"])
            else:
                a, b = int(term["integer"] or 1), 1
            if term["sign"] == "-":
                a = -a
            table.term(current, int(term["basis"]), a, b, location)
            pos = term.end()
    if used_c != numerators.keys() or used_d != denominators.keys():
        raise ParseError("TeX: unused register entries (possibly a changed or missing reference): "
                         f"C={sorted(numerators.keys() - used_c)[:20]}, "
                         f"D={sorted(denominators.keys() - used_d)[:20]}")
    if not table.products:
        raise ParseError("TeX: no products found")
    return table


def short_rational(value):
    def short(n):
        s = str(n)
        return s if len(s) <= 60 else f"{s[:24]}...{s[-24:]} ({len(s.lstrip('-'))} digits)"
    return f"{short(value[0])} / {short(value[1])}"


def compare(m2, tex):
    differences = []
    for key in sorted(m2.coefficients.keys() | tex.coefficients.keys()):
        left = m2.coefficients.get(key, (0, 1))
        right = tex.coefficients.get(key, (0, 1))
        # Cross multiplication is exact, including for unreduced fractions.
        if left[0] * right[1] != right[0] * left[1]:
            differences.append({
                "product": list(key[:2]), "output_basis": key[2],
                "m2": short_rational(left), "tex": short_rational(right),
                "m2_location": m2.locations.get(key, "omitted (zero)"),
                "tex_location": tex.locations.get(key, "omitted (zero)"),
            })
    return differences


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("m2", nargs="?", type=Path, default=ROOT / "verify_e13.m2")
    parser.add_argument("tex", nargs="?", type=Path, default=ROOT / "multiplication_table.tex")
    parser.add_argument("--report", type=Path, help="write a JSON report with input SHA-256 hashes")
    args = parser.parse_args(argv)
    report = {"status": "ERROR", "method": "Independent literal parsing; exact integer cross multiplication"}
    try:
        sources = []
        for label, path in (("m2", args.m2), ("tex", args.tex)):
            data = path.read_bytes()
            report[label] = {"path": str(path.resolve()), "sha256": hashlib.sha256(data).hexdigest()}
            sources.append(data.decode("utf-8"))
        m2 = parse_m2(sources[0])
        tex = parse_tex(sources[1], m2.dimension)
        differences = compare(m2, tex)
        report.update(status="FAIL" if differences else "PASS", dimension=m2.dimension,
                      unordered_products_checked=m2.dimension * (m2.dimension + 1) // 2,
                      differences=differences, registers=tex.registers)
        for label, table in (("m2", m2), ("tex", tex)):
            nonzero = {key for key, value in table.coefficients.items() if value[0]}
            report[label].update(nonzero_products=len({key[:2] for key in nonzero}),
                                 nonzero_coefficients=len(nonzero))
        code = 1 if differences else 0
        if differences:
            print(f"FAIL: {len(differences)} coefficients differ.")
            for item in differences[:20]:
                i, j = item["product"]
                print(f"  b_{i} b_{j}, coefficient of b_{item['output_basis']}:")
                print(f"    M2:  {item['m2']} [{item['m2_location']}]")
                print(f"    TeX: {item['tex']} [{item['tex_location']}]")
        else:
            print(f"PASS: all {report['m2']['nonzero_coefficients']} nonzero coefficients "
                  f"in {report['m2']['nonzero_products']} products agree exactly.")
            print(f"Checked all {report['unordered_products_checked']} unordered basis products, "
                  "including omitted zero products.")
            print(f"Resolved {tex.registers['numerators']} numerator entries and "
                  f"{tex.registers['denominators']} denominator entries.")
    except (ParseError, OSError, UnicodeError) as exc:
        report["error"] = str(exc)
        print(f"ERROR: {exc}", file=sys.stderr)
        code = 2
    if args.report:
        args.report.write_text(json.dumps(report, indent=2) + "\n")
        print(f"Report: {args.report}")
    return code


if __name__ == "__main__":
    sys.exit(main())
