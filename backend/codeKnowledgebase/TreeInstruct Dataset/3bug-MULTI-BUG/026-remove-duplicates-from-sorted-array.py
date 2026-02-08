"""
<problem>
Problem Link: https://leetcode.com/problems/remove-duplicates-from-sorted-array/description/

Given a sorted array nums, remove the duplicates in-place such that each element appear only once and return the new length.
Do not allocate extra space for another array, you must do this by modifying the input array in-place with O(1) extra memory.

Example 1:
Given nums = [1,1,2],

Your function should return length = 2, with the first two elements of nums being 1 and 2 respectively.
It doesn't matter what you leave beyond the returned length.

Example 2:

Given nums = [0,0,1,1,1,2,2,3,3,4],
Your function should return length = 5, with the first five elements of nums being modified to 0, 1, 2, 3, and 4 respectively.
It doesn't matter what values are set beyond the returned length.

Clarification:
Confused why the returned value is an integer but your answer is an array?
Note that the input array is passed in by reference, which means modification to the input array will be known to the caller as well.
Internally you can think of this:

// nums is passed in by reference. (i.e., without making a copy)
int len = removeDuplicates(nums);

// any modification to nums in your function would be known by the caller.
// using the length returned by your function, it prints the first len elements.
for (int i = 0; i < len; i++) {
    print(nums[i]);
}
</problem>
<bug_fixes>
Replace `index = 1` with `index = 0` on line 3.
Add a colon at the end of line 5.
Replace `index` with `index + 1` on line 8.
</bug_fixes>
<bug_desc>
On line 3, index starts with 1, isntead of 0. This means that the first element of the array will be skipped, and the duplicates will not be removed correctly.
On line 5, a colon is missing from the if-condition, causing it to not terminate. This is a syntactical bug that can be fixed by adding a colon at the end.
On line 8, the function only returns index instead of index+1. This will be incorrect because the length of the array after removing duplicates should include the last unique element.
</bug_desc>
"""
class Solution:
    def removeDuplicates(self, nums: List[int]) -> int:
        index = 1
        for i in range(1,len(nums)):
          if nums[index] != nums[i]
            nums[index+1] = nums[i]
            index += 1
        return index
