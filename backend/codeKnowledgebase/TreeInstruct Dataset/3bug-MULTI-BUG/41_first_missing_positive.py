"""
<problem>
Given an unsorted integer array, find the smallest missing positive integer.

Example 1:
Input: [1,2,0]
Output: 3
Example 2:

Input: [3,4,-1,1]
Output: 2
Example 3:

Input: [7,8,9,11,12]
Output: 1
</problem>
<bug_fixes>
Replace `[0] * n` with `[1] + [0] * n` on line 4.
Replace `<` with `<=` on line 9.
Replace `j+1` with `n+1` on line 13.
</bug_fixes>
<bug_desc>
On line 4, the list t is not initialized correctly. The first value needs to be a 1 because it is the smallest possible positive integer. Missing this could result in incorrect behavior.
On line 9, in the while loop condition while j < n, the loop will stop before checking the last index n. It should be while j <= n.
On line 13, the function is returning j + 1 instead of n + 1 when no missing positive integer is found in the range [1, n].
</bug_desc>
"""
class Solution(object):
    def firstMissingPositive(self, nums):
        n = len(nums)
        t = [0] * n
        for i in nums:
            if i >= 1 and i <= n:
                t[i] = 1
        j = 1
        while j < n:
            if t[j] == 0:
                return j
            j +=1
        return j+1