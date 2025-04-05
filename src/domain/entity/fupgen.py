from datetime import datetime
from typing import Any, Callable

from pydantic import BaseModel, model_serializer

from domain.entity.recurrence import RecurrenceConfig


class FupGenInput(BaseModel):
    hookid: str
    owner: str
    name: str
    recurrence: RecurrenceConfig
    active: bool
    channel: str
    msg: str | Callable[[dict[str, Any]], str]
    metadata: dict[str, Any] = {}
    description: str | None = None


class FupGenOutput(BaseModel):
    id: str
    created_at: datetime


class FollowupGenerator(FupGenInput, FupGenOutput):

    @property
    def get_msg(self) -> str | Callable[[dict[str, Any]], str]:
        if callable(self.msg):
            return self.msg(self.metadata)
        return self.msg

    @model_serializer(mode="plain")
    def serialize(self) -> dict[str, Any]:
        data = self.__dict__.copy()
        data["msg"] = self.get_msg
        return data


if __name__ == "__main__":
    ...
    # followup = FollowupGenerator(
    #     id="abc",
    #     msg=lambda d: f"Olá, {d.get('nome', 'sem nome')}",
    #     metadata={"nome": "João"},
    # )
    # print(followup.model_dump())
