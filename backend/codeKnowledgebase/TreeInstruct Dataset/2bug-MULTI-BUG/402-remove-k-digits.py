"""
<problem>
Problem Link: https://leetcode.com/problems/remove-k-digits/

Given a non-negative integer num represented as a string, remove k digits from the number 
so that the new number is the smallest possible.

Note:
The length of num is less than 10002 and will be ≥ k.
The given num does not contain any leading zero.

Example 1:
Input: num = "1432219", k = 3
Output: "1219"
Explanation: Remove the three digits 4, 3, and 2 to form the new number 1219 which is the smallest.

Example 2:
Input: num = "10200", k = 1
Output: "200"
Explanation: Remove the leading 1 and the number is 200. Note that the output must not 
contain leading zeroes.

Example 3:
Input: num = "10", k = 2
Output: "0"
Explanation: Remove all the digits from the number and it is left with nothing which is 0.
</problem>
<bug_fixes>
Replace `{}` with `[]` on line 5.
Add `k -= 1` on line 13.
</bug_fixes>
<bug_desc>
On line 5, stack is initialized as a dictionary, when it is used as a list later on. To fix this, set stack to a list ([]).
ON line 13, or after line 12, k is never updated. This causes an infinite loop, and can be fixed by decrementing k by 1 in each iteration of the loop.
</bug_desc>
"""
class Solution:
    def removeKdigits(self, num: str, k: int) -> str:
        if k == num:
          return "0"
        stack = {}
        for i in range(len(num)):
          while k and stack and stack[-1] > num[i]:
            stack.pop()
            k -= 1
          stack.append(num[i])
        while k:
          stack.pop()

        index = 0
        while index < len(stack) and stack[index] == "0":
          index += 1
        return "0" if index == len(stack) else "".join(stack[index:])