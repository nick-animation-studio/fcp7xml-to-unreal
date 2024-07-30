class Shot:

    def __init__(self, name, sf, ef, ip, op):
        self.name = name
        self.sf = int(sf)
        self.ef = int(ef)
        self.ip = int(ip)
        self.op = int(op)
        self.dur = self.sf - self.ef
        self.clipdur = self.op - self.ip
        self.fx = {}
        self.seq = None
        self.matched_shot = None

        self.notes = []

    def scene_number(self):
        return self.name.split("_")[1]
    
    def is_valid(self):
        print(self.ip, " ", self.op, " ", self.sf, " ", self.ef)
        return True

    def __str__(self):
        outstr = f"{self.name:30s} {self.sf:6d} {self.ef:6d}"
        return outstr

    def fx_str(self):
        outstr = ""
        for k in self.fx:
            outstr += f" FX: {k}"
            for param in self.fx[k]:
                outstr += f" {param} {self.fx[ k][ param]}"
        return outstr

    def match(self, s):

        # Logic is this:
        # If both start and end frames match, it's "perfect"
        # If the above isn't true, and both start and end are within 2, it's "close"
        # Otherwise it's not a match (None)
        
        if (self.sf == s.sf) & (self.ef == s.ef):
            return "perfect"
        elif (self.ef in range(s.ef - 2, s.ef + 2)) & (self.sf in range(s.sf - 2, s.sf + 2)):
            return "close"
        else:
            return None

    # return true if s is inside self
    def contains(self, s):
        return (s.sf >= self.sf) & (s.ef <= self.ef)

    # return true if this shot overlaps any of the frame range given
    def overlaps(self, sf, ef):
        if (ef < self.sf) | (sf > self.ef):
            return False
        else:
            return True

    def add_fx(self, fx_name, fx_val_dict):
        add_it = True
        """
        if (fx_name == "basic"):
            if (fx_val_dict[ "scale"] == "200") & (fx_val_dict[ "rotation"] == "0"):
                add_it = False
        """
        if add_it:
            self.fx[fx_name] = fx_val_dict

    def has_fx(self):
        return len(self.fx) > 0
