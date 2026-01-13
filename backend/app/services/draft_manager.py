"""
Draft Manager Service

Manages draft work operations including CRUD and cleanup.
Coordinates with Supabase client and conflict resolver for safe operations.
"""

from typing import Optional, List, Dict, Any
import logging
from datetime import datetime, timedelta

from app.models.draft import (
    Draft,
    DraftCreate,
    DraftUpdate,
    DraftSaveRequest,
)
from app.services.supabase_client import supabase_service
from app.services.conflict_resolver import ConflictResolver
from app.core.errors import AutoBidderError, ConflictError
from app.config import settings

logger = logging.getLogger(__name__)


class DraftManager:
    """
    Manages draft operations for users.
    
    Provides methods to list, get, save, delete drafts with
    proper validation, conflict detection, and error handling.
    """
    
    def __init__(self) -> None:
        """Initialize draft manager."""
        self.supabase = supabase_service
        self.conflict_resolver = ConflictResolver()
    
    async def list_drafts(self, user_id: str) -> List[Draft]:
        """
        List all active drafts for user.
        
        Args:
            user_id: User's UUID
            
        Returns:
            List of Draft objects
        """
        try:
            drafts_data = await self.supabase.list_user_drafts(user_id)
            return [Draft(**draft) for draft in drafts_data]
        except Exception as e:
            logger.error(f"Error listing drafts for user {user_id}: {e}")
            raise AutoBidderError(f"Failed to list drafts: {e}")
    
    async def get_draft(
        self,
        user_id: str,
        entity_type: str,
        entity_id: Optional[str],
    ) -> Optional[Draft]:
        """
        Get specific draft.
        
        Args:
            user_id: User's UUID
            entity_type: Type of entity
            entity_id: Entity ID (None for new entities)
            
        Returns:
            Draft object or None if not found
        """
        try:
            draft_data = await self.supabase.get_draft(user_id, entity_type, entity_id)
            
            if not draft_data:
                return None
            
            return Draft(**draft_data)
        except Exception as e:
            logger.error(f"Error getting draft: {e}")
            raise AutoBidderError(f"Failed to get draft: {e}")
    
    async def save_draft(
        self,
        user_id: str,
        entity_type: str,
        entity_id: Optional[str],
        draft_request: DraftSaveRequest,
    ) -> Draft:
        """
        Save draft with conflict detection.
        
        Args:
            user_id: User's UUID
            entity_type: Type of entity
            entity_id: Entity ID (None for new entities)
            draft_request: Draft save request with data and version
            
        Returns:
            Saved Draft object
            
        Raises:
            AutoBidderError: If save fails or conflict detected
        """
        try:
            # Check for existing draft
            existing = await self.get_draft(user_id, entity_type, entity_id)
            
            # Detect version conflict
            if existing:
                has_conflict = self.conflict_resolver.detect_conflict(
                    client_version=draft_request.version,
                    server_version=existing.version,
                )
                
                if has_conflict:
                    conflict_info = {
                        "server_version": existing.version,
                        "client_version": draft_request.version,
                        "server_updated_at": existing.updated_at,
                    }
                    raise ConflictError(
                        "Version conflict detected",
                        details=conflict_info,
                    )
            
            # Increment version
            new_version = (existing.version + 1) if existing else 1
            
            # Prepare draft data
            draft_data: Dict[str, Any] = {
                "user_id": user_id,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "draft_data": draft_request.draft_data,
                "version": new_version,
                "last_saved_at": datetime.now().isoformat(),
            }
            
            # Save to database
            result = await self.supabase.upsert_draft(draft_data)
            
            return Draft(**result)
        except AutoBidderError:
            raise
        except Exception as e:
            logger.error(f"Error saving draft: {e}")
            raise AutoBidderError(f"Failed to save draft: {e}")
    
    async def delete_draft(
        self,
        user_id: str,
        entity_type: str,
        entity_id: Optional[str],
    ) -> None:
        """
        Delete draft.
        
        Args:
            user_id: User's UUID
            entity_type: Type of entity
            entity_id: Entity ID (None for new entities)
        """
        try:
            await self.supabase.delete_draft(user_id, entity_type, entity_id)
            logger.info(f"Deleted draft for {entity_type}:{entity_id}")
        except Exception as e:
            logger.error(f"Error deleting draft: {e}")
            # Don't raise - deletion is non-critical
    
    async def cleanup_expired(self, retention_hours: Optional[int] = None) -> int:
        """
        Clean up expired drafts older than retention period.
        
        Args:
            retention_hours: Retention period in hours (uses config if not provided)
            
        Returns:
            Number of drafts cleaned up
        """
        try:
            if retention_hours is None:
                retention_hours = settings.draft_retention_hours
            
            # Calculate cutoff time
            cutoff_time = datetime.now() - timedelta(hours=retention_hours)
            
            logger.info(f"Starting draft cleanup (retention: {retention_hours}h, cutoff: {cutoff_time})")
            
            # TODO: Implement cleanup query via Supabase
            # This would require a custom SQL query or RPC function
            # For now, log that cleanup would happen here
            logger.info("Draft cleanup triggered - implementation pending")
            
            return 0
        except Exception as e:
            logger.error(f"Error cleaning up expired drafts: {e}")
            return 0


# Global instance
draft_manager = DraftManager()
