-- =============================================================================
-- A) Pool membership
-- =============================================================================
SELECT pm.pool_id, pm.sample_id
FROM pool_members pm
WHERE pm.pool_id = 'POOL_0001'
ORDER BY pm.sample_id;

-- =============================================================================
-- B) Pools that triggered reflex testing
-- =============================================================================
SELECT entity_id AS pool_id, result, ct_value, tested_at
FROM tests
WHERE entity_type='POOL' AND result IN ('BORDERLINE','POS')
ORDER BY tested_at;

-- =============================================================================
-- C) Lineage for one sample (pool → pool test → reflex test)
-- =============================================================================
SELECT s.sample_id,
       pm.pool_id,
       pt.result AS pool_result,
       pt.ct_value AS pool_ct,
       rt.result AS reflex_result,
       rt.ct_value AS reflex_ct
FROM samples s
JOIN pool_members pm ON pm.sample_id = s.sample_id
LEFT JOIN tests pt ON pt.entity_type='POOL' AND pt.entity_id = pm.pool_id
LEFT JOIN tests rt ON rt.entity_type='SAMPLE' AND rt.entity_id = s.sample_id
WHERE s.sample_id = 'SAMPLE_0042';

-- =============================================================================
-- D) Exception detection (pool needs reflex but a member is missing reflex test)
-- =============================================================================
SELECT pm.pool_id, pm.sample_id
FROM pool_members pm
JOIN tests pt ON pt.entity_type='POOL' AND pt.entity_id = pm.pool_id
LEFT JOIN tests rt ON rt.entity_type='SAMPLE' AND rt.entity_id = pm.sample_id
WHERE pt.result IN ('BORDERLINE','POS')
  AND rt.test_id IS NULL
ORDER BY pm.pool_id, pm.sample_id;

-- =============================================================================
-- E) Derive "final status" (simple rule)
-- =============================================================================
SELECT s.sample_id,
       pm.pool_id,
       pt.result AS pool_result,
       rt.result AS reflex_result,
       CASE
         WHEN pt.result = 'NEG' THEN 'FINAL_NEG'
         WHEN rt.result IN ('POS','BORDERLINE') THEN 'FINAL_POS_REVIEW'
         WHEN rt.result = 'NEG' THEN 'FINAL_NEG'
         ELSE 'PENDING_REFLEX'
       END AS final_status
FROM samples s
JOIN pool_members pm ON pm.sample_id = s.sample_id
JOIN tests pt ON pt.entity_type='POOL' AND pt.entity_id = pm.pool_id
LEFT JOIN tests rt ON rt.entity_type='SAMPLE' AND rt.entity_id = pm.sample_id
ORDER BY final_status, pm.pool_id, s.sample_id;
