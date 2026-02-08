"""
<problem>
Problem Link: https://leetcode.com/problems/fizz-buzz/

Write a program that outputs the string representation of numbers from 1 to n.
But for multiples of three it should output “Fizz” instead of the number and for the multiples of five output 
“Buzz”. For numbers which are multiples of both three and five output “FizzBuzz”.

Example:

n = 15,

Return:
[
    "1",
    "2",
    "Fizz",
    "4",
    "Buzz",
    "Fizz",
    "7",
    "8",
    "Fizz",
    "Buzz",
    "11",
    "Fizz",
    "13",
    "14",
    "FizzBuzz"
]
</problem>
<bug_fixes>
Replace `or` with `and` on line 8.
Add `return result` on line 16.
</bug_fixes>
<bug_desc>
On line 8, the if-condition check if i is divisible by 3 or 5. This is incorrect behavior because r3+r5 is appended if either is true. It should be appended if both are true.
On line 16, or after line 15, nothing is returned from the method, which is incorrect behavior. This is a syntactical mistake that can be resolved by returning result from the method.
</bug_desc>
"""
class Solution:
    def fizzBuzz(self, n):
        result = []
        r5 = "Buzz"
        r3 = "Fizz"
        for i in range(1,n+1):
            print(i)
            if i % 3 == 0 or i % 5 ==0:
                result.append(r3+r5)
            elif i % 3 == 0:
                result.append(r3)
            elif i % 5 == 0:
                result.append(r5)
            else:
                result.append(str(i))
