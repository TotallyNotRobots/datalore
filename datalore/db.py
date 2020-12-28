import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

__all__ = ("Session", "metadata", "engine", "Base")

engine = create_engine(os.getenv("DB_URL", "sqlite:///datalore.db"))
Session = scoped_session(sessionmaker(bind=engine))

_DeclarativeMeta = declarative_base(bind=engine)


class Base(_DeclarativeMeta):
    __abstract__ = True

    def __repr__(self) -> str:
        db_session = Session()
        obj = db_session.merge(self)
        obj_type = type(obj)
        cols = [col.name for col in obj_type.__table__.columns]
        return "{}({})".format(
            obj_type.__name__,
            ", ".join(
                "{}={!r}".format(name, getattr(obj, name)) for name in cols
            ),
        )


metadata = Base.metadata
