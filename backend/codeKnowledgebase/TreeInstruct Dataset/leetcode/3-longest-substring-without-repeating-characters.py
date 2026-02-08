"""
<problem>
Problem Link: https://leetcode.com/problems/longest-substring-without-repeating-characters/

Given a string, find the length of the longest substring without repeating characters.

Example 1:
Input: "abcabcbb"
Output: 3 
Explanation: The answer is "abc", with the length of 3. 

Example 2:
Input: "bbbbb"
Output: 1
Explanation: The answer is "b", with the length of 1.

Example 3:
Input: "pwwkew"
Output: 3
Explanation: The answer is "wke", with the length of 3. 
             Note that the answer must be a substring, "pwke" is a subsequence and not a substring.
</problem>
"""
class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
      temp = set()
      max_length = 0
      index = 0
      for i in range(len(s)):
        if s[i] in temp:
          max_length = max(max_length, i-index)
          while s[index] != s[i]:
            temp.remove(s[index])
            index += 1
          index += 1
        else:
          temp.add(s[i])
      return max(max_length, len(s)-index)