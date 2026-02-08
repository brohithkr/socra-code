"""
<problem>
Problem Link: https://leetcode.com/problems/spiral-matrix/

Given a matrix of m x n elements (m rows, n columns), return all elements of the matrix in spiral order.

Example 1:
Input:
[
 [ 1, 2, 3 ],
 [ 4, 5, 6 ],
 [ 7, 8, 9 ]
]
Output: [1,2,3,6,9,8,7,4,5]

Example 2:
Input:
[
  [1, 2, 3, 4],
  [5, 6, 7, 8],
  [9,10,11,12]
]
Output: [1,2,3,4,8,12,11,10,9,5,6,7]
</problem>
<bug_fixes>
Replace `len(matrix)` with `len(matrix)-1` on line 6.
Replace `/` with `%` on line 27.
</bug_fixes>
<bug_desc>
On line 6, bottom is set to the number of rows in matrix. This is incorrect because it is out of bounds of the array, resulting in a runtime error. Fix it by setting bottom to len(matrix) - 1.
On line 27, direction+1 is divided by 4, which could result in a floating point number. direction could also take a value higher than 4, which could result in an infinite loop as no variable will be updated. Therefore, using a modulo operation would fix this error.
</bug_desc>
"""
class Solution(object):
    def spiralOrder(self, matrix):
        if matrix == []:
            return []
        top = left = 0
        bottom = len(matrix)
        right = len(matrix[0]) - 1
        direction = 0
        res = []
        while top <= bottom and left <= right:
            if direction == 0:
                for i in range(left,right+1):
                    res.append(matrix[top][i])
                top += 1
            elif direction == 1:
                for i in range(top,bottom+1):
                    res.append(matrix[i][right])
                right -= 1
            elif direction == 2:
                for i in range(right,left-1,-1):
                    res.append(matrix[bottom][i])
                bottom -= 1
            elif direction == 3:
                for i in range(bottom, top-1, -1):
                    res.append(matrix[i][left])
                left += 1
            direction = (direction+1) / 4
        return res