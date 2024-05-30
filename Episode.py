class Episode:

    def __init__(self, xml_file, root):
        self.file = xml_file
        self.root = root
        self.shots = []
        self.track_names = []
        self.audio_files = []
        self.shot_count = 0
        self.removed = 0
        self.fx_shots = 0
        self.burnin_count = 0

        self.start_frame = 100000
        self.end_frame = -1

        self.cshots = []
        self.sshots = []
        # Is seqs correct? Not sure how we use sequence vs scene
        self.seqs = []

    def add_note(self, note):
        for shot in self.shots:
            if shot.contains(note):
                shot.notes.append(note)
