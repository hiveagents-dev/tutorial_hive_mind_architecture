"""
SQLite storage layer for AgentDB.

Provides persistent storage using Python's built-in sqlite3 module.
Ported from the TypeScript AgentDB's UnifiedDatabase layer.
"""

import sqlite3
import json
import os
import logging
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
from contextlib import contextmanager

logger = logging.getLogger(__name__)

SCHEMA_PATH = Path(__file__).parent / "schema.sql"


class Storage:
    """
    SQLite storage backend for AgentDB.

    Handles all structured data persistence including episodes, skills,
    causal edges, reasoning patterns, facts, notes, and events.
    """

    def __init__(self, db_path: str = "agentdb.sqlite"):
        """
        Initialize storage.

        Args:
            db_path: Path to SQLite database file. Use ":memory:" for in-memory DB.
        """
        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None
        logger.info(f"Storage initialized with path: {db_path}")

    def initialize(self) -> None:
        """Create connection and initialize schema."""
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._init_schema()
        logger.info("Storage schema initialized")

    def _init_schema(self) -> None:
        """Load and execute the SQL schema."""
        schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
        self._conn.executescript(schema_sql)
        self._conn.commit()

    @property
    def connection(self) -> sqlite3.Connection:
        if self._conn is None:
            raise RuntimeError("Storage not initialized. Call initialize() first.")
        return self._conn

    @contextmanager
    def transaction(self):
        """Context manager for transactions with automatic rollback on error."""
        conn = self.connection
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    # ── Episode Operations ────────────────────────────────────────────

    def insert_episode(
        self,
        task: str,
        input_data: str = "",
        output: str = "",
        critique: str = "",
        reward: float = 0.0,
        success: bool = False,
        namespace: str = "default",
        metadata: Optional[Dict] = None,
    ) -> int:
        """Insert an episode and return its ID."""
        with self.transaction() as conn:
            cursor = conn.execute(
                """INSERT INTO episodes (task, input, output, critique, reward, success, namespace, metadata_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (task, input_data, output, critique, reward, int(success), namespace,
                 json.dumps(metadata or {})),
            )
            return cursor.lastrowid

    def get_episode(self, episode_id: int) -> Optional[Dict]:
        """Get episode by ID."""
        row = self.connection.execute(
            "SELECT * FROM episodes WHERE id = ?", (episode_id,)
        ).fetchone()
        return dict(row) if row else None

    def get_episodes(
        self,
        namespace: str = "default",
        limit: int = 100,
        success_only: bool = False,
    ) -> List[Dict]:
        """Get episodes with optional filtering."""
        query = "SELECT * FROM episodes WHERE namespace = ?"
        params: list = [namespace]
        if success_only:
            query += " AND success = 1"
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        rows = self.connection.execute(query, params).fetchall()
        return [dict(r) for r in rows]

    def update_episode(self, episode_id: int, **fields) -> bool:
        """Update episode fields."""
        allowed = {"task", "input", "output", "critique", "reward", "success", "metadata_json"}
        updates = {k: v for k, v in fields.items() if k in allowed}
        if not updates:
            return False
        if "success" in updates:
            updates["success"] = int(updates["success"])
        if "metadata_json" in updates and isinstance(updates["metadata_json"], dict):
            updates["metadata_json"] = json.dumps(updates["metadata_json"])
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values()) + [episode_id]
        with self.transaction() as conn:
            conn.execute(
                f"UPDATE episodes SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                values,
            )
        return True

    def delete_episode(self, episode_id: int) -> bool:
        """Delete episode by ID."""
        with self.transaction() as conn:
            cursor = conn.execute("DELETE FROM episodes WHERE id = ?", (episode_id,))
            return cursor.rowcount > 0

    # ── Skill Operations ──────────────────────────────────────────────

    def insert_skill(
        self,
        name: str,
        description: str = "",
        code: str = "",
        signature: str = "",
        success_rate: float = 0.0,
        namespace: str = "default",
        metadata: Optional[Dict] = None,
    ) -> int:
        """Insert a skill and return its ID."""
        with self.transaction() as conn:
            cursor = conn.execute(
                """INSERT INTO skills (name, description, code, signature, success_rate, namespace, metadata_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (name, description, code, signature, success_rate, namespace,
                 json.dumps(metadata or {})),
            )
            return cursor.lastrowid

    def get_skill(self, skill_id: int) -> Optional[Dict]:
        """Get skill by ID."""
        row = self.connection.execute(
            "SELECT * FROM skills WHERE id = ?", (skill_id,)
        ).fetchone()
        return dict(row) if row else None

    def get_skills(self, namespace: str = "default", limit: int = 100) -> List[Dict]:
        """Get skills for namespace."""
        rows = self.connection.execute(
            "SELECT * FROM skills WHERE namespace = ? ORDER BY success_rate DESC LIMIT ?",
            (namespace, limit),
        ).fetchall()
        return [dict(r) for r in rows]

    def update_skill_stats(
        self, skill_id: int, success: bool, increment_usage: bool = True
    ) -> None:
        """Update skill usage statistics."""
        skill = self.get_skill(skill_id)
        if not skill:
            return
        usage = skill["usage_count"] + (1 if increment_usage else 0)
        current_rate = skill["success_rate"]
        # Exponential moving average for success rate
        alpha = 0.1
        new_rate = alpha * (1.0 if success else 0.0) + (1 - alpha) * current_rate
        with self.transaction() as conn:
            conn.execute(
                "UPDATE skills SET usage_count = ?, success_rate = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (usage, new_rate, skill_id),
            )

    def insert_skill_link(
        self, source_id: int, target_id: int, link_type: str, weight: float = 1.0
    ) -> int:
        """Insert a link between two skills."""
        with self.transaction() as conn:
            cursor = conn.execute(
                "INSERT INTO skill_links (source_skill_id, target_skill_id, link_type, weight) VALUES (?, ?, ?, ?)",
                (source_id, target_id, link_type, weight),
            )
            return cursor.lastrowid

    # ── Causal Edge Operations ────────────────────────────────────────

    def insert_causal_edge(
        self,
        cause: str,
        effect: str,
        uplift: float = 0.0,
        confidence: float = 0.0,
        namespace: str = "default",
        metadata: Optional[Dict] = None,
    ) -> int:
        """Insert a causal edge."""
        with self.transaction() as conn:
            cursor = conn.execute(
                """INSERT INTO causal_edges (cause, effect, uplift, confidence, observation_count, namespace, metadata_json)
                   VALUES (?, ?, ?, ?, 1, ?, ?)""",
                (cause, effect, uplift, confidence, namespace, json.dumps(metadata or {})),
            )
            return cursor.lastrowid

    def get_causal_edges(
        self, cause: Optional[str] = None, effect: Optional[str] = None,
        namespace: str = "default",
    ) -> List[Dict]:
        """Query causal edges by cause and/or effect."""
        query = "SELECT * FROM causal_edges WHERE namespace = ?"
        params: list = [namespace]
        if cause:
            query += " AND cause = ?"
            params.append(cause)
        if effect:
            query += " AND effect = ?"
            params.append(effect)
        query += " ORDER BY confidence DESC"
        rows = self.connection.execute(query, params).fetchall()
        return [dict(r) for r in rows]

    def update_causal_edge(
        self, edge_id: int, uplift: float, confidence: float
    ) -> None:
        """Update causal edge metrics."""
        with self.transaction() as conn:
            conn.execute(
                """UPDATE causal_edges
                   SET uplift = ?, confidence = ?, observation_count = observation_count + 1,
                       updated_at = CURRENT_TIMESTAMP
                   WHERE id = ?""",
                (uplift, confidence, edge_id),
            )

    # ── Experiment Operations ─────────────────────────────────────────

    def create_experiment(
        self, name: str, hypothesis: str, cause: str, effect: str
    ) -> int:
        """Create a causal experiment."""
        with self.transaction() as conn:
            cursor = conn.execute(
                "INSERT INTO causal_experiments (name, hypothesis, cause, effect) VALUES (?, ?, ?, ?)",
                (name, hypothesis, cause, effect),
            )
            return cursor.lastrowid

    def record_observation(
        self, experiment_id: int, group_name: str, outcome: float,
        metadata: Optional[Dict] = None,
    ) -> int:
        """Record an experiment observation."""
        with self.transaction() as conn:
            cursor = conn.execute(
                "INSERT INTO causal_observations (experiment_id, group_name, outcome, metadata_json) VALUES (?, ?, ?, ?)",
                (experiment_id, group_name, outcome, json.dumps(metadata or {})),
            )
            return cursor.lastrowid

    def complete_experiment(self, experiment_id: int, result: Dict) -> None:
        """Mark experiment as completed with results."""
        with self.transaction() as conn:
            conn.execute(
                "UPDATE causal_experiments SET status = 'completed', result_json = ?, completed_at = CURRENT_TIMESTAMP WHERE id = ?",
                (json.dumps(result), experiment_id),
            )

    # ── Reasoning Pattern Operations ──────────────────────────────────

    def insert_pattern(
        self,
        task_type: str,
        approach: str,
        context: str = "",
        outcome: str = "",
        success: bool = False,
        reward: float = 0.0,
        namespace: str = "default",
        metadata: Optional[Dict] = None,
    ) -> int:
        """Insert a reasoning pattern."""
        with self.transaction() as conn:
            cursor = conn.execute(
                """INSERT INTO reasoning_patterns
                   (task_type, approach, context, outcome, success, reward, namespace, metadata_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (task_type, approach, context, outcome, int(success), reward, namespace,
                 json.dumps(metadata or {})),
            )
            return cursor.lastrowid

    def get_pattern(self, pattern_id: int) -> Optional[Dict]:
        """Get pattern by ID."""
        row = self.connection.execute(
            "SELECT * FROM reasoning_patterns WHERE id = ?", (pattern_id,)
        ).fetchone()
        return dict(row) if row else None

    def get_patterns(
        self, task_type: Optional[str] = None, namespace: str = "default", limit: int = 50
    ) -> List[Dict]:
        """Get reasoning patterns."""
        query = "SELECT * FROM reasoning_patterns WHERE namespace = ?"
        params: list = [namespace]
        if task_type:
            query += " AND task_type = ?"
            params.append(task_type)
        query += " ORDER BY success_count DESC, reward DESC LIMIT ?"
        params.append(limit)
        rows = self.connection.execute(query, params).fetchall()
        return [dict(r) for r in rows]

    def update_pattern_stats(
        self, pattern_id: int, success: bool, reward: float = 0.0
    ) -> None:
        """Update pattern statistics after usage."""
        with self.transaction() as conn:
            conn.execute(
                """UPDATE reasoning_patterns
                   SET usage_count = usage_count + 1,
                       success_count = success_count + CASE WHEN ? THEN 1 ELSE 0 END,
                       reward = (reward * usage_count + ?) / (usage_count + 1),
                       updated_at = CURRENT_TIMESTAMP
                   WHERE id = ?""",
                (int(success), reward, pattern_id),
            )

    # ── Fact Operations ───────────────────────────────────────────────

    def insert_fact(
        self, subject: str, predicate: str, obj: str,
        confidence: float = 1.0, namespace: str = "default",
    ) -> int:
        """Insert a fact triple."""
        with self.transaction() as conn:
            cursor = conn.execute(
                "INSERT INTO facts (subject, predicate, object, confidence, namespace) VALUES (?, ?, ?, ?, ?)",
                (subject, predicate, obj, confidence, namespace),
            )
            return cursor.lastrowid

    def query_facts(
        self, subject: Optional[str] = None, predicate: Optional[str] = None,
        obj: Optional[str] = None, namespace: str = "default",
    ) -> List[Dict]:
        """Query facts by subject/predicate/object."""
        query = "SELECT * FROM facts WHERE namespace = ?"
        params: list = [namespace]
        if subject:
            query += " AND subject = ?"
            params.append(subject)
        if predicate:
            query += " AND predicate = ?"
            params.append(predicate)
        if obj:
            query += " AND object = ?"
            params.append(obj)
        rows = self.connection.execute(query, params).fetchall()
        return [dict(r) for r in rows]

    # ── Note Operations ───────────────────────────────────────────────

    def insert_note(
        self, content: str, importance: float = 0.5,
        namespace: str = "default", metadata: Optional[Dict] = None,
    ) -> int:
        """Insert a free-form note."""
        with self.transaction() as conn:
            cursor = conn.execute(
                "INSERT INTO notes (content, importance, namespace, metadata_json) VALUES (?, ?, ?, ?)",
                (content, importance, namespace, json.dumps(metadata or {})),
            )
            return cursor.lastrowid

    # ── Event Operations ──────────────────────────────────────────────

    def log_event(
        self, agent_name: str, event_type: str, content: str,
        phase: str = "", namespace: str = "default",
        metadata: Optional[Dict] = None,
    ) -> int:
        """Log an agent event."""
        with self.transaction() as conn:
            cursor = conn.execute(
                "INSERT INTO events (agent_name, event_type, content, phase, namespace, metadata_json) VALUES (?, ?, ?, ?, ?, ?)",
                (agent_name, event_type, content, phase, namespace,
                 json.dumps(metadata or {})),
            )
            return cursor.lastrowid

    def get_events(
        self, agent_name: Optional[str] = None, event_type: Optional[str] = None,
        namespace: str = "default", limit: int = 100,
    ) -> List[Dict]:
        """Get events with filtering."""
        query = "SELECT * FROM events WHERE namespace = ?"
        params: list = [namespace]
        if agent_name:
            query += " AND agent_name = ?"
            params.append(agent_name)
        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        rows = self.connection.execute(query, params).fetchall()
        return [dict(r) for r in rows]

    # ── Embedding Operations ──────────────────────────────────────────

    def store_embedding(
        self, table: str, ref_id: int, embedding_bytes: bytes,
        model: str = "default", dimensions: int = 384,
    ) -> int:
        """Store a vector embedding for a record.

        Args:
            table: One of 'episode_embeddings', 'skill_embeddings',
                   'pattern_embeddings', 'note_embeddings'.
            ref_id: ID of the referenced record.
            embedding_bytes: Serialized float array as bytes.
            model: Embedding model name.
            dimensions: Vector dimensions.
        """
        ref_col_map = {
            "episode_embeddings": "episode_id",
            "skill_embeddings": "skill_id",
            "pattern_embeddings": "pattern_id",
            "note_embeddings": "note_id",
        }
        ref_col = ref_col_map.get(table)
        if not ref_col:
            raise ValueError(f"Invalid embedding table: {table}")
        with self.transaction() as conn:
            cursor = conn.execute(
                f"INSERT INTO {table} ({ref_col}, embedding, model, dimensions) VALUES (?, ?, ?, ?)",
                (ref_id, embedding_bytes, model, dimensions),
            )
            return cursor.lastrowid

    def get_all_embeddings(self, table: str) -> List[Tuple[int, int, bytes]]:
        """Get all embeddings from a table. Returns (id, ref_id, embedding_bytes)."""
        ref_col_map = {
            "episode_embeddings": "episode_id",
            "skill_embeddings": "skill_id",
            "pattern_embeddings": "pattern_id",
            "note_embeddings": "note_id",
        }
        ref_col = ref_col_map.get(table)
        if not ref_col:
            raise ValueError(f"Invalid embedding table: {table}")
        rows = self.connection.execute(
            f"SELECT id, {ref_col}, embedding FROM {table}"
        ).fetchall()
        return [(r[0], r[1], r[2]) for r in rows]

    # ── Memory Scoring ────────────────────────────────────────────────

    def score_memory(
        self, memory_type: str, memory_id: int,
        quality: float = 0.0, novelty: float = 0.0,
        relevance: float = 0.0, utility: float = 0.0,
    ) -> int:
        """Score a memory entry for quality tracking."""
        with self.transaction() as conn:
            cursor = conn.execute(
                "INSERT INTO memory_scores (memory_type, memory_id, quality, novelty, relevance, utility) VALUES (?, ?, ?, ?, ?, ?)",
                (memory_type, memory_id, quality, novelty, relevance, utility),
            )
            return cursor.lastrowid

    def log_memory_access(
        self, memory_type: str, memory_id: int,
        access_type: str = "read", was_useful: bool = False,
        metadata: Optional[Dict] = None,
    ) -> None:
        """Log memory access for usage tracking."""
        with self.transaction() as conn:
            conn.execute(
                "INSERT INTO memory_access_log (memory_type, memory_id, access_type, was_useful, metadata_json) VALUES (?, ?, ?, ?, ?)",
                (memory_type, memory_id, access_type, int(was_useful),
                 json.dumps(metadata or {})),
            )

    # ── Statistics ────────────────────────────────────────────────────

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        conn = self.connection
        stats = {}
        for table in [
            "episodes", "skills", "causal_edges", "reasoning_patterns",
            "facts", "notes", "events",
        ]:
            row = conn.execute(f"SELECT COUNT(*) as cnt FROM {table}").fetchone()
            stats[table] = row[0] if row else 0

        # Views
        episode_stats = conn.execute("SELECT * FROM v_episode_stats").fetchall()
        stats["episode_stats_by_namespace"] = [dict(r) for r in episode_stats]

        skill_stats = conn.execute("SELECT * FROM v_skill_stats").fetchall()
        stats["skill_stats_by_namespace"] = [dict(r) for r in skill_stats]

        causal_stats = conn.execute("SELECT * FROM v_causal_summary").fetchall()
        stats["causal_stats_by_namespace"] = [dict(r) for r in causal_stats]

        return stats

    def optimize(self) -> None:
        """Run ANALYZE and VACUUM for performance."""
        conn = self.connection
        conn.execute("ANALYZE")
        conn.execute("VACUUM")
        logger.info("Database optimized (ANALYZE + VACUUM)")

    def close(self) -> None:
        """Close the database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None
            logger.info("Storage connection closed")
