"""
<problem>
Problem Link: https://leetcode.com/problems/add-binary/

Given two binary strings, return their sum (also a binary string).
The input strings are both non-empty and contains only characters 1 or 0.

Example 1:
Input: a = "11", b = "1"
Output: "100"

Example 2:
Input: a = "1010", b = "1011"
Output: "10101"
</problem>
<bug_fixes>
Replace `1` with `'1'` on line 18.
Replace `res[::-1].join('')` with `''.join(res[::-1])` on line 21.
</bug_fixes>
<bug_desc>
On line 18, carry is a string variable, but is being compared to an int - the condition will always be false. To fix the bug, compare carry with '1' (as a string).
On line 21, the syntax for the join() method is wrong, as join() is a string method. The arguments needs to be reversed to fix the bug, like so: ''.join(res[::-1]).
</bug_desc>
"""
class Solution:
    def addBinary(self, a: str, b: str) -> str:
      res = []
      i = len(a) - 1
      j = len(b) - 1
      carry = '0'
      while i >= 0 or j >=0:
        ach = a[i] if i >= 0 else '0'
        bch = b[j] if j >= 0 else '0'
        if ach == bch:
          res.append(carry)
          carry = ach
        else:
          res.append('1' if carry == '0' else '0')
        i -= 1
        j -= 1
      
      if carry == 1:
        res.append(carry)
      
      return res[::-1].join('')