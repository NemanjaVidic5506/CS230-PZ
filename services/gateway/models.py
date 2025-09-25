from sqlalchemy.orm import declarative_base, Mapped, mapped_column, Session
from sqlalchemy import String, JSON, create_engine, select
from datetime import datetime
from typing import Optional
from config import DATABASE_URL

Base = declarative_base()
engine = create_engine(DATABASE_URL, echo=False, future=True)

class Job(Base):
    __tablename__ = "jobs"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)  
    job_type: Mapped[str] = mapped_column(String(32))
    params: Mapped[dict] = mapped_column(JSON)
    state: Mapped[str] = mapped_column(String(32), default="PENDING")
    result: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), default=lambda: datetime.utcnow().isoformat(timespec="seconds"))

Base.metadata.create_all(engine)

def upsert_job(task_id: str, job_type: str, params: dict, state: str):
    with Session(engine) as s:
        j = s.get(Job, task_id)
        if not j:
            j = Job(id=task_id, job_type=job_type, params=params, state=state)
            s.add(j)
        else:
            j.state = state
        s.commit()

def set_job_result(task_id: str, state: str, result: dict | None):
    with Session(engine) as s:
        j = s.get(Job, task_id)
        if j:
            j.state = state
            j.result = result
            s.commit()

def list_jobs(limit=50):
    with Session(engine) as s:
        stmt = select(Job).order_by(Job.created_at.desc()).limit(limit)
        return [{
            "task_id": j.id,
            "job_type": j.job_type,
            "params": j.params,
            "state": j.state,
            "result": j.result,
            "created_at": j.created_at,
        } for j in s.execute(stmt).scalars().all()]
