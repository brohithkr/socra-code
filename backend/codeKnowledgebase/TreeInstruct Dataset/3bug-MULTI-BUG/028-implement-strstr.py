"""
<problem>
Problem Link: https://leetcode.com/problems/implement-strstr/description/

Implement strStr().
Return the index of the first occurrence of needle in haystack, or -1 if needle is not part of haystack.

Example 1:
Input: haystack = "hello", needle = "ll"
Output: 2

Example 2:
Input: haystack = "aaaaa", needle = "bba"
Output: -1

Clarification:
What should we return when needle is an empty string? This is a great question to ask during an interview.
For the purpose of this problem, we will return 0 when needle is an empty string. This is consistent to C's strstr() and Java's indexOf().
</problem>
<bug_fixes>
Add a colon at the end of line 5.
Replace `haystack[i:i+1]` with `haystack[i:i+l]` on line 6.
Add `return -1` on line 9.
</bug_fixes>
<bug_desc>
On line 5, a colon is missing from the for-loop, causing it to not terminate. This is a syntactical bug that can be fixed by adding a colon at the end.
On line 6, haystack[i:i+1] is compared to needle. haystack[i:i+1] will return the ith character only. This will result in incorrect behavior if needle is more than one character long. Taking the subset from i to i+l will fix the mistake, i.e., haystack[i:i+l].
On line 9, or after line 8, nothing is returned from the method if a matching needle is not found. This is incorrect behavior as -1 should be returned. Adding `return -1` will fix the mistake.
</bug_desc>
"""
class Solution(object):
    def strStr(self, haystack, needle):
        if needle == ""or needle == haystack: return 0
        l = len(needle)
        for i in range(0,(len(haystack)-l+1))
            if haystack[i:i+1] == needle:
                return i
            print(haystack[i:i+l])
            