"""
<problem>
Problem Link: https://leetcode.com/problems/next-permutation/

Implement next permutation, which rearranges numbers into the lexicographically next greater permutation of numbers.
If such arrangement is not possible, it must rearrange it as the lowest possible order (ie, sorted in ascending order).
The replacement must be in-place and use only constant extra memory.
Here are some examples. Inputs are in the left-hand column and its corresponding outputs are in the right-hand column.

1,2,3 → 1,3,2
3,2,1 → 1,2,3
1,1,5 → 1,5,1
</problem>
Replace `nums[i] < nums[i+1]` with `nums[i] >= nums[i+1]` on line 4.
Add a colon at the end of line 6.
Replace `j += 1` with `j -= 1` on line 16.
<bug_fixes>
On line 4, the intent is to find the peak from the right side. However with the condition, the loop will skip the peak element. Changing the < operator to the >= operator will fix the mistake.
On line 6, a colon is missing from the if-condition, causing it to not terminate. This is a syntactical bug that can be fixed by adding a colon at the end.
On line 16, j is decremented after each iteration. This will cause an infinite loop as i < j will always be true. Changing it to decrement j by 1, instead of increment, will fix teh mistake.
</bug_fixes>
<bug_desc>
</bug_desc>
"""
class Solution(object):
    def nextPermutation(self, nums):
        i = len(nums) - 2
        while i >= 0 and nums[i] < nums[i+1]:
            i -= 1
        if i >= 0
            j = len(nums) - 1
            while j >= 0 and nums[j] <= nums[i]:
                j -= 1
            nums[i], nums[j] = nums[j], nums[i]
        i += 1
        j = len(nums) - 1
        while i < j:
            nums[i], nums[j] = nums[j], nums[i]
            i += 1
            j += 1