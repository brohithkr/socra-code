"""
<problem>
Problem Link: https://leetcode.com/problems/subsets/

Given an integer array nums of unique elements, return all possible subsets (the power set).
The solution set must not contain duplicate subsets. Return the solution in any order.

Example 1:
Input: nums = [1,2,3]
Output: [[],[1],[2],[1,2],[3],[1,3],[2,3],[1,2,3]]

Example 2:
Input: nums = [0]
Output: [[],[0]]
 
Constraints:
1 <= nums.length <= 10
-10 <= nums[i] <= 10
All the numbers of nums are unique.
</problem>
<bug_fixes>
Add a colon at the end of line 2.
Replace `len(nums)-1` with `len(nums)` on line 10.
Add `create_subset(nums, 0)` on line 13.
</bug_fixes>
<bug_desc>
On line 2, a colon is missing from the method signature, causing it to not terminate. This is a syntactical bug that can be fixed by adding a colon at the end.
On line 10, the upper bound in the range function is len(nums)-1. This is a mistake as not all values will be considered. This seems to be a syntactical mistake where the student does not know the range function is exclusive on the upper bound. It can be fixed by changing it to `range(index, len(nums)-1).
On line 13, the function create_subset is never called, and an empty list is returned. This is a mistake, and can be fixed by calling `create_subset(nums, 0)` on line 13.
</bug_desc>
"""
class Solution:
    def subsets(self, nums: List[int]) -> List[List[int]]
        self.res = []
        
        def create_subset(nums, index, subset=[]):
            self.res.append(subset)
            if index >= len(nums):
                return
            
            for i in range(index, len(nums)-1):
                create_subset(nums, i+1, subset + [nums[i]])


        return self.res
