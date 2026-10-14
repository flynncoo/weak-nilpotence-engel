-- Note from Oisín: This verification code was generated with Claude Code using the Opus 4.8 model.
-- I checked it carefully, line by line, and vouch for its fidelity.
-- Self-contained Macaulay2 verifier: commutative nonassoc Q-algebra with
-- t_4 == 0 identically AND e_8(x,y) != 0  (8-Engel does NOT follow from t_4).
-- Run:  M2 --script verify_e8.m2
n = 22;
zeroV = toList(n:0/1);
e = i -> apply(n, k -> if k == i then 1/1 else 0/1);
SC = new MutableHashTable;
SC#(0,0) = hashTable{1 => 1/1};
SC#(0,1) = hashTable{2 => 1/1};
SC#(0,2) = hashTable{3 => -1/4};
SC#(0,3) = hashTable{4 => -4/1};
SC#(0,5) = hashTable{6 => 1/1};
SC#(0,6) = hashTable{8 => 1/1};
SC#(0,7) = hashTable{9 => 1/1};
SC#(0,8) = hashTable{10 => 1/1};
SC#(0,10) = hashTable{12 => -1/2, 14 => -1/2};
SC#(0,11) = hashTable{12 => 1/1};
SC#(0,12) = hashTable{16 => 1/1};
SC#(0,13) = hashTable{15 => -1/1};
SC#(0,14) = hashTable{16 => -2/1};
SC#(0,15) = hashTable{17 => -1/1};
SC#(0,16) = hashTable{18 => 2/1, 19 => 1/2, 17 => 1/2};
SC#(0,17) = hashTable{20 => -1/1};
SC#(0,18) = hashTable{20 => 1/4};
SC#(0,19) = hashTable{20 => -1/2};
SC#(0,20) = hashTable{21 => 1/2};
SC#(1,1) = hashTable{3 => 1/1};
SC#(1,2) = hashTable{4 => 1/1};
SC#(1,5) = hashTable{7 => 1/1};
SC#(1,6) = hashTable{11 => 1/1};
SC#(1,7) = hashTable{13 => 1/1};
SC#(1,8) = hashTable{14 => 1/1};
SC#(1,9) = hashTable{15 => 1/1};
SC#(1,10) = hashTable{16 => 1/1};
SC#(1,12) = hashTable{19 => -2/1, 18 => -4/1, 17 => -1/1};
SC#(1,13) = hashTable{18 => -16/1, 19 => -4/1, 17 => -4/1};
SC#(1,14) = hashTable{19 => 4/1, 18 => 14/1, 17 => 3/1};
SC#(1,16) = hashTable{20 => -1/2};
SC#(1,17) = hashTable{21 => 1/1};
SC#(1,18) = hashTable{21 => -1/4};
SC#(1,19) = hashTable{21 => 1/2};
SC#(2,5) = hashTable{10 => -2/1, 9 => -1/1, 11 => -1/1};
SC#(2,9) = hashTable{17 => 1/1};
SC#(2,10) = hashTable{18 => 1/1};
SC#(2,11) = hashTable{19 => 1/1};
SC#(2,14) = hashTable{20 => -1/2};
SC#(2,16) = hashTable{21 => 1/4};
SC#(3,5) = hashTable{13 => -4/1, 14 => -8/1, 12 => -4/1};
SC#(3,7) = hashTable{19 => 16/1, 17 => 12/1, 18 => 64/1};
SC#(3,8) = hashTable{17 => -6/1, 19 => -10/1, 18 => -32/1};
SC#(3,10) = hashTable{20 => 1/1};
SC#(3,12) = hashTable{21 => 1/1};
SC#(4,5) = hashTable{16 => 4/1, 15 => 1/1};
SC#(4,6) = hashTable{18 => -6/1, 19 => -2/1, 17 => -1/1};
SC#(4,8) = hashTable{20 => 1/2};
SC#(4,10) = hashTable{21 => -1/4};
mult = (u,v) -> (
  w := new MutableList from zeroV;
  for i from 0 to n-1 do if u#i != 0 then
    for j from 0 to n-1 do if v#j != 0 then (
      key := if i <= j then (i,j) else (j,i);
      if SC#?key then for k in keys(SC#key) do w#k = w#k + u#i*v#j*(SC#key)#k;
    );
  toList w);
x = e 5; y = e 0;
t4 = (a,b,c,d) -> mult(a, mult(b, mult(c, d))) + mult(a, mult(mult(b, c), d)) + mult(a, mult(mult(b, d), c)) + mult(mult(a, b), mult(c, d)) + mult(mult(a, c), mult(b, d)) + mult(mult(a, mult(b, c)), d) + mult(mult(mult(a, b), c), d) + mult(mult(mult(a, c), b), d) + mult(mult(a, d), mult(b, c)) + mult(mult(a, mult(b, d)), c) + mult(mult(mult(a, b), d), c) + mult(mult(mult(a, d), b), c) + mult(mult(a, mult(c, d)), b) + mult(mult(mult(a, c), d), b) + mult(mult(mult(a, d), c), b);
bad = 0;
for i from 0 to n-1 do for j from i to n-1 do for k from j to n-1 do for l from k to n-1 do
  if t4(e i, e j, e k, e l) != zeroV then bad = bad + 1;
<< "t4 == 0 identically (sorted quadruples): " << (bad == 0) << endl;
ee = x; for t from 1 to 8 do ee = mult(ee, y);
<< "e8(x,y) = " << ee << endl;
<< "8-Engel fails (e8 != 0): " << (ee != zeroV) << endl;
if bad != 0 or ee == zeroV then error "8-Engel verification failed";
