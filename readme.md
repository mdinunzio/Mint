# MintKit
Tools for scraping and analyzing Mint data

## Mint Calculation Notes

- We can calculate **total income** as the sum of all eight Mint "Income" categories (see below).
  Under normal circumstances, this should tie out with the "Income" section of the Mint 
  "Trends" tab. However, these figures may differ by the amount of interest income generated 
  by  retirement accounts, which is reflected in the "Trends" tab but not included in the 
  transactions export.
  
- **"Mortgage & Rent"** is simply the set of any transactions belonging to that Mint category.
  
- We can define **"Wash"** transactions as those belonging to categories (Credit Card Payment, 
  Transfer, Investments, and Duplicate) which do not affect the output of "Spending" and
  "Income" figures in the Mint web UI.
  
- The **"Investments"** category is sometimes assigned by Mint to certain transactions, usually
  those from Coinbase deposits. However, it does not appear in the list of options available 
  to users trying to manually assign a category. Transactions of this type will also not 
  affect the output of "Income" and "Spending" figures in the Mint web UI (e.g. 
  "Spending Over Time"). When Mint does not designate an investment to the "Investments"
  category, it usually assigns it to the "Transfers" category. In this way these user-defined
  investments also avoid influencing Mint's UI calculations given their status as a wash
  transaction.
  
- We can calculate **total spending** as the sum of all transactions less total income, wash
  transactions, and investments. Under normal circumstances, this should tie out with "Spending" 
  in the trends tab. This is spending across all groups except investments (i.e. rent, recurring,
  and discretionary). This figure should almost exactly match the figure in "Trends" under 
  "Spending > Over Time". However, discrepancies may occur due to transactions like 
  "Advisory Fee" (e.g. one from Wealthfront) which are used in calculating "Spending Over 
  Time" in Mint, but not provided in the transactions export. This measures all real spending 
  (by removing wash transactions and factoring in reimbursements such as those through Venmo) 
  which determines monthly cash flow. If we were to add back in all true investments (including
  those erroneously marked "Transfers") we would be able to determine monthly change in net worth.

## User-Defined Group Notes

Groups are defined outside of Mint to illuminate the distinction between recurring expenses, 
discretionary spending, and wash transactions which should be ignored. Additionally, they facilitate
the distinction between net worth change calculations and cash flow change calculations.
There are six possible groups a transaction can fall into:

- **"Rent"** encompasses any transaction with the Mint Category "Mortgage and Rent".
  
- **"Income"** encompasses all the following Mint Categories: Income, Bonus, Interest Income,
  Paycheck, Reimbursement, Rental Income, Returned Purchase.
  
- **"Wash"** encompasses all the following Mint Categories: Credit Card Payment, Transfer, Duplicate.
  
- **"Recurring"** is defined by a custom pattern matching scheme on various columns
  and is designed to represent transactions which happen each month which can be planned
  ahead of time.
  
- **"Investments"** is defined by a custom pattern matching scheme on various columns
  as well as anything assigned to the category "Investments" by Mint. Note that "Investments"
  is not a standard Category normally accessible in the Mint UI. This group is designed
  to represent deposit transactions which happen each month and can be planned ahead of time.
  Additionally, it distinguishes between transactions used to calculate changes in net worth 
  and those used to calculate changes in cash flow.
  
- **"Discretionary"** is any type of spending which does not fall into the above groups.

## Account Notes

- The old Charles Schwab account, "Investor Checking", stopped updating after 2/2/2022. 
  This was replaced by "Investor Checking ...458" which uses the new  authentication protocol.
  Duplicate transactions were manually removed on 2/8/2022.
  