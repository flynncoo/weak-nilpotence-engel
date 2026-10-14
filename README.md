# weak-nilpotence-engel

Exact computational verification accompanying “On a conjecture of Dotsenko
on weak nilpotence and the Engel identity”. The scripts verify supplied
examples and a supplied certificate; they do not reproduce the original
search for algebras or the discovery of the certificate. The paper is supplied
as `main.pdf`; its manuscript LaTeX source is not present in this checkout.

All algebras are commutative and nonassociative. Products retain their binary
parentheses throughout. We use `e_0(x,y)=x` and
`e_{k+1}(x,y)=e_k(x,y)*y`: `e_k` has exactly `k` copies of `y` and total degree
`k+1`. The polynomial `t_n` sums all distinct commutative nonassociative
multilinear monomials on **distinct argument slots, before substitution**.
Coincident argument values do not remove summands or their multiplicities.
There are 15 such trees for `t_4` and 105 for `t_5`.

| Mathematical claim / data check | Script |
| --- | --- |
| A_17: `t_4=0`, `e_7(b_5,b_0)=(1/8)b_16`, `t_5(b_0,b_0,b_0,b_0,b_0)=30b_4`; structure constant denominators are powers of 2 | `verify_e7.m2` |
| A_22: `t_4=0`, `e_8(b_5,b_0)=-(1/16)b_21`; structure constant denominators are powers of 2 | `verify_e8.m2` |
| Universal implication `t_4=0` implies `e_9=0`; input coefficient denominator audit | `verify_e9.m2` |
| A_111: `t_5=0`, `e_13(b_5,b_0)=b_110`, `e_14(b_5,b_0)=0`; grading implies `e_14=0` identically | `e13/verify_e13.m2` (extended check) |
| Exact equality of the A_111 M2 and LaTeX multiplication tables | `e13/compare_m2_tex.py` |
| LaTeX derived from the repository's e_9 certificate | `export_e9_tex.py` |
| Exact comparison of the paper PDF's A_17/A_22 tables and 482 appendix certificate records with M2 | `compare_paper.py` (optional PDF audit) |
| Labelled-tree definitions and rejection of malformed/incorrect temporary copies | `test_verifiers.py` |

**Main reproduction commands.** Run from the repository root with Macaulay2
and Python 3 on `PATH`. The Python commands in this main group use only the
standard library. The optional PDF audit below additionally uses `pypdf`.

```sh
M2 --version
python3 --version
M2 --script verify_e7.m2
M2 --script verify_e8.m2
M2 --script verify_e9.m2
python3 e13/compare_m2_tex.py
PYTHONDONTWRITEBYTECODE=1 python3 test_verifiers.py
```

Each verifier exits with a nonzero status on a failed required check.
Expected success messages include:

```text
PASS: structure constant denominators are powers of 2
PASS: t4 = 0 on all 4845 sorted basis quadruples
PASS: e_7(b_5,b_0) = (1/8) b_16
PASS: labelled tree counts t4 = 15, t5 = 105
PASS: t5(b_0,b_0,b_0,b_0,b_0) = 30 b_4
```

For A_22 the corresponding count is 12650 and the witness message is
`PASS: e_8(b_5,b_0) = (-1/16) b_21`. For e_9 expect 482 records,
input denominator LCM 252000, one surviving monomial with coefficient 1,
and `CERTIFICATE VERIFIES (sum == e_9 exactly): true`. The LCM is computed
from reduced input coefficients; 252000 is an observed value, not a value
forced by the verifier. A count different from the manuscript's stated 482
is an error.

The table comparison should report 2749 nonzero coefficients in 469 products
agreeing exactly, checking all 6216 unordered basis products (including
omitted zeros), with 2516 numerator and 329 denominator register entries.
It independently parses literal M2 data and the LaTeX source, comparing
rational values by exact integer cross multiplication. It does **not** check
`t_5`, the Engel witness, the PDF rendering, or the e_9 appendix. The existing
`e13/multiplication_table.pdf` is a presentation of the table; the comparison
uses `e13/multiplication_table.tex`.

**Verification methods and characteristics.** For the finite-dimensional
examples, the supplied table defines bilinear multiplication over the
rationals. A symmetric multilinear identity is determined by its values on
basis tuples. Symmetry permits sorting the tuple, while multilinearity
extends the result to all arguments. Repeated basis indices must be included:
they are not implied by checking tuples of distinct basis elements.
The small verifiers check every nondecreasing basis quadruple. A_17's `t_5`
evaluator first enumerates labelled unordered binary trees using root
bipartitions, choosing the side containing the least label exactly once;
it then substitutes the five arguments and sums all 105 values.

The small tables' reduced denominators contain only powers of 2. Here
`Z[1/2]=Z[1/4]`, agreeing with Remark 2.9 of the paper. Their
identities are therefore valid over `Z[1/2]`, and specialization to a field
of characteristic greater than 2 preserves `t_4=0` and the displayed
nonzero Engel witnesses. This establishes the A_17 and A_22 counterexamples
in those characteristics (and characteristic zero). The witness `30b_4`
proves `t_5` nonvanishing in characteristic zero and characteristics greater
than 2 other than 3 and 5; it alone proves nothing about `t_5` nonvanishing
in characteristics 3 or 5.

For the universal implication, `verify_e9.m2` stores 482 records, each a
rational coefficient, a multiplication context containing exactly one `*`
placeholder, and four substituted trees. Before expansion or cancellation it
checks **every input coefficient's reduced denominator** for prime factors
outside `{2,3,5,7}`, computes their LCM, and checks binary tree validity,
placeholder count, and total multidegree `(1,9)`. It checks that the 15
`t_4` trees are distinct and correctly labelled, expands every record into
all 15 summands, inserts each into its context, and accumulates exact
rational coefficients. Canonicalization sorts the two children of each
node using commutativity only. Precisely the left-comb `e_9` must remain,
with coefficient 1.

Equivalently, each substituted/contextualized `t_4` consequence is a column
of a relation matrix `M`, the stored coefficients form a vector `lambda`,
and the verifier checks `M*lambda=v_e9` directly without constructing `M`
or searching for a new certificate. The free commutative nonassociative
tree basis has integral structure constants. Because every input scalar
lies in `Z[1/210]`, exact coefficient equality over `Q` also gives equality
over `Z[1/210]` (which embeds in `Q`). Specializing establishes the same
implication over every field of characteristic greater than 7, as well as
characteristic zero. The input denominator audit is essential; auditing
only the final coefficient 1 would not justify specialization.

**Extended A_111 check and Engel indexing.** This check uses very large
rational coefficients and is separate from the main checks. From the
repository root run:

```sh
M2 --script e13/verify_e13.m2
```

Alternatively, from `e13/`, run `M2 --script verify_e13.m2`. The script is
self-contained and reads no files relative to the working directory. Existing
`e13/` paths are retained; the implemented exponent is determined by the
loop, which performs 13 multiplications by `y` starting from `x=b_5`, with
`y=b_0`. The exact result is `e_13(b_5,b_0)=b_110`. One further multiplication
gives `e_14(b_5,b_0)=0`.

The script defines a 111-dimensional algebra and explicitly writes the 105
labelled summands of `t_5`. Its rigorous reduction checks the positive basis
grading and the decomposition `B=span(b_0,...,b_4)`,
`M=span(b_5,...,b_110)`, with `B*B` contained in `B`, `B*M` contained in `M`,
and `M*M=0`. Any tree with two or more `M` arguments vanishes: at their
first common ancestor both child values lie in `M`. Products of total
degree greater than 14 vanish by the checked grading. It then evaluates
all remaining sorted basis quintuples, including repetitions: 1067 cases.
The final required success line is
`PASS: A_111 t5 identity, all 1067 potentially nonzero basis cases`.
Loading the table or printing the witness is **not** a completed identity
verification.

The introduction (page 2) and Theorem 2.8 (page 5) of `main.pdf` state
failure of **13-Engel**, in agreement with the implementation. This resolves
the earlier README's indexing discrepancy. The verified positive grading,
with minimum degree 1 and maximum 14, also implies every degree-15 product
is zero. Thus `e_14=0` **identically**, beyond checking one pair. No
multiplication-table data were changed to obtain agreement with the paper.
No characteristic claim for A_111 follows from the small-table or certificate
audits: its structure constants need a separate denominator audit before
such a claim can be made.

**Printed data and provenance.** `main.pdf` is now available. The exact
PDF comparison command is:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 compare_paper.py
```

This optional audit uses `pypdf` to extract the paper's text. It understands
the current PDF layout and notation, not arbitrary PDF mathematics. It
compares the A_17 table on page 3 (37 nonzero products, 44 coefficients)
and the A_22 table on page 4 (49 products, 69 coefficients) with the M2
literals using exact fractions. It parses all 482 Appendix A records on
pages 5–18 and compares their coefficients, multiplication contexts, and
four substituted arguments **as multisets**, preserving record multiplicity.
It allows only record reordering, commutativity at each binary node, and
symmetry of `t_4` arguments. It preserves association and rejects ambiguous
products with more than two unparenthesized factors. It reports a nonzero
exit status on a mismatch or unsupported notation, and prints the PDF hash.
This is equality of the certificate data, a separate check from expansion
to `e_9` in Macaulay2. It does not verify every prose claim or replace the
extended A_111 identity check. The A_111 table is supplied separately and
continues to be checked by `e13/compare_m2_tex.py`.

The PDF audit passed with `pypdf` **6.10.2** on 2026-10-14 for `main.pdf`
with SHA-256:

```text
88bdce7dddc24f58443864a817dff000916ed0edcb78645ffab6da91716e4ece
```

The manuscript LaTeX source remains absent, so source-level agreement has
not been checked. To obtain a deterministic LaTeX fragment directly from
the machine-readable records, without a second copied coefficient list:

```sh
python3 export_e9_tex.py > /tmp/weak-nilpotence-e9-certificate.tex
```

The fragment records the SHA-256 of the literal certificate record lines
(joined by LF, no final LF), preserves record order and multiplicity, and
normalizes only commutative child order and symmetric `t_4` argument order.
It is labelled as derived from the repository certificate; the exporter
itself performs no manuscript comparison. It requires `amsmath` when
included in a LaTeX document. No paper or appendix is replaced.

The MIT licence in `LICENSE` and existing provenance comments are preserved.
The original comments attributing generation to Claude Code and a line-by-line
check to Oisín concern the original versions; they do not claim an author
audit of the modifications here.

**Testing record (2026-10-14).** Tests used Macaulay2 **1.26.06** and Python
**3.14.6**, on macOS **26.7.1**, Darwin **arm64**. Before edits, the three main
M2 commands and the Python table comparison all passed. After edits:

| Check | Observed outcome |
| --- | --- |
| `M2 --script verify_e7.m2` | PASS: all 4845 cases, exact e_7 and t_5 witnesses, tree counts and denominator audit |
| `M2 --script verify_e8.m2` | PASS: all 12650 cases, exact e_8 witness and denominator audit |
| `M2 --script verify_e9.m2` | PASS: 482 records, denominator LCM 252000, exact reconstruction |
| `python3 e13/compare_m2_tex.py` | PASS before and after edits: all coefficients and omitted zeros agree |
| `PYTHONDONTWRITEBYTECODE=1 python3 test_verifiers.py` | PASS: tree definitions, deterministic export, all 10 negative fixtures |
| `python3 export_e9_tex.py > /private/tmp/weak-nilpotence-e9-certificate.tex` | PASS: generated fragment from all 482 records |
| Earlier A_111 attempts | INTERRUPTED after 333.64 and 311.23 seconds; superseded by the completed run below |
| `M2 --script e13/verify_e13.m2` | PASS: all 1067 potentially nonzero basis cases; grading and exact e_13/e_14 witnesses; exit status 0; 580.31 seconds |
| `PYTHONDONTWRITEBYTECODE=1 python3 compare_paper.py` | PASS: both printed small tables and all 482 appendix records agree exactly |
| Manuscript LaTeX source comparison | NOT RUN: source absent; PDF data comparison passed |

The full A_111 check completed successfully on 2026-10-14 using the
Macaulay2 version and environment above. The exact timed command was:

```sh
/usr/bin/time -p M2 --script e13/verify_e13.m2 > /private/tmp/weak-nilpotence-e13-full.log 2>&1
```

It exited with status **0**, after checking all 1067 required quintuples,
and printed `t5 == 0 identically (sorted quintuples; grading and M*M = 0): true`
and the final success assertion. Measured times were **580.31 seconds real**
(about 9 minutes 40 seconds), 598.59 seconds user CPU, and 2.28 seconds system
CPU. The exact witness checks also passed: `e_13(b_5,b_0)=b_110` and
`e_14(b_5,b_0)=0`. The verified grading establishes `e_14=0` identically.
Captured output, environment, command, exit status, and the verifier's SHA-256
are retained in [e13/verification-output.txt](e13/verification-output.txt).
This completed run supersedes the earlier interrupted attempts; those partial
attempts were not successful full verifications. Runtimes depend on the
machine and software environment.

The PDF comparator was also checked with temporary extracted-text fixtures:
an altered appendix coefficient and an altered small-table coefficient were
both rejected, as was an ambiguously parenthesized product. The paper's
15-term `t_4` definition and the four-term `t_3` identity on page 4 were
additionally checked by exact tree expansion in a one-off audit. The e_9
M2 verifier was rerun after the PDF comparison and passed again.

The temporary negative fixtures require both a nonzero exit status and the
appropriate diagnostic. They alter expected Engel/t_5 vectors, a small-table
denominator, a certificate coefficient, an input denominator containing 11,
a placeholder, tree arity, multidegree, and the record count. The structural
tests independently check the explicit `t_4`/`t_5` formulas against exhaustive
labelled-tree enumeration. They do not substitute for the full A_111 run.

To identify the precise source used, record:

```sh
git rev-parse HEAD
git status --short
git diff --binary > /tmp/weak-nilpotence-local-changes.patch
git ls-files --others --exclude-standard
```

A commit hash identifies committed files only. Also retain the diff and any
untracked new files when reproducing an uncommitted checkout. These changes
are left uncommitted for review; no release, DOI, or hash for them is claimed.
For a referee archive, the author should review the changes and choose and
record an exact committed revision or future pinned release. The supplied PDF resolves the 13-Engel indexing and
agrees with the stored e_9 appendix certificate.
