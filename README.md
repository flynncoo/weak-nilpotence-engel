# weak-nilpotence-engel

This repo contains the Macauley2 code that is used to check the main claims of the paper "On a conjecture of Dotsenko on weak nilpotence and the Engel identity."
The contents of this repo are as follows:
1. main.pdf is the paper itself.
2. A verify_e7.m2 script: this checks the t_4=0 identity for the algebra A appearing in the paper.
3. A verify_e8.m2 script: this checks the  t_4=0 identity for the algebra A appearing in the paper.
4. A verify_e9.m2 script: this is a machine readable script showing that the 9-Engel identity can be deduced from the t_4=0 identity.
5. e13 is a folder containing three files all pertaining to a 111 dimensional algebra $A_{111}$ satisfying $t_5=0$ which but not the 14-Engel identity:
   i) multiplication_table.tex and multiplication_table.pdf provide the multiplication table of this example.
   ii) verify_e13.m2 provides a Macauley2 file checking the counterexample.
   iii) compare_m2_tex.py is a python file which checks that the multiplication_table.tex and verify_e13.m2 study the same algebra.
