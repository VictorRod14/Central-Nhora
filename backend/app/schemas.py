from pydantic import BaseModel, Field


class LoginInput(BaseModel):
    email: str
    password: str


class MessageInput(BaseModel):
    content: str = Field(min_length=1, max_length=10000)
    private: bool = False


class StatusInput(BaseModel):
    status: str


class AssignmentInput(BaseModel):
    assignee_id: int | None = None


class LabelsInput(BaseModel):
    labels: list[str]


class LabelInput(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    color: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    description: str = Field(default="", max_length=255)


class NewConversationInput(BaseModel):
    name: str
    phone_number: str
    inbox_id: int
    message: str
