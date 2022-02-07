CREATE TABLE finances."MintTransactions" (
	"Date" date NULL,
	"Description" varchar NULL,
	"OriginalDescription" varchar NULL,
	"Amount" numeric NULL,
	"TransactionType" varchar NULL,
	"Category" varchar NULL,
	"AccountName" varchar NULL,
	"Labels" varchar NULL,
	"Notes" varchar NULL,
	"UpdateDatetime" timestamp NULL
);

-- Column comments

COMMENT ON COLUMN finances."MintTransactions"."Date" IS 'The date of the transaction.';
COMMENT ON COLUMN finances."MintTransactions"."Description" IS 'Mint''s description of the transaction.';
COMMENT ON COLUMN finances."MintTransactions"."OriginalDescription" IS 'The orignal source''s description of the transaction.';
COMMENT ON COLUMN finances."MintTransactions"."Amount" IS 'The amount of the transaction.';
COMMENT ON COLUMN finances."MintTransactions"."TransactionType" IS 'Whether the transaction was a debit or credit.';
COMMENT ON COLUMN finances."MintTransactions"."Category" IS 'Mint''s categorization of the transaction.';
COMMENT ON COLUMN finances."MintTransactions"."AccountName" IS 'The source account of the transaction.';
COMMENT ON COLUMN finances."MintTransactions"."Labels" IS 'Labels from Mint.';
COMMENT ON COLUMN finances."MintTransactions"."Notes" IS 'Notes from Mint.';
COMMENT ON COLUMN finances."MintTransactions"."UpdateDatetime" IS 'The timestamp at which the row was last updated.';
