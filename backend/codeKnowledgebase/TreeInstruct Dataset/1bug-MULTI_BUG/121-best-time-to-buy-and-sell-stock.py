"""
<problem>
Problem Link: https://leetcode.com/problems/best-time-to-buy-and-sell-stock/description/

Say you have an array for which the ith element is the price of a given stock on day i.
If you were only permitted to complete at most one transaction (i.e., buy one and sell one share of the stock), 
design an algorithm to find the maximum profit.
Note that you cannot sell a stock before you buy one.

Example 1
Input: [7,1,5,3,6,4]
Output: 5
Explanation: Buy on day 2 (price = 1) and sell on day 5 (price = 6), profit = 6-1 = 5.
             Not 7-1 = 6, as selling price needs to be larger than buying price.

Example 2:
Input: [7,6,4,3,1]
Output: 0
Explanation: In this case, no transaction is done, i.e. max profit = 0.
</problem>
<bug_fixes>
Replace `profit` with `return profit` on line 10.
</bug_fixes>
<bug_desc>
On line 10, there is no return keyword to prepend profit. Therefore, nothing is returned, which is incorrect behavior. To fix this, use the return keyword in front of profit.
</bug_desc>
"""
class Solution(object):
    def maxProfit(self, prices):
        if not prices:return 0
        profit, buy = 0, prices[0]
        for price in prices:
            if price > buy:
                profit = (price-buy) if (price-buy) > profit else profit
            else:
                buy = price
        profit