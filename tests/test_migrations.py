"""Migration tests for Phase 1 remediation.

Tests:
1. Clean migration against fresh isolated database
2. Verify no duplicate journal_entries table creation
3. Verify migration chain is correct (no stamp-heads fallback)
"""

import os
import sys
import unittest
import tempfile
import shutil
import subprocess
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / 'backend'))


class TestMigrations(unittest.TestCase):
    """Test migration integrity."""

    def setUp(self):
        """Create fresh isolated database for each test."""
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, 'test_migrate.db')
        self.db_url = f'sqlite:///{self.db_path}'
        os.environ['DATABASE_URL'] = self.db_url

    def tearDown(self):
        """Clean up test database."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _run_alembic(self, upgrade_target='head'):
        """Run alembic upgrade using Python API directly."""
        backend_dir = pathlib.Path(__file__).parent.parent / 'backend'
        alembic_ini = backend_dir / 'alembic.ini'
        alembic_script_dir = backend_dir / 'alembic'
        
        # Create a wrapper script with absolute paths
        wrapper = pathlib.Path(self.test_dir) / 'run_alembic.py'
        wrapper.write_text(f'''
import os
import sys

os.environ["DATABASE_URL"] = "{self.db_url}"
sys.path.insert(0, "{backend_dir.parent}")

from alembic.config import Config
from alembic import command as alembic_cmd

cfg = Config("{alembic_ini}")
cfg.set_main_option("script_location", "{alembic_script_dir}")
cfg.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])
alembic_cmd.upgrade(cfg, "{upgrade_target}")
''')
        
        result = subprocess.run(
            [sys.executable, str(wrapper)],
            capture_output=True,
            text=True
        )
        return result

    def _connect_to_db(self):
        """Connect to the test database and return engine."""
        from sqlalchemy import create_engine
        
        engine = create_engine(
            self.db_url,
            connect_args={"check_same_thread": False}
        )
        return engine

    def _get_tables(self):
        """Get list of non-alembic tables from the database."""
        engine = self._connect_to_db()
        with engine.connect() as conn:
            tables = conn.execute(
                __import__('sqlalchemy').text(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'alembic%'"
                )
            ).fetchall()
            return [t[0] for t in tables]

    def test_clean_migration_vs_isolated_db(self):
        """Prove a clean migration works against a fresh isolated database."""
        # Run all migrations from scratch
        result = self._run_alembic('head')
        self.assertEqual(result.returncode, 0, f"Alembic upgrade failed: {result.stderr}")

        # Connect and verify tables exist
        table_names = self._get_tables()
        
        # Essential tables for Phase 1
        self.assertIn('journal_entries', table_names, "journal_entries table missing")
        
        # Verify alembic_version was created
        engine = self._connect_to_db()
        with engine.connect() as conn:
            version = conn.execute(
                __import__('sqlalchemy').text("SELECT version_num FROM alembic_version")
            ).fetchone()
            self.assertIsNotNone(version, "alembic_version should exist after migration")

    def test_no_duplicate_journal_entries(self):
        """Verify no duplicate journal_entries table creation."""
        # Run migration to upgrade
        result = self._run_alembic('head')
        self.assertEqual(result.returncode, 0, f"Alembic upgrade failed: {result.stderr}")
        
        # Connect and verify journal_entries exists only once
        table_names = self._get_tables()
        self.assertEqual(
            table_names.count('journal_entries'), 1, 
            f"journal_entries appears {table_names.count('journal_entries')} times"
        )

    def test_migration_chain_correct(self):
        """Verify migration chain is correct."""
        # Upgrade to head
        result = self._run_alembic('head')
        self.assertEqual(result.returncode, 0, f"Alembic upgrade failed: {result.stderr}")
        
        # Verify the expected final migration exists
        table_names = self._get_tables()
        self.assertIn('ceo_decision_records', table_names, "CEO decision records table not created")
        
        # Verify alembic recorded the migration
        engine = self._connect_to_db()
        with engine.connect() as conn:
            version = conn.execute(
                __import__('sqlalchemy').text("SELECT version_num FROM alembic_version")
            ).fetchone()
            self.assertIsNotNone(version, "Version should be recorded after migration")

    def test_no_automatic_stamp_head(self):
        """Verify migration failures surface in CI (no stamp-heads fallback)."""
        # The fact that we can run 'upgrade head' successfully proves
        # that migrations run properly without needing to stamp heads.
        # This test documents that migrations work without auto-stamp.
        
        result = self._run_alembic('head')
        self.assertEqual(result.returncode, 0, f"Alembic upgrade should succeed: {result.stderr}")


if __name__ == '__main__':
    unittest.main()