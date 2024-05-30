from matm.helpers import *
from urllib.parse import unquote


class AudioFile:

    def __init__(
        self, filename, path, masterclipid, startFrame, endFrame, trackName, trackColor
    ):
        self.filename = filename
        self.path = path
        self.masterclipid = masterclipid
        self.sf = int(startFrame)
        self.ef = int(endFrame)
        self.trackname = trackName
        self.trackcolor = trackColor
        self.printed = False
        self.effects = []
        self.shotlist = []

        self.label = ""
        if self.trackcolor == "Yellow":
            self.label = "From Viacom Library"
        if self.trackcolor == "Brown":
            if self.is_dialogue():
                self.label = "Scratch VO"
            else:
                self.label = "Unlicensed Material"

        # if _ef is -1, we can grab in and out, subtract in from out, add to sf to get ef

        if (self.sf == -1) | (self.ef == -1):
            self.badTC = True
        else:
            self.badTC = False

        # print( f"Creating AudioFile named {self.filename}")

    def is_music(self):
        return self.trackname.startswith("Music")

    def is_sfx(self):
        return self.trackname.startswith("SFX")

    def is_dialogue(self):
        sfx_or_music = (self.trackname.startswith("SFX")) | (
            self.trackname.startswith("Music")
        )
        return not sfx_or_music

    #
    # header and info dumping should be more coordinated, it's too easy for these to get out of sync.
    #
    def dump_header(self):
        return [
            "TRACK",
            "FILE",
            "START_TC",
            "END_TC",
            "SHOTLIST",
            "COLOR",
            "LABEL",
            "EFFECTS",
            "PATH",
        ]

    def dump(self):

        shotlist = ", ".join([s.name for s in self.shotlist])
        fx = ", ".join(self.effects)

        return [
            self.trackname,
            self.filename,
            frames_to_TC(self.sf),
            frames_to_TC(self.ef),
            shotlist,
            self.trackcolor,
            self.label,
            fx,
            unquote(self.path),
        ]

    def __str__(self):

        return ",".join(self.dump())

    def __eq__(self, x):
        return (
            (self.filename == x.filename)
            & (self.sf == x.sf)
            & (self.ef == x.ef)
            & (self.trackname == x.trackname)
            & (self.trackcolor == x.trackcolor)
        )
