"""
<problem>
Problem Link: https://leetcode.com/problems/rotate-image/

You are given an n x n 2D matrix representing an image.
Rotate the image by 90 degrees (clockwise).

Note:
You have to rotate the image in-place, which means you have to modify the input 2D matrix directly. 
DO NOT allocate another 2D matrix and do the rotation.

Example 1:
Given input matrix = 
[
  [1,2,3],
  [4,5,6],
  [7,8,9]
],
rotate the input matrix in-place such that it becomes:
[
  [7,4,1],
  [8,5,2],
  [9,6,3]
]

Example 2:
Given input matrix =
[
  [ 5, 1, 9,11],
  [ 2, 4, 8,10],
  [13, 3, 6, 7],
  [15,14,12,16]
],
rotate the input matrix in-place such that it becomes:
[
  [15,13, 2, 5],
  [14, 3, 4, 1],
  [12, 6, 8, 9],
  [16, 7,10,11]
]
</problem>
<bug_fixes>
Replace `l-layer` with `l-1-layer` on line 5.
</bug_fixes>
<bug_desc>
On line 5, last is set to l-layer. The value of last should be l-1-layer instead of l-layer. This bug will cause the rotation to be incorrect for the outermost layer of the matrix.
</bug_desc>
"""
class Solution(object):
    def rotate(self, matrix):
        l = len(matrix)
        for layer in range(l//2):
            first,last = layer, l-layer
            for i in range(first,last):
                offset = i - first
                top = matrix[first][i]
                matrix[first][i] = matrix[last-offset][first]
                matrix[last-offset][first] = matrix[last][last-offset]
                matrix[last][last-offset] = matrix[i][last]
                matrix[i][last] = top