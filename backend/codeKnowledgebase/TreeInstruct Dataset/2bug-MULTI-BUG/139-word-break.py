"""
<problem>
Problem Link: https://leetcode.com/problems/word-break/

Given a string s and a dictionary of strings wordDict, return true if s can be segmented into a 
space-separated sequence of one or more dictionary words.
Note that the same word in the dictionary may be reused multiple times in the segmentation.

Example 1:
Input: s = "leetcode", wordDict = ["leet","code"]
Output: true
Explanation: Return true because "leetcode" can be segmented as "leet code".

Example 2:
Input: s = "applepenapple", wordDict = ["apple","pen"]
Output: true
Explanation: Return true because "applepenapple" can be segmented as "apple pen apple".
Note that you are allowed to reuse a dictionary word.

Example 3:
Input: s = "catsandog", wordDict = ["cats","dog","sand","and","cat"]
Output: false
 
Constraints:
1 <= s.length <= 300
1 <= wordDict.length <= 1000
1 <= wordDict[i].length <= 20
s and wordDict[i] consist of only lowercase English letters.
All the strings of wordDict are unique.
</problem>
<bug_fixes>
Replace `len(s)` with `i` on line 9.
Replace `len(s)` with `-1` on line 13.
</bug_fixes>
<bug_desc>
On line 9, the inner loop `for j in range(len(s))` iterates over the entire string s for each value of i, even though it only needs to check substrings up to i. Change the condition to `for j in range(i)`.
On line 13, instead of w[len(s)], it should be w[-1] to access the last element of the list w. In Python, negative indexing allows you to access elements from the end of the list.
</bug_desc>
"""
class Solution:
    def wordBreak(self, s: str, wordDict: List[str]) -> bool:
        wordDict = set(wordDict)
        
        w = [False] * (len(s) + 1)
        w[0] = True
        
        for i in range(1, len(s)+1):
            for j in range(len(s)):
                if w[j] and s[j:i] in wordDict:
                    w[i] = True
                    break
        return w[len(s)]