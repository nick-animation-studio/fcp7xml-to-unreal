from typing import List
from premiere_to_ue.models import Shot


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
