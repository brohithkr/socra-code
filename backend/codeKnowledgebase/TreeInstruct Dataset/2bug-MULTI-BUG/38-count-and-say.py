"""
<problem>
Problem Link: https://leetcode.com/problems/count-and-say/

The count-and-say sequence is the sequence of integers with the first five terms as following:
1.     1
2.     11
3.     21
4.     1211
5.     111221
1 is read off as "one 1" or 11.
11 is read off as "two 1s" or 21.
21 is read off as "one 2, then one 1" or 1211.

Given an integer n where 1 ≤ n ≤ 30, generate the nth term of the count-and-say sequence.
Note: Each term of the sequence of integers will be represented as a string.

Example 1:
Input: 1
Output: "1"

Example 2:
Input: 4
Output: "1211"
</problem>
<bug_fixes>
Replace `for i in range(s)` with `for i in s` on line 8.
Replace `res.join("")` with `"".join(res)` on line 18.
</bug_fixes>
<bug_desc>
On line 8, the range function is used incorrectly since the string s is passed into the function. This is a syntactical mistake and should be changed to `for i in s` to iterate over the characters of s correctly.
On line 18, a runtime error occurs because the list res does not have a function called join. This is a syntactical mistake as the correct syntax for the join is: "".join(res).
</bug_desc>
"""
class Solution(object):
    def countAndSay(self, n):
        if n == 1:
            return "1"
        s = "1"
        for _ in range(n-1):
            curVal,count,res = s[0], 0, []
            for i in range(s):
                if curVal == i:
                    count += 1
                else:
                    res.append(str(count))
                    res.append(curVal)
                    curVal = i
                    count = 1
            res.append(str(count))
            res.append(curVal)
            s = res.join("")
        return s
