-- AgentDB Schema for Python Port
-- Cognitive memory system for autonomous AI agents
-- Ported from: https://github.com/ruvnet/agentic-flow/tree/main/packages/agentdb

-- Episodic memory (Reflexion-style replay with self-critique)
CREATE TABLE IF NOT EXISTS episodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task TEXT NOT NULL,
    input TEXT,
    output TEXT,
    critique TEXT,
    reward REAL DEFAULT 0.0,
    success INTEGER DEFAULT 0,
    namespace TEXT DEFAULT 'default',
    metadata_json TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Episode embeddings for vector similarity search
CREATE TABLE IF NOT EXISTS episode_embeddings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    episode_id INTEGER NOT NULL,
    embedding BLOB NOT NULL,
    model TEXT DEFAULT 'default',
    dimensions INTEGER DEFAULT 384,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (episode_id) REFERENCES episodes(id) ON DELETE CASCADE
);

-- Reusable skill patterns
CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    code TEXT,
    signature TEXT,
    success_rate REAL DEFAULT 0.0,
    usage_count INTEGER DEFAULT 0,
    namespace TEXT DEFAULT 'default',
    metadata_json TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Skill relationships
CREATE TABLE IF NOT EXISTS skill_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_skill_id INTEGER NOT NULL,
    target_skill_id INTEGER NOT NULL,
    link_type TEXT NOT NULL CHECK(link_type IN ('prerequisite', 'alternative', 'refinement', 'composition')),
    weight REAL DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    FOREIGN KEY (target_skill_id) REFERENCES skills(id) ON DELETE CASCADE
);

-- Skill embeddings
CREATE TABLE IF NOT EXISTS skill_embeddings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_id INTEGER NOT NULL,
    embedding BLOB NOT NULL,
    model TEXT DEFAULT 'default',
    dimensions INTEGER DEFAULT 384,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
);

-- Causal relationships (cause-effect tracking)
CREATE TABLE IF NOT EXISTS causal_edges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cause TEXT NOT NULL,
    effect TEXT NOT NULL,
    uplift REAL DEFAULT 0.0,
    confidence REAL DEFAULT 0.0,
    confounder_score REAL DEFAULT 0.0,
    observation_count INTEGER DEFAULT 0,
    namespace TEXT DEFAULT 'default',
    metadata_json TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Causal experiments (A/B testing)
CREATE TABLE IF NOT EXISTS causal_experiments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    hypothesis TEXT,
    cause TEXT NOT NULL,
    effect TEXT NOT NULL,
    treatment_group TEXT DEFAULT '{}',
    control_group TEXT DEFAULT '{}',
    status TEXT DEFAULT 'running' CHECK(status IN ('running', 'completed', 'cancelled')),
    result_json TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Causal observations
CREATE TABLE IF NOT EXISTS causal_observations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    experiment_id INTEGER NOT NULL,
    group_name TEXT NOT NULL CHECK(group_name IN ('treatment', 'control')),
    outcome REAL NOT NULL,
    metadata_json TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (experiment_id) REFERENCES causal_experiments(id) ON DELETE CASCADE
);

-- Reasoning patterns
CREATE TABLE IF NOT EXISTS reasoning_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_type TEXT NOT NULL,
    approach TEXT NOT NULL,
    context TEXT,
    outcome TEXT,
    success INTEGER DEFAULT 0,
    reward REAL DEFAULT 0.0,
    usage_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    namespace TEXT DEFAULT 'default',
    metadata_json TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reasoning pattern embeddings
CREATE TABLE IF NOT EXISTS pattern_embeddings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_id INTEGER NOT NULL,
    embedding BLOB NOT NULL,
    model TEXT DEFAULT 'default',
    dimensions INTEGER DEFAULT 384,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pattern_id) REFERENCES reasoning_patterns(id) ON DELETE CASCADE
);

-- Facts (subject-predicate-object triples)
CREATE TABLE IF NOT EXISTS facts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT NOT NULL,
    predicate TEXT NOT NULL,
    object TEXT NOT NULL,
    confidence REAL DEFAULT 1.0,
    ttl INTEGER DEFAULT NULL,
    namespace TEXT DEFAULT 'default',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Notes (free-form memory)
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    importance REAL DEFAULT 0.5,
    namespace TEXT DEFAULT 'default',
    metadata_json TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Note embeddings
CREATE TABLE IF NOT EXISTS note_embeddings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    note_id INTEGER NOT NULL,
    embedding BLOB NOT NULL,
    model TEXT DEFAULT 'default',
    dimensions INTEGER DEFAULT 384,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE
);

-- Events log (fine-grained agent activity)
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_name TEXT NOT NULL,
    event_type TEXT NOT NULL CHECK(event_type IN ('planning', 'execution', 'reflection', 'learning', 'communication')),
    content TEXT NOT NULL,
    phase TEXT,
    namespace TEXT DEFAULT 'default',
    metadata_json TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Memory quality scores
CREATE TABLE IF NOT EXISTS memory_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    memory_type TEXT NOT NULL,
    memory_id INTEGER NOT NULL,
    quality REAL DEFAULT 0.0,
    novelty REAL DEFAULT 0.0,
    relevance REAL DEFAULT 0.0,
    utility REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Memory access log
CREATE TABLE IF NOT EXISTS memory_access_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    memory_type TEXT NOT NULL,
    memory_id INTEGER NOT NULL,
    access_type TEXT NOT NULL CHECK(access_type IN ('read', 'write', 'search')),
    was_useful INTEGER DEFAULT 0,
    metadata_json TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_episodes_namespace ON episodes(namespace);
CREATE INDEX IF NOT EXISTS idx_episodes_success ON episodes(success);
CREATE INDEX IF NOT EXISTS idx_episodes_created_at ON episodes(created_at);
CREATE INDEX IF NOT EXISTS idx_skills_namespace ON skills(namespace);
CREATE INDEX IF NOT EXISTS idx_skills_success_rate ON skills(success_rate);
CREATE INDEX IF NOT EXISTS idx_causal_edges_cause ON causal_edges(cause);
CREATE INDEX IF NOT EXISTS idx_causal_edges_effect ON causal_edges(effect);
CREATE INDEX IF NOT EXISTS idx_causal_edges_namespace ON causal_edges(namespace);
CREATE INDEX IF NOT EXISTS idx_reasoning_patterns_task_type ON reasoning_patterns(task_type);
CREATE INDEX IF NOT EXISTS idx_reasoning_patterns_namespace ON reasoning_patterns(namespace);
CREATE INDEX IF NOT EXISTS idx_events_agent_name ON events(agent_name);
CREATE INDEX IF NOT EXISTS idx_events_event_type ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_facts_subject ON facts(subject);
CREATE INDEX IF NOT EXISTS idx_facts_predicate ON facts(predicate);
CREATE INDEX IF NOT EXISTS idx_memory_scores_type_id ON memory_scores(memory_type, memory_id);

-- Views
CREATE VIEW IF NOT EXISTS v_episode_stats AS
SELECT
    namespace,
    COUNT(*) as total_episodes,
    AVG(reward) as avg_reward,
    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful,
    SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failed
FROM episodes
GROUP BY namespace;

CREATE VIEW IF NOT EXISTS v_skill_stats AS
SELECT
    namespace,
    COUNT(*) as total_skills,
    AVG(success_rate) as avg_success_rate,
    SUM(usage_count) as total_usage
FROM skills
GROUP BY namespace;

CREATE VIEW IF NOT EXISTS v_causal_summary AS
SELECT
    namespace,
    COUNT(*) as total_edges,
    AVG(confidence) as avg_confidence,
    AVG(uplift) as avg_uplift
FROM causal_edges
GROUP BY namespace;
