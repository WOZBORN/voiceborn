from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, DateTime
from . import Base

class User(Base):
    __tablename__ = "users"

    telegram_id = Column(BigInteger, primary_key=True, index=True)
    limit = Column(Integer, default=1000)
    limit_usage = Column(Integer, default=0)
    limit_renew_date = Column(DateTime, default=datetime.utcnow)
