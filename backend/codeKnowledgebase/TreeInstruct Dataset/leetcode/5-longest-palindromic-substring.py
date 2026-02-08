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
"""
class Solution:
    def longestPalindrome(self, s: str) -> str:
        if len(s) < 2:
            return s
        start_index = max_len = 0
        for i in range(len(s)):
            for j in range(len(s)-1, i-1, -1):
                if s[i:j+1] == (s[j:i-1:-1] if i > 0 else s[j::-1]):
                    if max_len < j - i + 1:
                        start_index = i
                        max_len = j - i + 1
                    break
        return s[start_index: start_index + max_len]
            