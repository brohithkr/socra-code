"""
<problem>
Given a sorted array and a target value, return the index if the target is found. 
If not, return the index where it would be if it were inserted in order.
You may assume no duplicates in the array.

Sample Test Cases:
Input: [1,3,5,6], 5
Output: 2
Input: [1,3,5,6], 2
Output: 1
Input: [1,3,5,6], 7
Output: 4
Input: [1,3,5,6], 0
Output: 0
</problem>
<bug_fixes>
Replace / with // on line 5.
Replace `star` with `start` on line 12.
</bug_fixes>
<bug_desc>
On line 5, a float division occurs between (start+end) and 2. This might result in mid being a float value if (start+end) is not divisible by 2. This can be fixed by performing n integer division, i.e., mid = (start+end)//2.
On line 12, an unknown variable called star is returned. This causes a runtime error. It seems to be a spelling mistake where `start` should be returned instead of `star`.
</bug_desc>
"""
class Solution:
    def searchInsert(self, nums: List[int], target: int) -> int:
        start, end = 0, len(nums)-1
        while start <= end:
          mid = (start+end)/2
          if nums[mid] == target:
            return mid
          elif nums[mid] < target:
            start = mid + 1
          else:
            end = mid - 1
        return star
