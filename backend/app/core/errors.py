"""
Custom Exception Classes

Defines application-specific exceptions for error handling.
"""

from typing import Any, Optional


class AutoBidderError(Exception):
    """Base exception for Auto-Bidder application."""

    def __init__(self, message: str, details: Optional[Any] = None) -> None:
        """Initialize exception with message and optional details."""
        self.message = message
        self.details = details
        super().__init__(self.message)


class DocumentProcessingError(AutoBidderError):
    """Exception raised during document processing."""

    pass


class EmbeddingError(AutoBidderError):
    """Exception raised during embedding generation."""

    pass


class VectorStoreError(AutoBidderError):
    """Exception raised during vector store operations."""

    pass


class ProposalGenerationError(AutoBidderError):
    """Exception raised during proposal generation."""

    pass


class ScrapingError(AutoBidderError):
    """Exception raised during job scraping."""

    pass


class AuthenticationError(AutoBidderError):
    """Exception raised for authentication failures."""

    pass


class RateLimitError(AutoBidderError):
    """Exception raised when rate limit is exceeded."""

    pass


class ValidationError(AutoBidderError):
    """Exception raised for validation failures."""

    pass


class ConflictError(AutoBidderError):
    """Exception raised when a version conflict is detected."""

    pass
