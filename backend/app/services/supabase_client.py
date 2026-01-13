"""
Supabase Client Service

Provides read-only access to Supabase database for the Python backend.
Used to fetch strategies, user profiles, and other reference data.
"""

from typing import Any, Dict, List, Optional
import logging
from supabase import create_client, Client

from app.config import settings
from app.core.errors import AutoBidderError

logger = logging.getLogger(__name__)


class SupabaseService:
    """Service for interacting with Supabase database."""

    def __init__(self) -> None:
        """Initialize Supabase client with service role key."""
        try:
            self.client: Client = create_client(
                settings.supabase_url,
                settings.supabase_service_key,
            )
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise AutoBidderError(f"Supabase initialization failed: {e}")

    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user profile by user_id.

        Args:
            user_id: User's UUID

        Returns:
            User profile dict or None if not found

        Raises:
            AutoBidderError: If query fails
        """
        try:
            response = (
                self.client.table("user_profiles")
                .select("*")
                .eq("user_id", user_id)
                .execute()
            )

            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Failed to fetch user profile: {e}")
            raise AutoBidderError(f"Failed to fetch user profile: {e}")

    async def get_strategy(self, strategy_id: str) -> Optional[Dict[str, Any]]:
        """
        Get bidding strategy by ID.

        Args:
            strategy_id: Strategy UUID

        Returns:
            Strategy dict or None if not found
        """
        try:
            response = (
                self.client.table("bidding_strategies")
                .select("*")
                .eq("id", strategy_id)
                .execute()
            )

            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Failed to fetch strategy: {e}")
            raise AutoBidderError(f"Failed to fetch strategy: {e}")

    async def get_default_strategy(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user's default bidding strategy.

        Args:
            user_id: User's UUID

        Returns:
            Default strategy dict or None if not found
        """
        try:
            response = (
                self.client.table("bidding_strategies")
                .select("*")
                .eq("user_id", user_id)
                .eq("is_default", True)
                .execute()
            )

            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Failed to fetch default strategy: {e}")
            raise AutoBidderError(f"Failed to fetch default strategy: {e}")

    async def get_active_keywords(self, user_id: str) -> List[str]:
        """
        Get user's active keywords.

        Args:
            user_id: User's UUID

        Returns:
            List of keyword strings
        """
        try:
            response = (
                self.client.table("keywords")
                .select("keyword")
                .eq("user_id", user_id)
                .eq("is_active", True)
                .execute()
            )

            return [item["keyword"] for item in response.data]
        except Exception as e:
            logger.error(f"Failed to fetch keywords: {e}")
            return []

    async def update_document_status(
        self,
        document_id: str,
        status: str,
        error_message: Optional[str] = None,
        chunk_count: int = 0,
        token_count: int = 0,
    ) -> None:
        """
        Update knowledge base document processing status.

        Args:
            document_id: Document UUID
            status: Processing status
            error_message: Error message if failed
            chunk_count: Number of chunks created
            token_count: Total tokens in chunks
        """
        try:
            update_data: Dict[str, Any] = {
                "processing_status": status,
                "chunk_count": chunk_count,
                "token_count": token_count,
            }

            if error_message:
                update_data["processing_error"] = error_message

            if status == "completed":
                update_data["processed_at"] = "now()"

            self.client.table("knowledge_base_documents").update(update_data).eq(
                "id", document_id
            ).execute()

            logger.info(f"Updated document {document_id} status to {status}")
        except Exception as e:
            logger.error(f"Failed to update document status: {e}")
            # Don't raise - this is a non-critical operation

    # Workflow Optimization Operations
    
    async def get_session_state(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user's session state.
        
        Args:
            user_id: User's UUID
            
        Returns:
            Session state dict or None if not found
        """
        try:
            response = (
                self.client.table("user_session_states")
                .select("*")
                .eq("user_id", user_id)
                .execute()
            )
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Failed to fetch session state: {e}")
            return None
    
    async def upsert_session_state(
        self, user_id: str, session_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create or update user's session state.
        
        Args:
            user_id: User's UUID
            session_data: Session state data to upsert
            
        Returns:
            Updated session state dict
            
        Raises:
            AutoBidderError: If operation fails
        """
        try:
            # Add user_id to data if not present
            session_data["user_id"] = user_id
            
            response = (
                self.client.table("user_session_states")
                .upsert(session_data, on_conflict="user_id")
                .execute()
            )
            
            return response.data[0] if response.data else {}
        except Exception as e:
            logger.error(f"Failed to upsert session state: {e}")
            raise AutoBidderError(f"Failed to update session state: {e}")
    
    async def delete_session_state(self, user_id: str) -> None:
        """
        Delete user's session state.
        
        Args:
            user_id: User's UUID
        """
        try:
            self.client.table("user_session_states").delete().eq(
                "user_id", user_id
            ).execute()
            logger.info(f"Deleted session state for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to delete session state: {e}")
            # Don't raise - non-critical operation
    
    async def get_draft(
        self, user_id: str, entity_type: str, entity_id: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Get draft for specific entity.
        
        Args:
            user_id: User's UUID
            entity_type: Type of entity (proposal, project, etc.)
            entity_id: Entity ID (None for new entities)
            
        Returns:
            Draft dict or None if not found
        """
        try:
            query = (
                self.client.table("draft_work")
                .select("*")
                .eq("user_id", user_id)
                .eq("entity_type", entity_type)
            )
            
            if entity_id:
                query = query.eq("entity_id", entity_id)
            else:
                query = query.is_("entity_id", "null")
            
            response = query.execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Failed to fetch draft: {e}")
            return None
    
    async def list_user_drafts(self, user_id: str) -> List[Dict[str, Any]]:
        """
        List all active drafts for user.
        
        Args:
            user_id: User's UUID
            
        Returns:
            List of draft dicts
        """
        try:
            response = (
                self.client.table("draft_work")
                .select("*")
                .eq("user_id", user_id)
                .execute()
            )
            
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Failed to list drafts: {e}")
            return []
    
    async def upsert_draft(self, draft_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create or update a draft.
        
        Args:
            draft_data: Draft data including user_id, entity_type, entity_id, draft_data
            
        Returns:
            Updated draft dict
            
        Raises:
            AutoBidderError: If operation fails
        """
        try:
            response = (
                self.client.table("draft_work")
                .upsert(draft_data)
                .execute()
            )
            
            return response.data[0] if response.data else {}
        except Exception as e:
            logger.error(f"Failed to upsert draft: {e}")
            raise AutoBidderError(f"Failed to save draft: {e}")
    
    async def delete_draft(
        self, user_id: str, entity_type: str, entity_id: Optional[str]
    ) -> None:
        """
        Delete a draft.
        
        Args:
            user_id: User's UUID
            entity_type: Type of entity
            entity_id: Entity ID (None for new entities)
        """
        try:
            query = (
                self.client.table("draft_work")
                .delete()
                .eq("user_id", user_id)
                .eq("entity_type", entity_type)
            )
            
            if entity_id:
                query = query.eq("entity_id", entity_id)
            else:
                query = query.is_("entity_id", "null")
            
            query.execute()
            logger.info(f"Deleted draft for {entity_type}:{entity_id}")
        except Exception as e:
            logger.error(f"Failed to delete draft: {e}")
            # Don't raise - non-critical operation
    
    async def insert_analytics_event(self, event_data: Dict[str, Any]) -> None:
        """
        Insert workflow analytics event.
        
        Args:
            event_data: Analytics event data
        """
        try:
            self.client.table("workflow_analytics").insert(event_data).execute()
        except Exception as e:
            logger.error(f"Failed to insert analytics event: {e}")
            # Don't raise - analytics is non-critical


# Global instance
supabase_service = SupabaseService()
