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
Add a colon to the if-condition on line 8.
Add a return statement on line 13 to `return head`.
</bug_fixes>
<bug_desc>
On line 3, p2 starts from the second node in the linked list. This could result in a runtime error as the (n+1)st node could be accessed. Instead, set p2 to head.
On line 8, the if-condition has no colon. This is a syntactial mistake that results in a runtime error as the if-condition is not terminated. Adding a colon at the end will fix the mistake.
On line 13, or after line 12, there is no return statement from the method. This results in incorrect behavior. It can be fixed by returning head from the method.
</bug_desc>
"""
class Solution(object):
    def removeNthFromEnd(self, head, n):
        p1,p2 = head,head.next
        if not head:
            return head
        for i in range(n):
            p1 = p1.next
        if not p1
            return p2.next
        while p1.next != None:
            p1 = p1.next
            p2 = p2.next
        p2.next = p2.next.next
        