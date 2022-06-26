CREATE TABLE global_table_test (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    create_time TIMESTAMPTZ NOT NULL DEFAULT now():::TIMESTAMPTZ,
    rowid INT8 NOT NULL DEFAULT unique_rowid(),
    worker VARCHAR(50) NOT NULL,
    cluster_node INT8 NOT NULL,
    gateway_region VARCHAR(50) NULL,
    gateway_az VARCHAR(50) NULL,
    lease_holder INT8 NULL,
    int8_col INT8 NULL,
    varchar50_col VARCHAR(50) NULL,
    bool_col BOOL NULL,
    jsonb_col JSONB NULL,
    CONSTRAINT glbal_table_test_pkey PRIMARY KEY (id ASC)
) LOCALITY GLOBAL;


