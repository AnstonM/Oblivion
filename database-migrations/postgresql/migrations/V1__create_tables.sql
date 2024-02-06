CREATE TABLE public."HistoricalPrice"(
    "isin" VARCHAR(40) PRIMARY KEY,
    "price" BIGINT NOT NULL,
    "date" DATE NOT NULL,
    "isActive" BOOLEAN NOT NULL DEFAULT TRUE
);
