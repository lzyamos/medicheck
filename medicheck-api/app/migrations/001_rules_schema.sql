-- =========================
-- Medicheck Rules Schema v1
-- =========================

BEGIN;

-- Optional: keep rules isolated
CREATE SCHEMA IF NOT EXISTS medicheck;

-- -------------
-- Enumerations
-- -------------
DO $$ BEGIN
  CREATE TYPE medicheck.rule_status AS ENUM ('draft', 'active', 'inactive', 'archived');
EXCEPTION
  WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
  CREATE TYPE medicheck.rule_severity AS ENUM ('info', 'low', 'medium', 'high', 'critical');
EXCEPTION
  WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
  CREATE TYPE medicheck.rule_scope AS ENUM ('global', 'patient', 'doctor', 'institution');
EXCEPTION
  WHEN duplicate_object THEN NULL;
END $$;

-- -----------------------
-- Symptom dictionary
-- -----------------------
-- A normalized set of symptom "keys" to avoid free-text chaos.
CREATE TABLE IF NOT EXISTS medicheck.symptoms (
  id            BIGSERIAL PRIMARY KEY,
  key           TEXT NOT NULL UNIQUE,            -- e.g. "fever", "chest_pain"
  display_name  TEXT NOT NULL,                   -- e.g. "Fever"
  description   TEXT,
  is_red_flag   BOOLEAN NOT NULL DEFAULT FALSE,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_symptoms_is_red_flag ON medicheck.symptoms(is_red_flag);

-- -----------------------
-- Rule modules (complaints)
-- -----------------------
-- Modules help you scale: "respiratory", "abdominal_pain", "chest_pain", etc.
CREATE TABLE IF NOT EXISTS medicheck.rule_modules (
  id           BIGSERIAL PRIMARY KEY,
  key          TEXT NOT NULL UNIQUE,     -- e.g. "respiratory"
  name         TEXT NOT NULL,            -- e.g. "Respiratory"
  description  TEXT,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- -----------------------
-- Rules (versioned)
-- -----------------------
-- Current active rules live here.
-- Condition logic and outputs are JSONB to keep it flexible.
CREATE TABLE IF NOT EXISTS medicheck.rules (
  id              BIGSERIAL PRIMARY KEY,
  module_id       BIGINT REFERENCES medicheck.rule_modules(id) ON DELETE SET NULL,

  -- Basic metadata
  name            TEXT NOT NULL,
  description     TEXT,
  status          medicheck.rule_status NOT NULL DEFAULT 'draft',
  severity        medicheck.rule_severity NOT NULL DEFAULT 'info',
  scope           medicheck.rule_scope NOT NULL DEFAULT 'global',

  -- Ordering / tie-breaks
  priority        INT NOT NULL DEFAULT 100,   -- lower = evaluated/returned earlier
  weight          INT NOT NULL DEFAULT 0,     -- used later for ranking "likely conditions"

  -- JSON logic
  -- Expected shape (example):
  -- {
  --   "all": [
  --     {"fact":"symptom","op":"has","value":"chest_pain"},
  --     {"fact":"symptom","op":"has","value":"shortness_of_breath"},
  --     {"fact":"age","op":">=","value":40}
  --   ],
  --   "any": [
  --     {"fact":"duration_hours","op":">=","value":1}
  --   ],
  --   "none": [
  --     {"fact":"pregnant","op":"==","value":true}
  --   ]
  -- }
  conditions      JSONB NOT NULL,

  -- JSON outputs
  -- Expected shape (example):
  -- {
  --   "triage": {"level":"emergency","reason":"Possible cardiac/pulmonary emergency"},
  --   "recommendations": [
  --     {"type":"action","text":"Go to ER now"},
  --     {"type":"test","text":"ECG"},
  --     {"type":"test","text":"Troponin"}
  --   ]
  -- }
  outcomes        JSONB NOT NULL,

  -- Audit
  created_by      TEXT,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Helpful indexes
CREATE INDEX IF NOT EXISTS idx_rules_status ON medicheck.rules(status);
CREATE INDEX IF NOT EXISTS idx_rules_module ON medicheck.rules(module_id);
CREATE INDEX IF NOT EXISTS idx_rules_priority ON medicheck.rules(priority);
CREATE INDEX IF NOT EXISTS idx_rules_scope ON medicheck.rules(scope);
CREATE INDEX IF NOT EXISTS idx_rules_severity ON medicheck.rules(severity);

-- JSONB GIN indexes for faster search/filter later
CREATE INDEX IF NOT EXISTS idx_rules_conditions_gin ON medicheck.rules USING GIN (conditions);
CREATE INDEX IF NOT EXISTS idx_rules_outcomes_gin ON medicheck.rules USING GIN (outcomes);

-- -----------------------
-- Rule tags (optional but useful)
-- -----------------------
CREATE TABLE IF NOT EXISTS medicheck.rule_tags (
  id          BIGSERIAL PRIMARY KEY,
  key         TEXT NOT NULL UNIQUE,     -- e.g. "red_flag", "respiratory", "peds"
  name        TEXT NOT NULL,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS medicheck.rule_tag_map (
  rule_id  BIGINT NOT NULL REFERENCES medicheck.rules(id) ON DELETE CASCADE,
  tag_id   BIGINT NOT NULL REFERENCES medicheck.rule_tags(id) ON DELETE CASCADE,
  PRIMARY KEY (rule_id, tag_id)
);

-- -----------------------
-- Rule versions (history)
-- -----------------------
CREATE TABLE IF NOT EXISTS medicheck.rule_versions (
  id           BIGSERIAL PRIMARY KEY,
  rule_id      BIGINT NOT NULL REFERENCES medicheck.rules(id) ON DELETE CASCADE,
  version      INT NOT NULL,
  snapshot     JSONB NOT NULL,         -- full rule snapshot at time of save
  created_by   TEXT,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(rule_id, version)
);

CREATE INDEX IF NOT EXISTS idx_rule_versions_rule_id ON medicheck.rule_versions(rule_id);

-- -----------------------
-- Seed: modules
-- -----------------------
INSERT INTO medicheck.rule_modules(key, name, description)
VALUES
  ('global_red_flags', 'Global Red Flags', 'Applies across all complaints'),
  ('respiratory', 'Respiratory', 'Cough, fever, SOB, wheeze'),
  ('chest_pain', 'Chest Pain', 'Chest discomfort and related symptoms'),
  ('abdominal_pain', 'Abdominal Pain', 'GI pain complaints'),
  ('urinary', 'Urinary', 'UTI and urinary symptoms'),
  ('headache', 'Headache', 'Headache and neuro screening')
ON CONFLICT (key) DO NOTHING;

-- -----------------------
-- Seed: symptoms (starter set)
-- -----------------------
INSERT INTO medicheck.symptoms(key, display_name, description, is_red_flag)
VALUES
  ('chest_pain', 'Chest pain', 'Any chest pressure/pain', true),
  ('shortness_of_breath', 'Shortness of breath', 'Breathing difficulty', true),
  ('confusion', 'Confusion', 'New confusion or altered mental status', true),
  ('fainting', 'Fainting', 'Syncope or near-syncope', true),
  ('severe_headache', 'Severe headache', 'Worst headache of life / sudden', true),
  ('neck_stiffness', 'Neck stiffness', 'Meningeal signs', true),
  ('high_fever', 'High fever', 'High temperature', false),
  ('cough', 'Cough', 'Cough (dry or productive)', false),
  ('sore_throat', 'Sore throat', 'Pain with swallowing', false),
  ('dysuria', 'Painful urination', 'Burning with urination', false)
ON CONFLICT (key) DO NOTHING;

-- -----------------------
-- Seed: tags
-- -----------------------
INSERT INTO medicheck.rule_tags(key, name)
VALUES
  ('red_flag', 'Red Flag'),
  ('triage', 'Triage'),
  ('starter', 'Starter Rule Set')
ON CONFLICT (key) DO NOTHING;

-- -----------------------
-- Seed: example red-flag rule
-- -----------------------
-- "Chest pain AND shortness of breath -> emergency"
WITH mod AS (
  SELECT id AS module_id FROM medicheck.rule_modules WHERE key = 'global_red_flags'
),
ins AS (
  INSERT INTO medicheck.rules(
    module_id, name, description, status, severity, scope, priority, weight, conditions, outcomes, created_by
  )
  SELECT
    mod.module_id,
    'Chest pain + shortness of breath',
    'Potential cardiac/pulmonary emergency red flag',
    'active',
    'critical',
    'global',
    1,
    0,
    '{
      "all": [
        {"fact":"symptom","op":"has","value":"chest_pain"},
        {"fact":"symptom","op":"has","value":"shortness_of_breath"}
      ]
    }'::jsonb,
    '{
      "triage": {"level":"emergency", "reason":"Chest pain with shortness of breath is a red flag."},
      "recommendations": [
        {"type":"action","text":"Seek emergency care immediately."},
        {"type":"action","text":"Do not drive yourself if you feel unwell—call emergency services."}
      ]
    }'::jsonb,
    'seed'
  FROM mod
  ON CONFLICT DO NOTHING
  RETURNING id
)
INSERT INTO medicheck.rule_tag_map(rule_id, tag_id)
SELECT ins.id, t.id
FROM ins
JOIN medicheck.rule_tags t ON t.key IN ('red_flag', 'triage', 'starter')
ON CONFLICT DO NOTHING;

COMMIT;
