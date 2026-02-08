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
Replace `d = []` with `d = {}` on line 3.
Add a colon at the end of line 6.
</bug_fixes>
<bug_desc>
On line 5, difference is calculated as nums[i] - target. This results in a negative number, which will not be found. Therefore, the difference needs to be calculated as target - nums[i].
On line 3, d is initialized as a list, but is used as a dictionary later on. This results in a runtime error. d needs to be initialized as a dictionary, by using '{}' to indicate a dictionary instead of a list.
On line 6, a colon is missing from the if-condition, causing it to not terminate. This is a syntactical bug that can be fixed by adding a colon at the end.
</bug_desc>
"""
class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
      d = []
      for i in range(len(nums)):
        difference = nums[i] - target
        if difference in d
          return [d[difference], i]
        d[nums[i]] = i
      return d
