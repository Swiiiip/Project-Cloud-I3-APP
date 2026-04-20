from dataclasses import dataclass

from pydantic import BaseModel


@dataclass(frozen=True)
class GuessSlotMatch(BaseModel):
    first_slot_match: bool
    second_slot_match: bool
