"""
Database Connection Pool Manager
"""

import asyncpg
import logging
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)

# Global database pool
_db_pool: Optional[asyncpg.Pool] = None


async def get_db_pool() -> asyncpg.Pool:
    """Get or create database connection pool."""
    global _db_pool
    
    if _db_pool is None:
        try:
            # Ensure database URL is compatible with asyncpg
            # asyncpg requires postgresql:// or postgres://, not postgresql+asyncpg://
            db_url = settings.database_url
            if db_url and db_url.startswith("postgresql+asyncpg://"):
                db_url = db_url.replace("postgresql+asyncpg://", "postgresql://", 1)
            elif db_url and db_url.startswith("postgres+asyncpg://"):
                db_url = db_url.replace("postgres+asyncpg://", "postgres://", 1)
                
            _db_pool = await asyncpg.create_pool(
                db_url,
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            logger.info("✅ Database connection pool created")
        except Exception as e:
            logger.error(f"❌ Failed to create database pool: {e}")
            raise
    
    return _db_pool


async def close_db_pool():
    """Close database connection pool."""
    global _db_pool
    
    if _db_pool:
        await _db_pool.close()
        _db_pool = None
        logger.info("Database connection pool closed")
