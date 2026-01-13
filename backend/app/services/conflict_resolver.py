"""
Conflict Resolver Service

Implements conflict detection and resolution logic for draft work.
Uses last-write-wins strategy with version checking.
"""

from typing import Dict, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ConflictResolver:
    """
    Resolves conflicts in draft work using version-based conflict detection.
    
    Implements last-write-wins strategy with warnings to user.
    """
    
    def detect_conflict(
        self,
        client_version: int,
        server_version: int,
    ) -> bool:
        """
        Detect if there's a version conflict.
        
        Args:
            client_version: Version number from client
            server_version: Current version on server
            
        Returns:
            True if conflict detected, False otherwise
        """
        # Conflict exists if client version doesn't match server version
        # This means someone else has modified the draft since client loaded it
        has_conflict = client_version != server_version
        
        if has_conflict:
            logger.warning(
                f"Version conflict detected: client={client_version}, server={server_version}"
            )
        
        return has_conflict
    
    def resolve_last_write_wins(
        self,
        client_data: Dict[str, Any],
        server_data: Dict[str, Any],
        resolution: str = "client",
    ) -> Dict[str, Any]:
        """
        Resolve conflict using last-write-wins strategy.
        
        Args:
            client_data: Data from client
            server_data: Data from server
            resolution: Which version to keep ("client" or "server")
            
        Returns:
            Resolved data
        """
        if resolution == "client":
            logger.info("Conflict resolved: using client data (last write wins)")
            return client_data
        elif resolution == "server":
            logger.info("Conflict resolved: using server data (discarding client changes)")
            return server_data
        else:
            # Default to server data for safety
            logger.warning(f"Unknown resolution strategy '{resolution}', defaulting to server data")
            return server_data
    
    def merge_data(
        self,
        client_data: Dict[str, Any],
        server_data: Dict[str, Any],
        merge_strategy: str = "prefer_client",
    ) -> Dict[str, Any]:
        """
        Attempt to merge client and server data.
        
        Note: This is a simple field-level merge. More sophisticated merging
        would require knowledge of the data structure and business logic.
        
        Args:
            client_data: Data from client
            server_data: Data from server
            merge_strategy: How to handle conflicts ("prefer_client" or "prefer_server")
            
        Returns:
            Merged data
        """
        merged = server_data.copy()
        
        # Merge fields from client
        for key, client_value in client_data.items():
            if key not in merged:
                # New field from client
                merged[key] = client_value
            elif merged[key] == client_value:
                # No conflict - values match
                continue
            else:
                # Conflict - use merge strategy
                if merge_strategy == "prefer_client":
                    merged[key] = client_value
                    logger.debug(f"Merge conflict on field '{key}': using client value")
                else:
                    # Keep server value
                    logger.debug(f"Merge conflict on field '{key}': keeping server value")
        
        return merged
    
    def can_auto_resolve(
        self,
        client_data: Dict[str, Any],
        server_data: Dict[str, Any],
    ) -> bool:
        """
        Determine if conflict can be auto-resolved without user input.
        
        Args:
            client_data: Data from client
            server_data: Data from server
            
        Returns:
            True if can auto-resolve, False if user input needed
        """
        # Check if changes are in different fields (no overlap)
        client_keys = set(client_data.keys())
        server_keys = set(server_data.keys())
        
        # Get keys that exist in both
        common_keys = client_keys & server_keys
        
        # Check if any common fields have different values
        conflicts = []
        for key in common_keys:
            if client_data.get(key) != server_data.get(key):
                conflicts.append(key)
        
        if not conflicts:
            # No actual conflicts - can auto-merge
            logger.info("No field conflicts detected - can auto-resolve")
            return True
        
        # Has conflicts - need user decision
        logger.info(f"Field conflicts detected: {conflicts} - requires user resolution")
        return False
    
    def create_conflict_info(
        self,
        client_version: int,
        server_version: int,
        server_updated_at: datetime,
    ) -> Dict[str, Any]:
        """
        Create conflict information for API response.
        
        Args:
            client_version: Client's version number
            server_version: Server's version number
            server_updated_at: When server version was last updated
            
        Returns:
            Conflict information dict
        """
        return {
            "conflict_type": "version_mismatch",
            "server_version": server_version,
            "client_version": client_version,
            "server_updated_at": server_updated_at.isoformat(),
            "message": f"Draft was modified by another session. Server has version {server_version}, but client attempted to save version {client_version}.",
        }


# Global instance
conflict_resolver = ConflictResolver()
