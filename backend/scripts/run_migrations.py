"""
Database Migration Runner for Railway Deployment

Runs all SQL migrations in order against the Railway PostgreSQL database.
"""

import asyncio
import asyncpg
import os
from pathlib import Path
import sys
import re


async def run_migrations():
    """Run all SQL migrations in order."""

    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable not set")
        print("Run this script via Railway CLI: railway run python backend/scripts/run_migrations.py")
        sys.exit(1)

    print(f"🔌 Connecting to database...")

    try:
        conn = await asyncpg.connect(database_url)
        print("✅ Connected to database")
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        sys.exit(1)

    # Find all migration files
    migrations_dir = Path(__file__).parent.parent.parent / "database" / "migrations"

    if not migrations_dir.exists():
        print(f"❌ Migrations directory not found: {migrations_dir}")
        sys.exit(1)

    migration_files = sorted(migrations_dir.glob("*.sql"), key=lambda p: p.name)

    # Guard against duplicate numeric prefixes such as 014_*.sql appearing multiple times.
    # This keeps migration ordering deterministic and avoids accidental schema divergence.
    prefix_map: dict[str, list[str]] = {}
    for migration_file in migration_files:
        match = re.match(r"^(\d+)_", migration_file.name)
        if not match:
            continue
        prefix = match.group(1)
        prefix_map.setdefault(prefix, []).append(migration_file.name)

    duplicate_prefixes = {
        prefix: names for prefix, names in prefix_map.items() if len(names) > 1
    }
    if duplicate_prefixes:
        print("❌ Duplicate migration numeric prefixes detected:")
        for prefix, names in sorted(duplicate_prefixes.items()):
            print(f"   {prefix}: {', '.join(sorted(names))}")
        print("Resolve duplicates before running migrations.")
        await conn.close()
        sys.exit(1)

    if not migration_files:
        print(f"⚠️  No migration files found in {migrations_dir}")
        await conn.close()
        return

    print(f"\n📋 Found {len(migration_files)} migration(s) to run:\n")

    # Run each migration
    for i, migration_file in enumerate(migration_files, 1):
        print(f"[{i}/{len(migration_files)}] Running {migration_file.name}...")

        try:
            sql = migration_file.read_text()
            await conn.execute(sql)
            print(f"    ✅ {migration_file.name} completed successfully\n")
        except Exception as e:
            print(f"    ❌ Failed to run {migration_file.name}: {e}\n")
            print("Continuing to next migration...\n")

    await conn.close()
    print("✅ All migrations completed!")
    print("\n🎉 Database is ready for production!")


if __name__ == "__main__":
    print("=" * 60)
    print("  Railway Database Migration Runner")
    print("=" * 60)
    print()

    asyncio.run(run_migrations())
