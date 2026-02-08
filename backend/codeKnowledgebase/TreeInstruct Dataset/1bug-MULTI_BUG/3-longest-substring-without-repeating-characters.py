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
<bug_fixes>
Replace `temp = []` with `temp = set()` on line 3.
</bug_fixes>
<bug_desc>
On line 3, temp is initialized as a list, which results in duplicate items. This is incorrect behavior, and therefore should be changed to a set.
On line 14, temp is treated as a list, which is why the `append` method is used. temp should be a set, and the correct method is `add`.
On line 15, the max_length is returned. The rest of the method does not consider the possibility of a longer subset at the end of the string. Therefore, it should return the maximum between the max_length and len(s)-index, i.e. max(max_length, len(s)-index).
</bug_desc>
"""
class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
      temp = []
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