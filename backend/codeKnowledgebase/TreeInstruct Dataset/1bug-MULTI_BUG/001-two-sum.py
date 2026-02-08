"""
<problem>
Problem Link: https://leetcode.com/problems/two-sum/
Given an array of integers, 
return indices of the two numbers such that they add up to a specific target.

You may assume that each input would have exactly one solution, and 
you may not use the same element twice.

Example:
Given nums = [2, 7, 11, 15], target = 9,
Because nums[0] + nums[1] = 2 + 7 = 9,
return [0, 1].
</problem>
<bug_fixes>
Replace `nums[i] - target` with `target - nums[i]` on line 5.
</bug_fixes>
<bug_desc>
On line 5, difference is calculated as nums[i] - target. This results in a negative number, which will not be found. Therefore, the difference needs to be calculated as target - nums[i].
</bug_desc>
"""
class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
      d = {}
      for i in range(len(nums)):
        difference = nums[i] - target
        if difference in d:
          return [d[difference], i]
        d[nums[i]] = i
      return d
