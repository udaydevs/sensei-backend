"""Model for prompt"""
from typing import Annotated
from pydantic import BaseModel, Field


class Prompt(BaseModel):
    """Model for prompts are defined here"""
    prompt: Annotated[
        str,
        Field(
            min_length=2,
            description="Prompt given by user to the llm model"
        )
    ]
