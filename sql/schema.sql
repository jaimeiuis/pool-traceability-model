PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS tests;
DROP TABLE IF EXISTS pool_members;
DROP TABLE IF EXISTS pools;
DROP TABLE IF EXISTS samples;

CREATE TABLE samples (
  sample_id   TEXT PRIMARY KEY,
  patient_id  TEXT NOT NULL,
  site_id     TEXT NOT NULL,
  collected_at TEXT NOT NULL
);

CREATE TABLE pools (
  pool_id      TEXT PRIMARY KEY,
  created_at   TEXT NOT NULL,
  pool_strategy TEXT NOT NULL,
  notes        TEXT
);

CREATE TABLE pool_members (
  pool_id   TEXT NOT NULL,
  sample_id TEXT NOT NULL,
  PRIMARY KEY (pool_id, sample_id),
  FOREIGN KEY (pool_id) REFERENCES pools(pool_id),
  FOREIGN KEY (sample_id) REFERENCES samples(sample_id)
);

CREATE TABLE tests (
  test_id      TEXT PRIMARY KEY,
  entity_type  TEXT NOT NULL CHECK(entity_type IN ('POOL', 'SAMPLE')),
  entity_id    TEXT NOT NULL,
  run_id       TEXT NOT NULL,
  result       TEXT NOT NULL CHECK(result IN ('NEG', 'BORDERLINE', 'POS')),
  ct_value     REAL,
  tested_at    TEXT NOT NULL,
  reflex_triggered INTEGER NOT NULL CHECK(reflex_triggered IN (0,1))
);

CREATE INDEX idx_tests_entity ON tests(entity_type, entity_id);
CREATE INDEX idx_pool_members_sample ON pool_members(sample_id);
