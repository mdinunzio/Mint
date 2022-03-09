CREATE TABLE finances."MintBudgets_dev" (
    "Column" varchar NOT NULL,
    "Group" varchar NOT NULL,
    "Subgroup" varchar NOT NULL,
    "Schedule" varchar NOT NULL,
    "Regex" varchar NOT NULL,
    "AllocatedAmount" numeric NULL,
    "MatchAmount" bool NOT NULL DEFAULT FALSE,
    "Website" varchar NULL,
    "Login" varchar NULL,
    "Notes" varchar NULL,
    "AsOfDate" date NOT NULL,
    "AppraisalDate" date NULL
);

COMMENT ON COLUMN finances."MintBudgets_dev"."Column" IS 'The name of the column on which to perform regex matching.';
COMMENT ON COLUMN finances."MintBudgets_dev"."Group" IS 'The group to assign to the transaction if a match occurs';
COMMENT ON COLUMN finances."MintBudgets_dev"."Subgroup" IS 'The subgroup to assign to the transaction if a match occurs';
COMMENT ON COLUMN finances."MintBudgets_dev"."Schedule" IS 'How often this transaction occurs.';
COMMENT ON COLUMN finances."MintBudgets_dev"."Regex" IS 'The regular expression used to match a transaction.';
COMMENT ON COLUMN finances."MintBudgets_dev"."AllocatedAmount" IS 'The amount allocated for a transaction.';
COMMENT ON COLUMN finances."MintBudgets_dev"."MatchAmount" IS 'If TRUE, the transaction amount must equal the allocated amount to be considered a match.';
COMMENT ON COLUMN finances."MintBudgets_dev"."Website" IS 'The website associated with this budget item.';
COMMENT ON COLUMN finances."MintBudgets_dev"."Login" IS 'Any logins associated with this budget item (comma separated).';
COMMENT ON COLUMN finances."MintBudgets_dev"."Notes" IS 'Any notes associated with this budget item.';
COMMENT ON COLUMN finances."MintBudgets_dev"."AsOfDate" IS 'The date the budget item was uploaded.';
COMMENT ON COLUMN finances."MintBudgets_dev"."AppraisalDate" IS 'The last date on which the budget item was appraised.';
