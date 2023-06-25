from dataclasses import dataclass
import enum

class AccessLevel(enum.Enum):
    VISITOR = 0
    MEMBER = 1
    ADMIN = 2

@dataclass
class User:
    telegram_id: int
    access_level: AccessLevel
    name: str
    nickname: str
    city: str
    link_to_photo: str
    score: int
    gamescore: int
    ordering: int

async def get_all_users() -> list[User]:
    pass
