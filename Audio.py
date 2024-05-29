from matm.helpers import *
from urllib.parse import unquote


class AudioFile:

    def __init__(
        self, filename, path, masterclipid, startFrame, endFrame, trackName, trackColor
    ):
        self._filename = filename
        self._path = path
        self._masterclipid = masterclipid
        self._sf = int(startFrame)
        self._ef = int(endFrame)
        self._trackname = trackName
        self._trackcolor = trackColor
        self._printed = False
        self._effects = []
        self._shotlist = []

        self._label = ""
        if self._trackcolor == "Yellow":
            self._label = "From Viacom Library"
        if self._trackcolor == "Brown":
            if self.is_dialogue():
                self._label = "Scratch VO"
            else:
                self._label = "Unlicensed Material"

        # if _ef is -1, we can grab in and out, subtract in from out, add to sf to get ef

        if (self._sf == -1) | (self._ef == -1):
            self._badTC = True
        else:
            self._badTC = False

        # print( f"Creating AudioFile named {self._filename}")

    def is_music(self):
        return self._trackname.startswith("Music")

    def is_sfx(self):
        return self._trackname.startswith("SFX")

    def is_dialogue(self):
        sfx_or_music = (self._trackname.startswith("SFX")) | (
            self._trackname.startswith("Music")
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

        shotlist = ", ".join([s._name for s in self._shotlist])
        fx = ", ".join(self._effects)

        return [
            self._trackname,
            self._filename,
            frames_to_TC(self._sf),
            frames_to_TC(self._ef),
            shotlist,
            self._trackcolor,
            self._label,
            fx,
            unquote(self._path),
        ]

    def __str__(self):

        return ",".join(self.dump())

    def __eq__(self, x):
        return (
            (self._filename == x._filename)
            & (self._sf == x._sf)
            & (self._ef == x._ef)
            & (self._trackname == x._trackname)
            & (self._trackcolor == x._trackcolor)
        )
