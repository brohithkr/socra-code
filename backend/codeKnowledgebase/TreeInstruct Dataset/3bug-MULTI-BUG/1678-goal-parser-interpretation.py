"""
<problem>
Problem Link: https://leetcode.com/problems/goal-parser-interpretation/

You own a Goal Parser that can interpret a string command. The command consists of an alphabet of "G", "()" and/or "(al)" 
in some order. The Goal Parser will interpret "G" as the string "G", "()" as the string "o", and "(al)" as the string "al". 
The interpreted strings are then concatenated in the original order.
Given the string command, return the Goal Parser's interpretation of command.

Example 1:
Input: command = "G()(al)"
Output: "Goal"
Explanation: The Goal Parser interprets the command as follows:
G -> G
() -> o
(al) -> al
The final concatenated result is "Goal".

Example 2:
Input: command = "G()()()()(al)"
Output: "Gooooal"

Example 3:
Input: command = "(al)G(al)()()G"
Output: "alGalooG"
 
Constraints:
1 <= command.length <= 100
</problem>
<bug_fixes>
Add `is_o = False` to line 9.
Replace `else if` with `elif` on line 10.
Replace `res.join("")` with "".join(res) on line 16.
</bug_fixes>
<bug_desc>
On line 9, after finding a ')', is_o must be set to False, ottherwise incorrect behavior will occur. Without setting it to False, it might never go back fom True to False, which will result in incorrect behavior. Therefore, once ')' is found, is_o must be set to False.
On line 10, incorrect syntax is used for the else-if block. In Python, else-if is spelled elif.
On line 16, the join() method is used incorrectly, as it is a string method. To fix the bug, reverse the arguments like so: "".join(res).
</bug_desc>
"""
class Solution:
    def interpret(self, command: str) -> str:
        res = []
        is_o = False
        for i in range(len(command)):
            if command[i] == ")":
                if is_o:
                    res.append('o')
                
            else if command[i] == "(":
                is_o = True
            else:
                res.append(command[i])
                is_o = False
                
        return res.join("")