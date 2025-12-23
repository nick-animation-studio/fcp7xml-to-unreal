from urllib.parse import unquote

from premiere_to_ue import config, logger
from premiere_to_ue.models.helpers import frames_to_tc


class AudioFile:
    OUTPUT_VALS = [
        "trackname",
        "filename",
        "starttime",
        "endtime",
        "shotlist",
        "trackcolor",
        "label",
        "effects",
        "path",
    ]

    def __init__(
        self,
        filename,
        path,
        masterclipid,
        startFrame,
        endFrame,
        trackName=None,
        trackColor=None,
    ):
        self.trackname = trackName
        self.filename = filename
        self.path = unquote(path)
        self.masterclipid = masterclipid
        self.sf = int(startFrame)
        self.starttime = frames_to_tc(self.sf)
        self.ef = int(endFrame)
        self.endtime = frames_to_tc(self.ef)

        self.trackcolor = trackColor
        self.printed = False
        self.effects = []
        self.shotlist = []

        self.label = None

        # 2025-12-22 macleodj-paramount simplify is_dialogue() check to label colors only
        if self.trackcolor.lower() in config["audio"]["track_colors"]:
            self.label = config["audio"]["track_colors"][self.trackcolor.lower()]
        else:
            self.label = config["audio"]["track_color_nomatch_label"]

        # if _ef is -1, we can grab in and out, subtract in from out, add to sf to get ef

        if (self.sf == -1) | (self.ef == -1):
            self.badTC = True
        else:
            self.badTC = False

        logger.debug(
            f"Processing AudioFile entry for file reference named {self.filename}"
        )

    def is_music(self):
        return self.trackname.startswith(config["audio"]["music_track_prefix"])

    def is_sfx(self):
        return self.trackname.startswith(config["audio"]["sfx_track_prefix"])

    def is_dialogue(self):
        sfx_or_music = (
            self.trackname.startswith(config["audio"]["sfx_track_prefix"])
        ) | (self.trackname.startswith(config["audio"]["music_track_prefix"]))
        return not sfx_or_music

    def to_list(self):
        return [getattr(self, key) for key in self.OUTPUT_VALS]

    def __str__(self):
        as_list = self.to_list()
        as_list = [f"{i}" for i in as_list]
        return ",".join(as_list)

    def __eq__(self, x):
        return (
            (self.filename == x.filename)
            & (self.sf == x.sf)
            & (self.ef == x.ef)
            & (self.trackname == x.trackname)
            & (self.trackcolor == x.trackcolor)
        )
