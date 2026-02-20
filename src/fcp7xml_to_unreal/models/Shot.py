from abc import ABC, abstractmethod

from fcp7xml_to_unreal import config


# A TimelineEntity is something that lives in a timeline, could be a shot, a burnin, a scene marker etc.
class TimelineEntity(ABC):
    def __init__(self, name, sf, ef, ip, op):
        self.rawname = name
        self.sf = int(sf)
        self.ef = int(ef)
        self.ip = int(ip)
        self.op = int(op)
        self.dur = self.sf - self.ef
        self.clipdur = self.op - self.ip
        self.notes = []
        self.fx = {}
        self.container = None  # e.g. broader entity containing this shot, aka a scene

    # TODO: needed?
    # def is_valid(self):
    #    logger.info(f"shot: {self.ip} {self.op} {self.sf} {self.ef}")
    #    return True

    # The name method needs local implementation and needs to be sortable
    @abstractmethod
    def name(self):
        pass

    def __lt__(self, other):
        return self.name() < other.name()

    def __str__(self):
        outstr = f"{self.rawname:30s} {self.sf:6d} {self.ef:6d}"
        return outstr

    def fx_str(self):
        outstr = ""
        for k in self.fx:
            outstr += f" FX: {k}"
            for param in self.fx[k]:
                outstr += f" {param} {self.fx[k][param]}"
        return outstr

    def has_fx(self):
        return len(self.fx) > 0

    def match(self, s):
        # Logic is this:
        # If both start and end frames match, it's "perfect"
        # If the above isn't true, and both start and end are within 2, it's "close"
        # Otherwise it's not a match (None)

        if (self.sf == s.sf) & (self.ef == s.ef):
            return "perfect"
        elif (self.ef in range(s.ef - 2, s.ef + 2)) & (
            self.sf in range(s.sf - 2, s.sf + 2)
        ):
            return "close"
        else:
            return None

    # return true if s is inside self
    def contains(self, s):
        return (s.sf >= self.sf) & (s.ef <= self.ef)

    # return true if this TimelineEntity overlaps any of the frame range given
    def overlaps(self, sf, ef):
        return not (ef < self.sf) | (sf > self.ef)

    def add_fx(self, fx_name, fx_val_dict):
        self.fx[fx_name] = fx_val_dict


# Whatever your pipeline, you can build in your local specifics to these subclasses.
# Scenes are made up of StoryShots.
# When it's time to conform, ConformedShots are matched to StoryShots.


class UnrealShot(TimelineEntity):
    def __init__(self, name, sf, ef, ip, op):
        super().__init__(name, sf, ef, ip, op)

    def name(self):
        return self.rawname

    # def scene_number(self):
    #    return self.rawname.split("_")[1]


class ConformScene(TimelineEntity):
    def __init__(self, name, sf, ef, ip, op):
        super().__init__(name, sf, ef, ip, op)

    # Our scene burnin images were named as follows:
    # seq_001,
    # seq_121a, etc.
    # So returning the name without the prefix 'seq_' gives us our sortable scene "name"
    def name(self):
        # TODO: this is the raw name less the prefix defined in ALL CAPS

        return self.rawname[len(config["CONFORMSCENE_BURNIN_PREFIX"]) :]


class ConformShot(TimelineEntity):
    def __init__(self, name, sf, ef, ip, op):
        super().__init__(name, sf, ef, ip, op)

    def name(self):
        # ConformShots in this implementation are named SC_SHT
        # SC  = Scene code
        # SHT = Shot code
        # TODO: this is the raw name less the prefix defined in ALL CAPS

        return (
            self.container.name()
            + "_"
            + self.rawname[len(config["CONFORMSHOT_BURNIN_PREFIX"]) :]
        )

    # TODO: this is very implementation-specific, and exists only to try and auto-resolve issues where
    # the conform shot burnin overlaps with multiple scene burnins.

    def is_first_shot(self):
        return int(self.rawname[3:]) == 1
