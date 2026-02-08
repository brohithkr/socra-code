"""
<problem>
Given a string containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.
An input string is valid if:
Open brackets must be closed by the same type of brackets.
Open brackets must be closed in the correct order.
Note that an empty string is also considered valid.

Example 1:
Input: "()"
Output: true

Example 2:
Input: "()[]{}"
Output: true

Example 3:
Input: "(]"
Output: false

Example 4:
Input: "([)]"
Output: false

Example 5:
Input: "{[]}"
Output: true
</problem>
<bug_fixes>
Replace `if c in d.keys():` with `if c in d.values():` in line 10.
</bug_fixes>
<bug_desc>
On line 10, the current character c is compared with the keys in d, or the closing parantheses. This will result in incorrect behavior as the opening brackets will not be considered properly. Change the condition to check with values instead of the keys.
</bug_desc>
"""
class Solution:
    def isValid(self, s: str) -> bool:
        stack = []
        d = {
          ')': '(',
          '}': '{',
          ']': '['
        }
        for c in s:
          if c in d.keys():
            stack.append(c)
          elif (not stack) or (stack.pop() != d[c]):
              return False
        return len(stack) == 0
