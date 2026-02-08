"""
<problem>
Problem Link: https://leetcode.com/problems/intersection-of-two-arrays-ii/

Given two arrays, write a function to compute their intersection.

Example 1:
Input: nums1 = [1,2,2,1], nums2 = [2,2]
Output: [2,2]

Example 2:
Input: nums1 = [4,9,5], nums2 = [9,4,9,8,4]
Output: [4,9]

Note:
Each element in the result should appear as many times as it shows in both arrays.
The result can be in any order.
</problem>
"""
class Solution:
    def intersect(self, nums1: List[int], nums2: List[int]) -> List[int]:
        if len(nums2) > len(nums1):
          self.intersect(nums2, nums1)
        
        d = {}
        res = []
        for no in nums1:
          d[no] = d.get(no, 0) + 1
        
        for no in nums2:
          if no in d and d[no]:
            res.append(no)
            d[no] -= 1
        return res