"""
<problem>
Problem Link: https://leetcode.com/problems/merge-k-sorted-lists/

Merge k sorted linked lists and return it as one sorted list. Analyze and describe its complexity.

Example:
Input:
[
  1->4->5,
  1->3->4,
  2->6
]
Output: 1->1->2->3->4->4->5->6
</problem>
"""
class Solution:
    def mergeKLists(self, lists: List[ListNode]) -> ListNode:
      res = ListNode(0)
      cur = res
      while cur:
        minNode,index = None, -1
        for i in range(len(lists)):
          if lists[i]:
            if not minNode or minNode.val > lists[i].val:
              minNode = lists[i]
              index = i
        if index != -1:
          lists[index] = lists[index].next
        cur.next, cur = minNode, minNode
      return res.next