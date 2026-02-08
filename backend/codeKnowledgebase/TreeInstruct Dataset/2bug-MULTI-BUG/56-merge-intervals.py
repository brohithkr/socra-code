"""
<problem>
Problem Link: https://leetcode.com/problems/merge-intervals/

Given a collection of intervals, merge all overlapping intervals.

Example 1:

Input: [[1,3],[2,6],[8,10],[15,18]]
Output: [[1,6],[8,10],[15,18]]
Explanation: Since intervals [1,3] and [2,6] overlaps, merge them into [1,6].

Example 2:
Input: [[1,4],[4,5]]
Output: [[1,5]]
Explanation: Intervals [1,4] and [4,5] are considered overlapping.
</problem>
<bug_fixes>
Replace `intervals = intervals.sort(key=lambda x: x[0])` with `intervals.sort(key=lambda x: x[0])` on line 3.
Replace `range(intervals)` with `intervals` on line 5.
</bug_fixes>
<bug_desc>
On line 3, intervals is sorted and the result is set to `intervals`. This is incorrect as the sort method works in-place and does not return anything. This is a syntactical mistake and can be fixed by simply writing `intervals.sort(key=lambda x: x[0])`.
On line 5, the range function is used incorrectly since the array intervals is passed into the function. This is a syntactical mistake and should be changed to `for interval in intervals` to iterate over the subarrays in intervals correctly.
</bug_desc>
"""
class Solution:
    def merge(self, intervals: List[List[int]]) -> List[List[int]]:
      intervals = intervals.sort(key=lambda x: x[0])
      merged = []
      for interval in range(intervals):
        if not merged or merged[-1][1] < interval[0]:
          merged.append(interval)
        else:
          merged[-1][1] = max(merged[-1][1], interval[1])
      return merged
