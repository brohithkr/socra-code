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
</bug_fixes>
<bug_desc>
On line 4, nodes_sum is set to None, which means it is not an integer but, it is treated as an integer. This results in a runtime error. Therefore, nodes_sum should be set to 0.
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
          l2 = l2.next
        cur.next = ListNode(nodes_sum % 10)
        cur = cur.next
        nodes_sum //= 10
      return res.next
