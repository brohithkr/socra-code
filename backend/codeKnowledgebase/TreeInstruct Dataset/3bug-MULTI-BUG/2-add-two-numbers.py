"""
<problem>
Problem Link: https://leetcode.com/problems/add-two-numbers/

You are given two non-empty linked lists representing two non-negative integers. The digits are stored in reverse order 
and each of their nodes contain a single digit. Add the two numbers and return it as a linked list.
You may assume the two numbers do not contain any leading zero, except the number 0 itself.

Example:
Input: (2 -> 4 -> 3) + (5 -> 6 -> 4)
Output: 7 -> 0 -> 8
Explanation: 342 + 465 = 807.
</problem>
<bug_fixes>
Replace `nodes_sum = None` with `nodes_sum = 0` on line 4.
Replace `cur.next = ListNode(nodes_sum / 10)` with `cur.next = ListNode(nodes_sum % 10)` on line 12.
Replace `l2 - l2.next` to `l2 = l2.next` on line 11.
</bug_fixes>
<bug_desc>
On line 4, nodes_sum is set to None, which means it is not an integer but, it is treated as an integer. This results in a runtime error. Therefore, nodes_sum should be set to 0.
On line 12, nodes_sum is divided by 10, which disrupts the carry logic, and sets the wrong value in place. Therefore, the division operation must be changes to a modulo operation.
On line 11, l2.next is subtracted from l2. This is a syntactical mistake, where the subtraction symbol should be the equate symbol. The line should read `l2 = l2.next`.
</bug_desc>
"""
class Solution:
    def addTwoNumbers(self, l1: ListNode, l2: ListNode) -> ListNode:
      res = cur = ListNode(0)
      nodes_sum = None
      while l1 or l2 or nodes_sum:
        if l1:
          nodes_sum += l1.val
          l1 = l1.next
        if l2:
          nodes_sum += l2.val
          l2 - l2.next
        cur.next = ListNode(nodes_sum / 10)
        cur = cur.next
        nodes_sum //= 10
      return res.next
