"""
<problem>
Problem Link: https://leetcode.com/problems/reverse-string/

Write a function that reverses a string. The input string is given as an array of characters char[].
Do not allocate extra space for another array, you must do this by modifying the input array 
in-place with O(1) extra memory.
You may assume all the characters consist of printable ascii characters.

Example 1:
Input: ["h","e","l","l","o"]
Output: ["o","l","l","e","h"]

Example 2:
Input: ["H","a","n","n","a","h"]
Output: ["h","a","n","n","a","H"]
</problem>
<bug_fixes>
Replace `len(s)` with `len(s) - 1` on line 3.
Replace `+` with `-` on line 7.
</bug_fixes>
<bug_desc>
On line 3, end is set to len(s) which could result in an IndexError because it is out of bounds. To fix this, set end to len(s)-1.
On line 7, end is incremented by 1. This causes an infinite loop since start and end are both incremented. To fix this, decrement end by 1.
</bug_desc>
"""
class Solution:
    def reverseString(self, s: List[str]) -> None:
        start, end = 0, len(s)
        while start < end:
          s[start], s[end] = s[end], s[start]
          start += 1
          end += 1
