"""
<problem>
Problem Link: https://leetcode.com/problems/jump-game-ii/

Given an array of non-negative integers nums, you are initially positioned 
at the first index of the array.
Each element in the array represents your maximum jump length at that position.
Your goal is to reach the last index in the minimum number of jumps.
You can assume that you can always reach the last index.

Example 1:

Input: nums = [2,3,1,1,4]
Output: 2
Explanation: The minimum number of jumps to reach the last index is 2. 
Jump 1 step from index 0 to 1, then 3 steps to the last index.

Example 2:
Input: nums = [2,3,0,1,4]
Output: 2

Constraints:
1 <= nums.length <= 104
0 <= nums[i] <= 1000
</problem>
<bug_fixes>
Add a colon at the end of line 2.
Replace `range(len(nums))` with`range(len(nums)-1)` on line 5.
Replace `return jumps + 1` with `return jumps` on line 12.
</bug_fixes>
<bug_desc>
On line 2, a colon is missing from the method signature, causing it to not terminate. This is a syntactical bug that can be fixed by adding a colon at the end.
On line 5, the for-loop ends with index at len(nums)-1. This results in a jump that is out of bounds. This is incorrect behavior and can be fixed by constraining the range to len(nums)-1.
On line 12, the code adds an extra unnecessary jump at the end. The correct code should return the value of jumps directly, as the last jump is already counted within the loop.
</bug_desc>
"""`
class Solution:
    def jump(self, nums: List[int]) -> int
        jumps, end, farthest = 0, 0, 0
        
        for index in range(len(nums)):
            farthest = max(farthest, index + nums[index])
            
            if end == index:
                jumps += 1
                end = farthest
        
        return jumps + 1