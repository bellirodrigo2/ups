from datetime import datetime

from pydantic import BaseModel

from domain.entity.fup import FollowUp


class Task(BaseModel):
    taskid: str
    fupgen_id: str
    run_from: datetime
    run_until: datetime
    fups: list[FollowUp]
