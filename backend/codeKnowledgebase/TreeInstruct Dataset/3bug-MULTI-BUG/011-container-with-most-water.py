"""
<problem>
Problem Link: https://leetcode.com/problems/container-with-most-water/

Given n non-negative integers a1, a2, ..., an , where each represents a point at coordinate (i, ai). n vertical lines are drawn such that 
the two endpoints of line i is at (i, ai) and (i, 0). Find two lines, which together with x-axis forms a container, such that the container 
contains the most water.
Note: You may not slant the container and n is at least 2.

Example:

Input: [1,8,6,2,5,4,8,3,7]
Output: 49
</problem>
<bug_fixes>
Replace >= with < on line 6.
Replace `r += 1` with `r -= 1` on line 9.
Add a return statement on line 10.
</bug_fixes>
<bug_desc>
On line 6, l is updated if the height of the left side is greater than the right. This is incorrect behavior because it reverses the direction of the search. The >= operator should be replaced with the < operator.
On line 9, r is incremented by 1. This results in an incorrect upper bound on the height. Therefore, it should be decremented instead.
On line 10, or after line 9, nothing is returned from the method. maxarea should be returned to ensure correct behavior.
</bug_desc>
"""
class Solution(object):
    def maxArea(self, height):
        maxarea,l,r = 0,0,len(height)-1
        while l < r:
            maxarea = max(maxarea, min(height[l],height[r])*(r-l))
            if height[l] >= height[r]:
                l += 1
            else:
                r += 1