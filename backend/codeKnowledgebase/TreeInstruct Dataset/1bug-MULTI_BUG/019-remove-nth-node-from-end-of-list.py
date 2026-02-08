"""
<problem>
Problem Link: https://leetcode.com/problems/remove-nth-node-from-end-of-list/

Given a linked list, remove the n-th node from the end of list and return its head.

Example:
Given linked list: 1->2->3->4->5, and n = 2.
After removing the second node from the end, the linked list becomes 1->2->3->5.

Note:
Given n will always be valid.

Follow up:
Could you do this in one pass?
</problem>
<bug_fixes>
Replace `p1,p2 = head,head.next` with `p1,p2 = head,head` on line 3.
</bug_fixes>
<bug_desc>
On line 3, p2 starts from the second node in the linked list. This could result in a runtime error as the (n+1)st node could be accessed. Instead, set p2 to head.
</bug_desc>
"""
class Solution(object):
    def removeNthFromEnd(self, head, n):
        p1,p2 = head,head.next
        if not head:
            return head
        for i in range(n):
            p1 = p1.next
        if not p1:
            return p2.next
        while p1.next != None:
            p1 = p1.next
            p2 = p2.next
        p2.next = p2.next.next
        return head