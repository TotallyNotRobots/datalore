import os

from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

__all__ = ("Session", "metadata", "engine", "Base")

engine = create_engine(os.getenv("DB_URL", "sqlite:///datalore.db"))
Session = scoped_session(sessionmaker(bind=engine))

_Base = declarative_base(bind=engine)


class Base(_Base):
    __abstract__ = True


metadata: MetaData = Base.metadata
