import contextlib
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, String, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from typing import List

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


class CollectHistory(Base, BaseMixin):
    __tablename__ = 'collect_history'

    key = Column(String, unique=True, nullable=False)
    last_time = Column(DateTime, nullable=False, default=datetime.now)


class DownloadHistory(Base, BaseMixin):
    __tablename__ = 'download_history'

    video_id = Column(Integer, unique=True, nullable=False)
    downloaded = Column(Integer, nullable=False, default=0)
    disappeared = Column(Integer, nullable=False, default=0)


Base.metadata.create_all(engine)


def get_last_collect_time(key: str) -> datetime:
    with get_session() as s:
        record: CollectHistory = s.query(CollectHistory).filter(CollectHistory.key == key).first()
        if record is None:
            return datetime.fromtimestamp(946656000)
        else:
            return record.last_time


def set_last_collect_time(key: str, t: datetime = datetime.now()):
    with get_session() as s:
        record: CollectHistory = s.query(CollectHistory).filter(CollectHistory.key == key).first()
        if record is None:
            record = CollectHistory()
            record.key = key
            record.last_time = t
            s.add(record)
        else:
            record.last_time = t


def _del_last_collect_time(key: str):
    with get_session() as s:
        s.query(CollectHistory).filter(CollectHistory.key == key).delete()


def is_collected(video_id: int) -> bool:
    with get_session() as s:
        record: DownloadHistory = s.query(DownloadHistory).filter(DownloadHistory.video_id == video_id).first()
        return record is not None


def is_downloaded(video_id: int) -> bool:
    with get_session() as s:
        record: DownloadHistory = s.query(DownloadHistory).filter(DownloadHistory.video_id == video_id).first()
        return record is not None and record.downloaded == 1


def is_disappeared(video_id: int) -> bool:
    with get_session() as s:
        record: DownloadHistory = s.query(DownloadHistory).filter(DownloadHistory.video_id == video_id).first()
        return record is not None and record.disappeared == 1


def download_history_set(video_id: int,
                         downloaded: bool = None,
                         disappeared: bool = None):
    with get_session() as s:
        record: DownloadHistory = s.query(DownloadHistory).filter(DownloadHistory.video_id == video_id).first()
        should_add = False
        if record is None:
            should_add = True
            record = DownloadHistory()
            record.video_id = video_id
        if downloaded is not None:
            record.downloaded = 1 if downloaded else 0
        if disappeared is not None:
            record.disappeared = 1 if disappeared else 0
        if should_add:
            s.add(record)


def get_to_download():
    with get_session() as s:
        records: List[DownloadHistory] = s.query(DownloadHistory).\
            filter(DownloadHistory.downloaded == 0 and DownloadHistory).\
            filter(DownloadHistory.disappeared == 0).\
            order_by(DownloadHistory.video_id.desc()).all()
        s.expunge_all()
        return records


def _del_downloaded(video_id: int):
    with get_session() as s:
        s.query(DownloadHistory).filter(DownloadHistory.video_id == video_id).delete()
