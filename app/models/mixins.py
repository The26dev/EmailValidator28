"""SQLAlchemy model mixins for encryption support."""

from sqlalchemy import event, String, TypeDecorator
from sqlalchemy.orm import declared_attr

from app.security.encryption import encryption_service

class EncryptedString(TypeDecorator):
    """Encrypted string type for SQLAlchemy."""
    
    impl = String
    cache_ok = True
    
    def process_bind_param(self, value, dialect):
        """Encrypt value before saving to database."""
        if value is not None:
            encrypted = encryption_service.encrypt_value(value)
            return str(encrypted)
        return None
        
    def process_result_value(self, value, dialect):
        """Decrypt value when loading from database."""
        if value is not None:
            return encryption_service.decrypt_value(eval(value))
        return None

class EncryptedMixin:
    """Mixin to add encryption capabilities to SQLAlchemy models."""
    
    @declared_attr
    def __encrypted_fields__(cls):
        """List of fields that should be encrypted."""
        return []
        
    @classmethod
    def __declare_last__(cls):
        """Configure encryption for specified fields."""
        for field_name in cls.__encrypted_fields__:
            # Get the original column
            column = getattr(cls, field_name)
            
            # Create new column with encryption
            new_column = column.copy()
            new_column.type = EncryptedString(length=1024)
            
            # Replace the original column
            setattr(cls, field_name, new_column)