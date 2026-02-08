"""
<problem>
Problem Link: https://leetcode.com/problems/maximum-subarray/description/

Given an integer array nums, find the contiguous subarray 
(containing at least one number) which has the largest sum and return its sum.

Example:
Input: [-2,1,-3,4,-1,2,1,-5,4],
Output: 6
Explanation: [4,-1,2,1] has the largest sum = 6.
</problem>
<bug_fixes>
Replace `inf` with `-inf` on line 3.
Add colon at the end of line 5.
Replace `cur_sum` with `max_sum` on line 9.
</bug_fixes>
<bug_desc>
On line 3, max_sum and cur_sum are initialized with float('inf') instead of float('-inf'). This is incorrect for finding the maximum subarray sum because no value will be larger than infinity, which will hinder the maximum subarray search.
On line 5, a colon is missing from the if-condition, causing it to remain unterminated. This is a syntactical mistake that can be fixed by adding a colon at the end of the if-condition.
On line 9, cur_sum is returned instead max_sum. The max_sum variable stores the maximum subarray sum, so it should be returned instead of cur_sum.
</bug_desc>
"""
class Solution:
    def maxSubArray(self, nums: List[int]) -> int:
        max_sum = cur_sum = float('inf')
        
        for num in nums
            cur_sum = max(cur_sum + num, num)
            max_sum = max(max_sum, cur_sum)
        
        return cur_sum
