-- Note from Oisín: This verification code was generated with Claude Code using the Opus 4.8 model.
-- I checked it carefully, line by line, and vouch for its fidelity.
-- Macaulay2 verifier.  Run:  M2 --script verify_e7.m2
n = 17;
zeroV = toList(n:0/1);
e = i -> apply(n, k -> if k == i then 1/1 else 0/1);
SC = new MutableHashTable;
SC#(0,0) = hashTable{1 => 1/1};
SC#(0,1) = hashTable{2 => 1/1};
SC#(0,2) = hashTable{3 => -1/4};
SC#(0,3) = hashTable{4 => -4/1};
SC#(0,5) = hashTable{6 => 1/1};
SC#(0,6) = hashTable{7 => 1/1};
SC#(0,7) = hashTable{8 => 1/1};
SC#(0,8) = hashTable{10 => -1/2, 11 => -1/2};
SC#(0,9) = hashTable{10 => 1/1};
SC#(0,10) = hashTable{12 => 1/1};
SC#(0,11) = hashTable{13 => -1/2, 12 => -2/1};
SC#(0,12) = hashTable{14 => 2/1, 15 => 1/2};
SC#(0,13) = hashTable{15 => -2/1, 14 => -8/1};
SC#(0,14) = hashTable{16 => -1/4};
SC#(0,15) = hashTable{16 => 1/2};
SC#(1,1) = hashTable{3 => 1/1};
SC#(1,2) = hashTable{4 => 1/1};
SC#(1,6) = hashTable{9 => 1/1};
SC#(1,7) = hashTable{11 => 1/1};
SC#(1,8) = hashTable{12 => 1/1};
SC#(1,9) = hashTable{13 => 1/1};
SC#(1,10) = hashTable{14 => 4/1};
SC#(1,11) = hashTable{14 => -2/1};
SC#(1,12) = hashTable{16 => 1/2};
SC#(1,13) = hashTable{16 => -2/1};
SC#(2,5) = hashTable{8 => -2/1, 9 => -1/1};
SC#(2,8) = hashTable{14 => 1/1};
SC#(2,9) = hashTable{15 => 1/1};
SC#(2,10) = hashTable{16 => 1/1};
SC#(2,11) = hashTable{16 => -1/2};
SC#(3,5) = hashTable{11 => -8/1, 10 => -4/1};
SC#(3,6) = hashTable{13 => -2/1};
SC#(3,7) = hashTable{15 => -2/1};
SC#(3,8) = hashTable{16 => 1/1};
SC#(4,5) = hashTable{12 => 4/1, 13 => 1/1};
SC#(4,6) = hashTable{14 => 2/1};
SC#(4,7) = hashTable{16 => 1/2};
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
<< "t4 == 0 identically: " << (bad == 0) << endl;
ee = x; for t from 1 to 7 do ee = mult(ee, y);
<< "e7(x,y) = " << ee << endl;
<< "7-Engel fails (e7 != 0): " << (ee != zeroV) << endl;
if bad != 0 or ee == zeroV then error "7-Engel verification failed";
