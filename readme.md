# MintKit
Tools for scraping and analyzing Mint data

## Group Notes
Groups are defined outside of Mint to illuminate the distinction between recurring expenses, 
discretionary spending, and wash transactions which should be ignored. Additionally, they facilitate
the distinction between net worth change calculations and cash flow change calculations.
There are six possible groups a transaction can fall into:
- **Rent** encompasses any transaction with the Mint Category "Mortgage and Rent".
- **Income** encompasses all the following Mint Categories: Income, Bonus, Interest Income,
  Paycheck, Reimbursement, Rental Income, Returned Purchase.
- **Wash** encompasses all the following Mint Categories: Credit Card Payment, Transfer, 
  Investments, Duplicate.
- **Recurring** is defined by a custom pattern matching scheme on various columns
  and is designed to represent transactions which happen each month and can
  be planned for.
- **Investments** is defined by a custom pattern matching scheme on various columns
  as well as anything given the category "Investments" by Mint. Note that "Investments"
  is not a standard Category normally accessible in the Mint UI. This group is designed
  to represent transactions which happen each month and can be planned for. Additionally
  they determine the distinction between transactions that diminish both net worth and
  cash flow and those that just diminish cash flow.
- **Discretionary** is any type of spending which does not fall into the above groups.

TODO: Expand the

## Account Notes
- The old Charles Schwab account, "Investor Checking", stopped updating after 2/2/2022. 
  This was replaced by "Investor Checking ...458" which uses the new  authentication protocol.