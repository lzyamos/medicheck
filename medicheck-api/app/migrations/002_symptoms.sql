CREATE TABLE IF NOT EXISTS symptom_sessions (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  patient_id uuid NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
  created_by_user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  role_context user_role NOT NULL,
  answers_json jsonb NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS analysis_outputs (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  symptom_session_id uuid NOT NULL REFERENCES symptom_sessions(id) ON DELETE CASCADE,
  insights_json jsonb NOT NULL,
  recommended_tests_json jsonb NOT NULL,
  urgency text NOT NULL CHECK (urgency IN ('ROUTINE','PROMPT','URGENT')),
  safety_statement text NOT NULL,
  model_version text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_symptom_sessions_patient ON symptom_sessions(patient_id);
CREATE INDEX IF NOT EXISTS idx_analysis_outputs_session ON analysis_outputs(symptom_session_id);
