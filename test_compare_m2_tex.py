"""Mutation tests for the independent M2/TeX transcription checker."""

import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from compare_m2_tex import ParseError, compare, main, parse_m2, parse_tex


M2 = """-- A small table, with intentionally unreduced fractions.
n = 6;
SC = new MutableHashTable;
SC#(0,0) = hashTable{1 => 2/2, 2 => -2/3, 3 => 7/5, 4 => 4/1};
SC#(0,1) = hashTable{5 => -1/1};
"""

TEX = r"""\documentclass{article}
\newcommand{\digitsrow}[1]{\noindent\texttt{#1}\par}
\begin{document}
Ignored introductory prose, including an escaped percent: \%.
\section{Multiplication table}
\begin{longtable}{@{}p{0.14\textwidth}p{0.82\textwidth}@{}}
\toprule Product & Value \\ \midrule\endfirsthead
\toprule Product & Value (continued) \\ \midrule\endhead
\bottomrule\endfoot
$b_{0}b_{0}$ & $b_{1} - \frac{2}{3}\,b_{2}$ \\
 & $+ \hyperref[C:1]{C_{1}}\,b_{3} + 4\,b_{4}$ \\
\addlinespace[2pt]
$b_{0}b_{1}$ & $- b_{5}$ \\ % A comment is not a coefficient.
\addlinespace[2pt]
\end{longtable}
\clearpage\section{Numerator register}
Concatenate the digit rows.
\begingroup\fontsize{8.5}{10.5}\selectfont
\Needspace{4\baselineskip}\par\addvspace{6pt}\noindent\textbf{$C_{1}=N_{1}/\hyperref[D:1]{D_{1}}$. Numerator $N_{1}$:}\label{C:1}\par\nobreak
\digitsrow{1}
\digitsrow{4}
\endgroup\clearpage\section{Denominator register}\label{denominators}
Positive integer denominators.
\begingroup\fontsize{8.5}{10.5}\selectfont
\Needspace{4\baselineskip}\par\addvspace{6pt}\noindent\textbf{Denominator $D_{1}$:}\label{D:1}\par\nobreak
\digitsrow{10}
\endgroup\end{document}
"""


class ComparisonTests(unittest.TestCase):
    def differences(self, tex=TEX, m2=M2):
        table = parse_m2(m2)
        return compare(table, parse_tex(tex, table.dimension))

    def test_equivalent_fractions_units_signs_and_continuation(self):
        self.assertEqual(self.differences(), [])

    def test_arbitrarily_large_register_integer(self):
        digits = "1234567890" * 1000
        m2 = M2.replace("3 => 7/5", f"3 => {digits}/10")
        tex = TEX.replace("\\digitsrow{1}\n\\digitsrow{4}", f"\\digitsrow{{{digits}}}")
        self.assertEqual(self.differences(tex, m2), [])

    def test_changed_digit_sign_inline_fraction_and_output_basis(self):
        mutations = [
            (r"\digitsrow{4}", r"\digitsrow{5}"),
            (r"\digitsrow{10}", r"\digitsrow{11}"),
            (r"\digitsrow{1}", r"\digitsrow{-1}"),
            (r"\frac{2}{3}", r"\frac{2}{5}"),
            (r"4\,b_{4}", r"5\,b_{4}"),
            ("$- b_{5}$", "$b_{5}$"),
            ("$- b_{5}$", "$- b_{4}$"),
            (r" + 4\,b_{4}", ""),
        ]
        for old, new in mutations:
            with self.subTest(mutation=(old, new)):
                self.assertTrue(self.differences(TEX.replace(old, new)))

    def test_missing_and_extra_products(self):
        row = next(line for line in TEX.splitlines() if line.startswith("$b_{0}b_{1}$"))
        self.assertTrue(self.differences(TEX.replace(row, "")))
        self.assertTrue(self.differences(TEX.replace(row, row + "\n" + row.replace("b_{0}b_{1}", "b_{1}b_{1}"))))

    def test_m2_change_is_detected(self):
        self.assertTrue(self.differences(m2=M2.replace("7/5", "8/5")))

    def test_omitted_terms_equal_explicit_zeros(self):
        self.assertEqual(self.differences(m2=M2 + "SC#(1,1) = hashTable{5 => 0/1};"), [])

    def test_malformed_or_inconsistent_tex_is_rejected(self):
        mutations = [
            (r"\hyperref[C:1]{C_{1}}", r"\hyperref[C:2]{C_{2}}"),
            (r"\hyperref[C:1]{C_{1}}", r"\hyperref[C:1]{C_{2}}"),
            (r"\hyperref[D:1]{D_{1}}", r"\hyperref[D:2]{D_{2}}"),
            (r"\hyperref[D:1]{D_{1}}", r"\hyperref[D:1]{D_{2}}"),
            (r"\label{C:1}", r"\label{C:2}"),
            (r"\label{D:1}", r"\label{D:2}"),
            (r"Numerator $N_{1}$", r"Numerator $N_{2}$"),
            (r"\digitsrow{10}", r"\digitsrow{0}"),
            (r"\frac{2}{3}", r"\frac{2}{0}"),
            (r"\digitsrow{4}", r"\digitsrow{-4}"),
            (r"\digitsrow{4}", r"\digitsrow{4x}"),
            (r"4\,b_{4}", r"4\,b_{99}"),
            (r"4\,b_{4}", r"4\,b_{3}"),
            (r"4\,b_{4}", r"4\,b_{4} + \unknown{2}"),
            (r" + 4\,b_{4}", r" 4\,b_{4}"),
            (r" & $+ \hyperref", r" & $\hyperref"),
            ("$b_{0}b_{0}$", ""),
            ("$b_{0}b_{1}$", "$b_{0}b_{0}$"),
            (r"\hyperref[C:1]{C_{1}}", r"\frac{7}{5}"),  # orphaned C_1
        ]
        for old, new in mutations:
            with self.subTest(mutation=(old, new)), self.assertRaises(ParseError):
                self.differences(TEX.replace(old, new))

    def test_duplicate_register_definitions(self):
        for kind in ("C", "D"):
            lines = TEX.splitlines()
            start = next(i for i, line in enumerate(lines) if f"\\label{{{kind}:1}}" in line)
            end = start + 1
            while lines[end].startswith(r"\digitsrow"):
                end += 1
            lines[end:end] = lines[start:end]
            with self.subTest(kind=kind), self.assertRaises(ParseError):
                self.differences("\n".join(lines))

    def test_malformed_m2_is_rejected(self):
        variants = [
            M2 + "SC#(0,0) = hashTable{1 => 1/1};",
            M2.replace("2/2", "2/0"),
            M2.replace("2/2", "mystery/2"),
            M2.replace("4 => 4/1", "3 => 4/1"),
            M2.replace("4 => 4/1", "99 => 4/1"),
            M2.replace("SC#(0,0)", "SC#(0,99)"),
            M2.replace("hashTable", "otherTable"),
        ]
        for variant in variants:
            with self.subTest(m2=variant), self.assertRaises(ParseError):
                parse_m2(variant)

    def test_cli_exit_codes_and_reports(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            m2, tex, report = [base / name for name in ("a.m2", "a.tex", "report.json")]
            m2.write_text(M2)
            for source, code, status in ((TEX, 0, "PASS"),
                                         (TEX.replace("$- b_{5}$", "$b_{5}$"), 1, "FAIL"),
                                         (TEX.replace(r"\digitsrow{10}", r"\digitsrow{x}"), 2, "ERROR")):
                tex.write_text(source)
                with self.subTest(status=status), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(main([str(m2), str(tex), "--report", str(report)]), code)
                    data = json.loads(report.read_text())
                    self.assertEqual(data["status"], status)
                    self.assertEqual(len(data["m2"]["sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
