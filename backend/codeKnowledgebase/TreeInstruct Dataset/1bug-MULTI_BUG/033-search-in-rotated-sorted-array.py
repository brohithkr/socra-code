"""
<problem>
Problem Link: https://leetcode.com/problems/search-in-rotated-sorted-array/

Suppose an array sorted in ascending order is rotated at some pivot unknown to you beforehand.
(i.e., [0,1,2,4,5,6,7] might become [4,5,6,7,0,1,2]).
You are given a target value to search. If found in the array return its index, otherwise return -1.
You may assume no duplicate exists in the array.
Your algorithm's runtime complexity must be in the order of O(log n).

Example 1:
Input: nums = [4,5,6,7,0,1,2], target = 0
Output: 4

Example 2:
Input: nums = [4,5,6,7,0,1,2], target = 3
Output: -1
</problem>
<bug_fixes>
Replace `len(nums)` with `len(nums) - 1` on line 4.
</bug_fixes>
<bug_desc>
On line 4, end is set to len(nums). In python, array indexing starts from 0, so the last valid index is len(nums) - 1. Setting end to len(nums) will result in an IndexOutOfBoundsException when nums[end] is accessed.
</bug_desc>
"""
class Solution(object):
    def search(self, nums, target):
        start = 0
        end = len(nums)
        while start <= end:
            mid = (start + end)//2
            if nums[mid] == target:
                return mid
            elif nums[start] <= nums[mid]:
                if target >= nums[start] and target < nums[mid]:
                    end = mid -1
                else:
                    start = mid + 1
            else:
                if target <= nums[end] and target > nums[mid]:
                    start = mid + 1
                else:
                    end = mid - 1
        return -1