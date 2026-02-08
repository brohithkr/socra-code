"""
<problem>
Problem Link: https://leetcode.com/problems/3sum/

Given an array nums of n integers, are there elements a, b, c in nums such that a + b + c = 0?
Find all unique triplets in the array which gives the sum of zero.

Note:
The solution set must not contain duplicate triplets.

Example:
Given array nums = [-1, 0, 1, 2, -1, -4],

A solution set is:
[
  [-1, 0, 1],
  [-1, -1, 2]
]
</problem>
<bug_fixes>
Replace `nums = nums.sort()` with `nums.sort()` on line 4.
Replace `start += 1` with `while curStart == nums[start] and start < end: start += ` on line 14.
</bug_fixes>
<bug_desc>
On line 4, the result of nums.sort() is being set as nums. nums.sort() does not return anything, and it sorts the array in-place, which results in nums being set to None. This is incorrect behavior, and can be fixed by simply using nums.sort().
On line 14, the start pointer is simply incremented by 1. This does not correctly handle duplicates. The correct way is to skip over the duplicates using a while loop.
</bug_desc>
"""
class Solution:
    def threeSum(self, nums: List[int]) -> List[List[int]]:
        res = []
        nums = nums.sort()
        for i in range(len(nums)-2):
          if i == 0 or nums[i] > nums[i-1]:
            start = i+1
            end = len(nums)-1
            while start < end:
              Sum = nums[i] + nums[start] + nums[end]
              if Sum == 0:
                res.append([nums[i],nums[start],nums[end]])
              elif Sum < 0:
                start += 1
              else:
                curEnd = nums[end]
                while curEnd == nums[end] and start < end:
                  end -= 1
        return res