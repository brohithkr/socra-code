"""
<problem>
Problem Link: https://leetcode.com/problems/longest-common-prefix/

Write a function to find the longest common prefix string amongst an array of strings.
If there is no common prefix, return an empty string "".

Example 1:
Input: ["flower","flow","flight"]
Output: "fl"

Example 2:
Input: ["dog","racecar","car"]
Output: ""
Explanation: There is no common prefix among the input strings.

Note:
All given inputs are in lowercase letters a-z.
</problem>
<bug_fixes>
Replace `res = strs` with `res = strs[0]` on line 5.
Replace `res[length:]` with `res[:length]` on line 16.
</bug_fixes>
<bug_desc>
On line 5, res is set to the strs array, but is referenced as a singular string later on. This seems to be a syntactical mistake, where res is the first element of the strs array, i.e., strs[0].
On line 16, the suffix of res is returned instead of the prefix. This is incorrect behavior and therefore, res[:length] should be returned.
</bug_desc>
"""
class Solution:
    def longestCommonPrefix(self, strs: List[str]) -> str:
      if not strs:
        return ""
      res = strs
      length = len(res)
      for i in range(1,len(strs)):
        index = 0
        while index < length and index < len(strs[i]):
          if res[index] != strs[i][index]:
            break
          index += 1
        if not index:
          return ""
        length = index
      return res[length:]