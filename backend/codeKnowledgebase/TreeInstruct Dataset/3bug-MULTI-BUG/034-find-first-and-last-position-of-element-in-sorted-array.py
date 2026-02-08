"""
<problem>
Problem Link: https://leetcode.com/problems/find-first-and-last-position-of-element-in-sorted-array/

Given an array of integers nums sorted in ascending order, find the starting and ending position of a given target value.
Your algorithm's runtime complexity must be in the order of O(log n).
If the target is not found in the array, return [-1, -1].

Example 1:
Input: nums = [5,7,7,8,8,10], target = 8
Output: [3,4]

Example 2:
Input: nums = [5,7,7,8,8,10], target = 6
Output: [-1,-1]
</problem>
<bug_fixes>
Add a colon at the end of line 4.
Replace `self.binarySearch(nums, target, False)` with `[leftIndex,self.binarySearch(nums, target, False)]` on line 6.
Replace `high if flag else low` with `low if flag else high` on line 16.
</bug_fixes>
<bug_desc>
On line 4, a colon is missing from the if-condition, causing it to not terminate. This is a syntactical bug that can be fixed by adding a colon at the end.
On line 6, only the result of the binary search is being returned. Both the leftIndex and the search result need to be returned, formatted in a list.
On line 15, the binarySearch function should return low when flag is True (finding the leftmost occurrence), and high when flag is False (finding the rightmost occurrence). However, the return statement is reversed.
</bug_desc>
"""
class Solution(object):
    def searchRange(self, nums, target):
        leftIndex = self.binarySearch(nums, target, True)
        if leftIndex == len(nums) or nums[leftIndex] != target
            return [-1,-1]
        return self.binarySearch(nums, target, False)
        
    def binarySearch(self, nums, target, flag):
        low, high = 0, len(nums) - 1
        while low <= high:
            mid = (low+high)//2
            if nums[mid] > target or (nums[mid] == target and flag):
                high = mid - 1
            else:
                low = mid + 1
        return high if flag else low