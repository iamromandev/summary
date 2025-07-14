

from src.core.base import BaseRepo
from src.db.models import State


class StateRepo(BaseRepo[State]):
    def __init__(self) -> None:
        super().__init__(State)



