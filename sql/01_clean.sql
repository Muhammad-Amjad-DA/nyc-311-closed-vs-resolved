-- 01_clean.sql | Load 12 months of NYC 311 requests (created 2025-01-01 to 2025-12-31) and build the clean table.
-- Engine: DuckDB (PostgreSQL-compatible syntax). Every rule is logged in docs/data_quality_log.md.

CREATE OR REPLACE TABLE raw AS
SELECT * FROM read_csv_auto('data/311_2025_*.csv', union_by_name = true,
       types = {'unique_key': 'VARCHAR', 'incident_zip': 'VARCHAR'}, sample_size = -1);

-- Rule 1: unique_key must be unique.
CREATE OR REPLACE TABLE dedup AS SELECT DISTINCT * FROM raw;

-- Rule 2: classify the free-text resolution into an outcome bucket with transparent keyword rules.
-- Order matters: the first matching rule wins. Rules are deliberately conservative.
CREATE OR REPLACE TABLE tickets AS
SELECT
    unique_key,
    created_date,
    closed_date,
    agency,
    complaint_type,
    descriptor,
    CASE WHEN borough IS NULL OR borough = 'Unspecified' THEN NULL ELSE borough END AS borough,
    UPPER(TRIM(incident_address))                    AS address,
    status,
    resolution_description,
    CASE
        WHEN closed_date IS NULL                                   THEN NULL
        WHEN closed_date < created_date                            THEN NULL     -- impossible duration
        ELSE DATE_DIFF('minute', created_date, closed_date) / 60.0
    END AS hours_to_close,
    CASE
        WHEN resolution_description IS NULL OR resolution_description = 'N/A'                          THEN 'no_resolution_text'
        WHEN regexp_matches(LOWER(resolution_description), 'duplicate|earlier complaint about the same location')
                                                                                                       THEN 'duplicate'
        WHEN regexp_matches(LOWER(resolution_description),
             'unable to gain|not able to gain|unable to complete the inspection|could not gain|were gone|could not find the person|attempted to investigate')
                                                                                                       THEN 'could_not_reach_or_gone'
        WHEN regexp_matches(LOWER(resolution_description),
             'took action to fix|summons|violations were issued|found violations|notice of violation|repaired|cleaned the location|collected the requested|removed the items|completed the requested work|shut the running|a violation of law occurred|corrected the problem|correct the condition|corrected the condition')
                                                                                                       THEN 'action_taken'
        WHEN regexp_matches(LOWER(resolution_description),
             'indicated that the condition was corrected|confirmed heat and hot water had been restored|verified that the following conditions were corrected')
                                                                                                       THEN 'fixed_per_caller_unverified'
        WHEN regexp_matches(LOWER(resolution_description),
             'no evidence|no violation|did not violate|no condition|could not find the problem|couldn''t find the condition|no criminal violation|action was not necessary|no further action|no encampment|no work is necessary|not find|didn''t observe|temporary condition|meets its standards|valid permit')
                                                                                                       THEN 'no_finding'
        WHEN regexp_matches(LOWER(resolution_description), 'jurisdiction|website|hpdonline|reviewed (this|your) complaint|additional information|conducted or attempted|referred|lead test kit|responded to your service request')
                                                                                                       THEN 'info_or_referral'
        ELSE 'other'
    END AS outcome
FROM dedup;
