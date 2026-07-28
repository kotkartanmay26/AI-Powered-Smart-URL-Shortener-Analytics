
from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Click(Base):
    __tablename__ = "clicks"

    id = Column(Integer, primary_key=True, index=True)
    url_id = Column(Integer, ForeignKey("urls.id"), nullable=False)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    referrer = Column(String, nullable=True)
    country = Column(String, nullable=True)
    browser = Column(String, nullable=True)
    device = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    url = relationship("URL", back_populates="clicks")


Index("ix_clicks_url_created", Click.url_id, Click.created_at)
