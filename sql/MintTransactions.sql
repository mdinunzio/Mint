CREATE TABLE finances."MintTransactions" (
	"Date" date NOT NULL,
	"Description" varchar NOT NULL,
	"OriginalDescription" varchar NULL,
	"Amount" numeric NULL,
	"TransactionType" varchar NULL,
	"Category" varchar NULL,
	"AccountName" varchar NULL,
	"Labels" varchar NULL,
	"Notes" varchar NULL,
	"UpdateDatetime" timestamp NULL,
	"Group" varchar NULL,
	"Subgroup" varchar NULL
);

CREATE INDEX "MintTransactions_idx_date" ON finances."MintTransactions" (
    "Date" DESC
);

CREATE INDEX "MintTransactions_idx_description" ON finances."MintTransactions" (
    "Description"
);

CREATE INDEX "MintTransactions_idx_transaction_type" ON finances."MintTransactions" (
    "TransactionType"
);

CREATE INDEX "MintTransactions_idx_group" ON finances."MintTransactions" (
    "Group"
);

CREATE INDEX "MintTransactions_idx_subgroup" ON finances."MintTransactions" (
    "Subgroup"
);



COMMENT ON COLUMN finances."MintTransactions"."Date" IS 'The date of the transaction.';
COMMENT ON COLUMN finances."MintTransactions"."Description" IS 'Mint''s description of the transaction.';
COMMENT ON COLUMN finances."MintTransactions"."OriginalDescription" IS 'The original source''s description of the transaction.';
COMMENT ON COLUMN finances."MintTransactions"."Amount" IS 'The amount of the transaction.';
COMMENT ON COLUMN finances."MintTransactions"."TransactionType" IS 'Whether the transaction was a debit or credit.';
COMMENT ON COLUMN finances."MintTransactions"."Category" IS 'Mint''s categorization of the transaction.';
COMMENT ON COLUMN finances."MintTransactions"."AccountName" IS 'The source account of the transaction.';
COMMENT ON COLUMN finances."MintTransactions"."Labels" IS 'Labels from Mint.';
COMMENT ON COLUMN finances."MintTransactions"."Notes" IS 'Notes from Mint.';
COMMENT ON COLUMN finances."MintTransactions"."UpdateDatetime" IS 'The timestamp at which the row was last updated.';
COMMENT ON COLUMN finances."MintTransactions"."Group" IS 'The user-defined group for the transaction.';
COMMENT ON COLUMN finances."MintTransactions"."Subgroup" IS 'The user-defined subgroup for the transaction.';
