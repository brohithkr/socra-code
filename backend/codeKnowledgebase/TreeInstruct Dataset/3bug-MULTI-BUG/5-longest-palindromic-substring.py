"""
<problem>
Problem Link: https://leetcode.com/problems/longest-palindromic-substring/

Given a string s, find the longest palindromic substring in s. 
You may assume that the maximum length of s is 1000.

Example 1:
Input: "babad"
Output: "bab"
Note: "aba" is also a valid answer.

Example 2:
Input: "cbbd"
Output: "bb"
</problem>
<bug_fixes>
Replace `for j in range(len(s), i-1, -1):` with `for j in range(len(s)-1, i-1, -1):` on line 7.
Replace `>` with `<` on line 9.
Add a closing bracket `]` to the end of line 13.
</bug_fixes>
<bug_desc>
On line 6, the starting value j for the for-loop is out of bounds for the array s. It should start from len(s)-1, instead.
On line 9, the code will only update start_index and max_len if the current palindrome found is shorter than the previously recorded longest palindrome. This is the opposite of the intended logic. The > operator should be <.
On line 13, the array accessing is not completed as it is not terminated with a closing bracket. Adding a ] to the end of the line will fix the mistake.
</bug_desc>
"""
class Solution:
    def longestPalindrome(self, s: str) -> str:
        if len(s) < 2:
            return s
        start_index = max_len = 0
        for i in range(len(s)):
            for j in range(len(s), i-1, -1):
                if s[i:j+1] == (s[j:i-1:-1] if i > 0 else s[j::-1]):
                    if max_len > j - i + 1:
                        start_index = i
                        max_len = j - i + 1
                    break
        return s[start_index: start_index + max_len
            