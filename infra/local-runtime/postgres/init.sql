CREATE TABLE IF NOT EXISTS runtime_metadata (
    namespace TEXT NOT NULL,
    key TEXT NOT NULL,
    payload JSONB NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (namespace, key)
);

CREATE INDEX IF NOT EXISTS idx_runtime_metadata_namespace ON runtime_metadata(namespace);
