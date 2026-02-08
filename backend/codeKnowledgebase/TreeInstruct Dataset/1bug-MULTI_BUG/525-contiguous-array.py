"""
<problem>
Problem Link: https://leetcode.com/problems/contiguous-array/

Given a binary array, find the maximum length of a contiguous subarray with equal number of 0 and 1.

Example 1:
Input: [0,1]
Output: 2
Explanation: [0, 1] is the longest contiguous subarray with equal number of 0 and 1.

Example 2:
Input: [0,1,0]
Output: 2
Explanation: [0, 1] (or [1, 0]) is a longest contiguous subarray with equal number of 0 and 1.
Note: The length of the given binary array will not exceed 50,000.
</problem>
<bug_fixes>
Replace `[]` with `{}` on line 3.
</bug_fixes>
<bug_desc>
On line 3, d is initialized to a list. This is incorrect behavior because it is treated as a dictionary later on. To fix this mistake, use `d = []`.
</bug_desc>
"""
class Solution:
    def findMaxLength(self, nums: List[int]) -> int:
        d = []
        d[0] = -1
        maxLen = count = 0
        for i in range(len(nums)):
          count += 1 if nums[i] == 1 else -1
          if count in d:
            maxLen = max(maxLen, i-d[count])
          else:
            d[count] = i
        return maxLen