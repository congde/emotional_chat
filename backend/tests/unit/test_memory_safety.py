"""Regression tests for memory tenant isolation and vector ownership."""

import sys
import types

# The safety tests exercise logic with a fake collection and do not require the
# optional Chroma runtime to be installed in the test environment.
if "chromadb" not in sys.modules:
    chromadb = types.ModuleType("chromadb")
    chromadb_config = types.ModuleType("chromadb.config")
    chromadb_utils = types.ModuleType("chromadb.utils")
    chromadb_embeddings = types.ModuleType("chromadb.utils.embedding_functions")
    chromadb_config.Settings = object
    chromadb_embeddings.DefaultEmbeddingFunction = object
    chromadb_utils.embedding_functions = chromadb_embeddings
    chromadb.utils = chromadb_utils
    sys.modules["chromadb"] = chromadb
    sys.modules["chromadb.config"] = chromadb_config
    sys.modules["chromadb.utils"] = chromadb_utils
    sys.modules["chromadb.utils.embedding_functions"] = chromadb_embeddings

from backend.agent.memory_hub import get_memory_hub, reset_memory_hub
from backend.memory_manager import MemoryManager


class FakeCollection:
    def __init__(self):
        self.rows = {
            "alice-memory": {"user_id": "alice", "importance": 0.4},
        }
        self.deleted = []
        self.updated = []

    def get(self, ids, include=None):
        found_ids = [memory_id for memory_id in ids if memory_id in self.rows]
        return {
            "ids": found_ids,
            "metadatas": [self.rows[memory_id].copy() for memory_id in found_ids],
        }

    def delete(self, ids):
        self.deleted.extend(ids)
        for memory_id in ids:
            self.rows.pop(memory_id, None)

    def update(self, ids, metadatas):
        self.updated.extend(zip(ids, metadatas))
        for memory_id, metadata in zip(ids, metadatas):
            self.rows[memory_id] = metadata.copy()


def make_manager(collection):
    manager = MemoryManager.__new__(MemoryManager)
    manager.memory_collection = collection
    return manager


def test_memory_hub_is_isolated_by_user_and_session():
    reset_memory_hub()

    alice_first = get_memory_hub("alice", "session-1")
    alice_again = get_memory_hub("alice", "session-1")
    alice_other_session = get_memory_hub("alice", "session-2")
    bob = get_memory_hub("bob", "session-1")

    assert alice_first is alice_again
    assert alice_first is not alice_other_session
    assert alice_first is not bob
    assert alice_first.user_store.store_id == "user_alice"
    assert bob.user_store.store_id == "user_bob"


def test_reset_memory_hub_can_target_one_user():
    reset_memory_hub()
    alice = get_memory_hub("alice", "session-1")
    bob = get_memory_hub("bob", "session-1")

    reset_memory_hub(user_id="alice")

    assert get_memory_hub("alice", "session-1") is not alice
    assert get_memory_hub("bob", "session-1") is bob


def test_vector_delete_rejects_wrong_owner():
    collection = FakeCollection()
    manager = make_manager(collection)

    assert manager.delete_memory("bob", "alice-memory") is False
    assert collection.deleted == []
    assert "alice-memory" in collection.rows


def test_vector_delete_allows_owner():
    collection = FakeCollection()
    manager = make_manager(collection)

    assert manager.delete_memory("alice", "alice-memory") is True
    assert collection.deleted == ["alice-memory"]


def test_importance_update_changes_vector_metadata():
    collection = FakeCollection()
    manager = make_manager(collection)

    assert manager.update_memory_importance("alice-memory", 0.9) is True
    assert collection.rows["alice-memory"]["importance"] == 0.9
    assert collection.rows["alice-memory"]["user_id"] == "alice"
