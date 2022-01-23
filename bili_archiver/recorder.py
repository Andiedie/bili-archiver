import contextlib
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, String, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///record.db')
Session = sessionmaker(bind=engine)
Base = declarative_base()


@contextlib.contextmanager
def get_session():
    s = Session()
    try:
        yield s
        s.commit()
    except Exception as e:
        s.rollback()
        raise e
    finally:
        s.close()


class BaseMixin:
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)


class RunHistory(Base, BaseMixin):
    __tablename__ = 'run_history'

    key = Column(String, unique=True, nullable=False)
    last_run = Column(DateTime, nullable=False, default=datetime.now)


class DownloadHistory(Base, BaseMixin):
    __tablename__ = 'download_history'

    video_id = Column(Integer, unique=True, nullable=False)


Base.metadata.create_all(engine)


def get_last_run_time(key: str) -> datetime:
    with get_session() as s:
        record: RunHistory = s.query(RunHistory).filter(RunHistory.key == key).first()
        if record is None:
            return datetime.fromtimestamp(946656000)
        else:
            return record.last_run


def set_last_run_time(key: str, t: datetime = datetime.now()):
    with get_session() as s:
        record: RunHistory = s.query(RunHistory).filter(RunHistory.key == key).first()
        if record is None:
            record = RunHistory()
            record.key = key
            record.last_run = t
            s.add(record)
        else:
            record.last_run = t


def _del_last_run_time(key: str):
    with get_session() as s:
        s.query(RunHistory).filter(RunHistory.key == key).delete()


def is_downloaded(video_id: int) -> bool:
    with get_session() as s:
        record: DownloadHistory = s.query(DownloadHistory).filter(DownloadHistory.video_id == video_id).first()
        return record is not None


def downloaded(video_id: int):
    with get_session() as s:
        record: DownloadHistory = s.query(DownloadHistory).filter(DownloadHistory.video_id == video_id).first()
        if record is None:
            record = DownloadHistory()
            record.video_id = video_id
            s.add(record)


def _del_downloaded(video_id: int):
    with get_session() as s:
        s.query(DownloadHistory).filter(DownloadHistory.video_id == video_id).delete()
