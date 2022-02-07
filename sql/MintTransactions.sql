CREATE TABLE public."MintTransactions" (
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

COMMENT ON COLUMN public.minttransactions."Date" IS 'The date of the transaction.';
COMMENT ON COLUMN public.minttransactions."Description" IS 'Mint''s description of the transaction.';
COMMENT ON COLUMN public.minttransactions."OriginalDescription" IS 'The orignal source''s description of the transaction.';
COMMENT ON COLUMN public.minttransactions."Amount" IS 'The amount of the transaction.';
COMMENT ON COLUMN public.minttransactions."TransactionType" IS 'Whether the transaction was a debit or credit.';
COMMENT ON COLUMN public.minttransactions."Category" IS 'Mint''s categorization of the transaction.';
COMMENT ON COLUMN public.minttransactions."AccountName" IS 'The source account of the transaction.';
COMMENT ON COLUMN public.minttransactions."Labels" IS 'Labels from Mint.';
COMMENT ON COLUMN public.minttransactions."Notes" IS 'Notes from Mint.';
COMMENT ON COLUMN public.minttransactions."UpdateDatetime" IS 'The timestamp at which the row was last updated.';
