"""
<problem>
Problem Link: https://leetcode.com/problems/largest-rectangle-in-histogram/

Given an array of integers heights representing the histogram's bar height where the width of each 
bar is 1, return the area of the largest rectangle in the histogram.

Example 1:
Input: heights = [2,1,5,6,2,3]
Output: 10
Explanation: The above is a histogram where width of each bar is 1.
The largest rectangle is shown in the red area, which has an area = 10 units.

Example 2:
Input: heights = [2,4]
Output: 4
 
Constraints:
1 <= heights.length <= 105
0 <= heights[i] <= 104
</problem>
<bug_fixes>
Add a colon to the end of line 2.
Replace `else 0` with `else -1` on line 10.
Replace `range(len(heights)-1, -1)` with `range(len(heights)-1, -1, -1)` on line 16.
</bug_fixes>
<bug_desc>
On line 2, a colon is missing from the method signature, causing it to not terminate. This is a syntactical bug that can be fixed by adding a colon at the end.
On line 10, the value of 0 is appended to the lb list when the stack is empty. However, this value 0 is incorrect because it represents an valid index. Instead, it should be -1 because stack is None or missing.
On line 16, the step in the range is set to the default of 1. This will result in an infinite loop as the counter should decrease to -1. This can be fixed by setting the step to -1 like so: `range(len(heights)-1,-1,-1)`.
</bug_desc>
"""
class Solution:
    def largestRectangleArea(self, heights: List[int]) -> int
        lb = []
        stack = []
        
        for index in range(len(heights)):
            while stack and heights[stack[-1]] >= heights[index]:
                stack.pop()
            
            lb.append(stack[-1] if stack else 0)
            stack.append(index)
        
        rb = [0] * len(heights)
        stack = []
        
        for index in range(len(heights)-1, -1):
            while stack and heights[stack[-1]] >= heights[index]:
                stack.pop()
            
            rb[index] = stack[-1] if stack else len(heights)
            stack.append(index)
        
        max_area = 0
        for index in range(len(heights)):
            width = rb[index] - lb[index] - 1
            max_area = max(max_area, width * heights[index])
        
        return max_area
