"""
<problem>
Problem Link: https://leetcode.com/problems/jump-game/

Given an array of non-negative integers, you are initially positioned at the first index of the array.
Each element in the array represents your maximum jump length at that position.
Determine if you are able to reach the last index.

Example 1:
Input: [2,3,1,1,4]
Output: true
Explanation: Jump 1 step from index 0 to 1, then 3 steps to the last index.

Example 2:
Input: [3,2,1,0,4]
Output: false
Explanation: You will always arrive at index 3 no matter what. Its maximum
             jump length is 0, which makes it impossible to reach the last index.
</problem>
<bug_fixes>
Add a colon at the end of line 2.
Replace `range(len(nums)-1, -1)` with `range(len(nums)-1, -1, -1)` on line 4.
</bug_fixes>
<bug_desc>
On line 2, a colon is missing from the method signature, causing it to not terminate. This is a syntactical bug that can be fixed by adding a colon at the end.
On line 4, the range function will increment i by 1 starting from len(nums) - 1. This will cause an infinite loop at -1 will never be reached. This is because the step parameter of the function range is set to the default, which is 1. It should be set to -1.
</bug_desc>
"""
class Solution1:
    def canJump(self, nums: List[int]) -> bool
      lastPos = len(nums) - 1
      for i in range(len(nums)-1, -1):
        if i + nums[i] >= lastPos:
          lastPos = i
      return lastPos == 0
