"""System settings model — global configuration for Myestro platform."""

from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Text, DateTime
from sqlalchemy.sql import func
from app.database import Base


class SystemSetting(Base):
    """Global system settings key-value store.
    
    Keys:
    - ai_global_enabled: "true" / "false" — global AI toggle
    """
    __tablename__ = "system_settings"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<SystemSetting {self.key}={self.value}>"