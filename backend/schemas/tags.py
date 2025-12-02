from typing import List

from pydantic import BaseModel


class TagResponse(BaseModel):
    name: str


class TagCreateRequest(BaseModel):
    tag_name: str


class TagListResponse(BaseModel):
    tags: List[TagResponse]


