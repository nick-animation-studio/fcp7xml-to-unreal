from typing import List
from matm import Shot


class Note:

    def __init__(
        self,
        sf: int = None,
        ef: int = None,
        tags: List[str] = [],
        text: str = "",
    ):
        self.sf = int(sf)
        self.ef = int(ef)
        self.tags = tags
        self.text = text
        # self.assigned_to = None
        # self.resolved = False
        # self.revised_shot = None
        # self.date_finished = None
        # self.comments = []
