from datetime import datetime

from pydantic import BaseModel

from domain.entity.channel import Channel
from domain.entity.recurrence import RecurrenceConfig


class FupGenReadConfig(BaseModel):
    hookid: str | None = None
    ownerid: str | None = None
    name: str | None = None
    active: bool | None = None
    channel: str | None = None
    # datahas: dict[str, Any] | None = None
    description: str | None = None


class FupGenInput(BaseModel):
    hookid: str
    ownerid: str
    name: str
    recurrence: RecurrenceConfig
    active: bool
    channel: list[Channel]
    msg: str  # | Callable[[dict[str, Any]], str]
    # data: dict[str, Any] = {}
    description: str | None = None


class FupGenOutput(BaseModel):
    id: str
    created_at: datetime


class FollowupGenerator(FupGenInput, FupGenOutput):
    last_run: datetime

    # @property
    # def get_msg(self) -> str | Callable[[dict[str, Any]], str]:
    #     if callable(self.msg):
    #         return self.msg(self.data)
    #     return self.msg

    # @model_serializer(mode="plain")
    # def serialize(self) -> dict[str, Any]:
    #     data = self.__dict__.copy()
    #     data["msg"] = self.get_msg
    #     return data


if __name__ == "__main__":
    ...
    # followup = FollowupGenerator(
    #     id="abc",
    #     msg=lambda d: f"Olá, {d.get('nome', 'sem nome')}",
    #     metadata={"nome": "João"},
    # )
    # print(followup.model_dump())
