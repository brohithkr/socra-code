"""
<problem>
Problem Link: https://leetcode.com/problems/swap-nodes-in-pairs/

Given a linked list, swap every two adjacent nodes and return its head.
You may not modify the values in the list's nodes, only nodes itself may be changed.

Example:
Given 1->2->3->4, you should return the list as 2->1->4->3.
</problem>
<bug_fixes>
Add `head = head.next` on line 11.
Add `return cur` on line 15.
</bug_fixes>
<bug_desc>
On line 11, the head node is never updated, which results in an incorrect order of ndoes. To fix the mistake, simply add `head = head.next` on line 11.
On line 15, or after line 14, nothing is returned from the method, which results in an incorrect output. Adding `return cur` will fix this mistake.
</bug_desc>
"""
class Solution(object):
    def swapPairs(self, head):
        if not head:
            return None
        cur = head.next if head.next else head
        prev = None
        while head and head.next:
            temp = head.next
            head.next = head.next.next
            temp.next = head

            if prev:
                prev.next = temp
            prev = temp.next
            