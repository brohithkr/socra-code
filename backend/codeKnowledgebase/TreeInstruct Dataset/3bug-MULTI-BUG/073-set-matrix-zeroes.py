"""
<problem>
Problem Link: https://leetcode.com/problems/set-matrix-zeroes/

Given a m x n matrix, if an element is 0, set its entire row and column to 0. Do it in-place.

Example 1:
Input: 
[
  [1,1,1],
  [1,0,1],
  [1,1,1]
]
Output: 
[
  [1,0,1],
  [0,0,0],
  [1,0,1]
]

Example 2:
Input: 
[
  [0,1,2,0],
  [3,4,5,2],
  [1,3,1,5]
]
Output: 
[
  [0,0,0,0],
  [0,4,5,0],
  [0,3,1,0]
]
</problem>
<bug_fixes>
Replace `range(0,col)` with `range(1,col)` on line 9.
Replace `and` with `or` on line 16.
Replace `matrix[0][i]` with `matrix[0][j]` on line 20.
</bug_fixes>
<bug_desc>
On line 9, using range(0,col) introduces a bug where the code unnecessarily modifies the first column of the matrix. To avoid this mistake, use range(1,col) in the for-loop.
On line 16, the logical condition is incorrect. It should be `if not matrix[i][0] or not matrix[0][j]`, as we want to set matrix[i][j] to 0 if either matrix[i][0] or matrix[0][j] is 0.
On line 20, the loop variable i is used instead of j in the line matrix[0][i] = 0. It should be matrix[0][j] = 0.
</bug_desc>
"""
class Solution(object):
    def setZeroes(self, matrix):
        row = len(matrix)
        col = len(matrix[0])
        is_col= False
        for i in range(row):
            if matrix[i][0] == 0:
                is_col= True
            for j in range(0,col):
                if matrix[i][j] == 0:
                    matrix[0][j] = 0
                    matrix[i][0] = 0
                    
        for i in range(1,row):
            for j in range(1,col):
                if not matrix[i][0] and not matrix[0][j]:
                    matrix[i][j] = 0
        if matrix[0][0] == 0:
            for j in range(col):
                matrix[0][i] = 0
        if is_col:
            for i in range(row):
                matrix[i][0] = 0