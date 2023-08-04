import enum


class AccessLevel(enum.Enum):
    WALKER: 'AccessLevel' = 0
    USER: 'AccessLevel' = 1
    ADMIN: 'AccessLevel' = 2


def get_access_level(access_level_id: int) -> AccessLevel:
    match access_level_id:
        case 0:
            return AccessLevel.WALKER
        case 1:
            return AccessLevel.USER
        case 2:
            return AccessLevel.ADMIN
        case _:
            raise ValueError(f"Unsupported access_level_id value: {access_level_id}")
