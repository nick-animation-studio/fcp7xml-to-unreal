class Note:
    def __init__(
        self,
        sf: int = None,
        ef: int = None,
        tags: list[str] = None,
        text: str = "",
    ):
        if tags is None:
            tags = []
        self.sf = int(sf)
        self.ef = int(ef)
        self.tags = tags
        self.text = text
        # self.assigned_to = None
        # self.resolved = False
        # self.revised_shot = None
        # self.date_finished = None
        # self.comments = []
