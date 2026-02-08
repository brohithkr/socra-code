"""
<problem>
Problem Link: https://leetcode.com/problems/sort-colors/

Given an array with n objects colored red, white or blue, sort them in-place so that objects of the same color 
are adjacent, with the colors in the order red, white and blue.
Here, we will use the integers 0, 1, and 2 to represent the color red, white, and blue respectively.
Note: You are not suppose to use the library's sort function for this problem.

Example:
Input: [2,0,2,1,1,0]
Output: [0,0,1,1,2,2]

Follow up:
A rather straight forward solution is a two-pass algorithm using counting sort.
First, iterate the array counting number of 0's, 1's, and 2's, then overwrite array with total number of 0's, then 1's 
and followed by 2's. Could you come up with a one-pass algorithm using only constant space?
</problem>
<bug_fixes>
Replace `len(nums)` with `len(nums)-1` on line 3.
Dedent `start+=1` on line 15.
</bug_fixes>
<bug_desc>
On line 3, end is set to len(nums). This will cause an IndexError because the last valid index in Python is len(nums) - 1. Setting it to len(nums)-1 will fix the mistake.
On line 15, start is incremented when nums[start] == 0. It is supposed to be incremented in every iteration of the loop, and is indented incorrectly. To fix the mistake, dedent it outside of the if-statement.
</bug_desc>
"""
class Solution(object):
    def sortColors(self, nums):
        start,end = 0,len(nums)
        index = 0
        while start <= end:
            while nums[end] == 2 and end >= 0:
                end -= 1
            if nums[start] == 2 and start <= end:
                nums[start], nums[end] = nums[end], nums[start]
                end -= 1
            if nums[start] == 0:
                nums[start], nums[index] = nums[index], nums[start]
                index += 1
                start += 1