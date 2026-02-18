import re
import xml.etree.ElementTree as ET

from premiere_to_ue import config, logger
from premiere_to_ue.models.Audio import AudioFile
from premiere_to_ue.models.Shot import ConformScene, ConformShot, UnrealShot


class Episode:
    def __init__(self, xml_file):
        self.file = xml_file
        self.tree = ET.parse(xml_file)
        self.root = self.tree.getroot()
        self.track_names = []
        self.audio_files = []
        self.shot_count = 0
        self.removed = 0

        self.burnin_count = 0

        self.start_frame = 100000
        self.end_frame = -1

        self.cshots = []
        self.sshots = []
        self.fx_shots = []

        self.scenes = []
        self.notes = []

        self.ingest_log = ""

        video_tracks = self.root.findall("./sequence/media/video")
        for video in video_tracks:
            tracks_removed = 0
            for track in video.findall("track"):
                # remove disabled tracks entirely
                if track.find("enabled").text == "FALSE":
                    tracks_removed += 1
                    video.remove(track)
                    continue

        self.process_audio()
        self.process_video()

    def write_filtered(self):
        outfile = self.file[:-4] + "_filtered" + ".xml"
        try:
            self.tree.write(outfile)
        except Exception as e:
            logger.error(f"Error writing filtered XML: {e}")
        logger.info(f"Wrote filtered xml to file: {outfile}")
        return

    def process_audio(self):
        #
        # AUDIO
        # Clipitems are audio files, and they may have transitionitems connecting them.
        # For some reason, FCP XML doesn't write accurate start/end frame counts (it uses -1)
        # if there's a transition. That necessitates a 2-pass process over each track.
        #

        important_tags = ["clipitem", "transitionitem"]

        # Currently, remove all audio from the exported XML, but build a report of what was there.
        # More logic can be built in here to preserve audio if needed
        for audio in self.root.findall("./sequence/media/audio"):
            for track in audio.findall("track"):
                track_name = "undefined"
                if track.attrib is not None:
                    if "MZ.TrackName" in track.attrib:
                        track_name = track.attrib["MZ.TrackName"]
                        self.track_names.append(track_name)

                # first pass: store everything in the track in a list
                # so that we can find transitions in a second pass.
                track_contents = []
                for clipitem in track.findall("./*"):
                    if clipitem.tag not in important_tags:
                        continue
                    track_contents.append(clipitem)

                # second pass: go through the clipitems and patch up start/end frames
                for index, thing in enumerate(track_contents):
                    if thing.tag == "transitionitem":
                        continue

                    # here we have clipitems only.
                    name = thing.find("name").text
                    mcid = thing.find("masterclipid")
                    masterclipid = mcid.text if mcid is not None else "undefined"

                    pathurl = thing.find("./file/pathurl")
                    path = pathurl.text if pathurl is not None else ""

                    start_frame = int(thing.find("start").text)
                    end_frame = int(thing.find("end").text)

                    color = "undefined"
                    for ls in thing.findall("labels"):
                        color = ls.find("label2").text

                    if start_frame == -1:
                        # our start frame MUST come from a prior transitionitem.
                        # trying without error-checking because I'm careless
                        # TODO: Add error checking?
                        start_frame = int(track_contents[index - 1].find("start").text)
                    if end_frame == -1:
                        end_frame = int(track_contents[index + 1].find("end").text)

                    # find all filters
                    filters = []
                    for effect in thing.findall("./filter/effect/name"):
                        filters.append(effect.text)

                    af = AudioFile(
                        name,
                        path,
                        masterclipid,
                        start_frame,
                        end_frame,
                        track_name,
                        color,
                    )
                    af.effects = filters

                    found = False
                    for a in self.audio_files:
                        if a == af:
                            found = True
                            continue
                    if not found:
                        self.audio_files.append(af)

                audio.remove(track)

    def is_movie_file(self, name):
        for suffix in config["MOVIE_FILE_SUFFIXES"]:
            if name.endswith(suffix):
                return True
        return False

    def is_image_file(self, name):
        for suffix in config["IMAGE_FILE_SUFFIXES"]:
            if name.endswith(suffix):
                return True
        return False

    def is_conformshot_burnin(self, basename):
        if basename.startswith(config["CONFORMSHOT_BURNIN_PREFIX"]):
            return True
        return False

    def is_conformscene_burnin(self, basename):
        if basename.startswith(config["CONFORMSCENE_BURNIN_PREFIX"]):
            return True
        return False

    def process_video(self):
        for track in self.root.findall("./sequence/media/video/track"):
            for clipitem in track.findall("clipitem"):
                # remove disabled clips entirely
                if clipitem.find("enabled").text == "FALSE":
                    track.remove(clipitem)
                    continue

                name = clipitem.find("name").text

                start = clipitem.find("start").text
                end = clipitem.find("end").text

                inp = clipitem.find("in").text
                outp = clipitem.find("out").text

                # Is this clip a movie file?
                # If so, check if it's a valid story shot by matching its name against the regex from config
                # Uncomment the printout "NOTE" below if you fear something appropriate is being filtered out!
                if self.is_movie_file(name):
                    # TODO: use 'unreal shot' instead of 'story shot'
                    # TODO: should this regex live with UnrealShot? I think so.
                    story_shot_pattern = config["shot_name_regex"]
                    logger.debug(
                        f"Checking shot {name} against regex {story_shot_pattern}"
                    )
                    valid_story_shot = re.match(story_shot_pattern, name)
                    if valid_story_shot is None:
                        # print(f"NOTE: ignoring input clip {name} (it does not match story shot naming conventions)")
                        track.remove(clipitem)
                        continue

                    # Now let's filter the name to make it match UE level sequence naming
                    # Productions can have any number of filters, just run the list in order.

                    # TODO: eval() to be removed once yaml config is fixed to not double quote strings
                    filteredname = name
                    for resub in config["shot_name_resubs"]:
                        filteredname = re.sub(
                            eval(resub["pattern"]),
                            eval(resub["replacement"]),
                            filteredname,
                        )

                    # if we changed anything let's rename this
                    if filteredname != name:
                        clipitem.find("name").text = filteredname

                    # the start and end values will be bad if there's a transition.
                    # It's not clear how to fix this automatically! TODO: would be cool to figure out some logic
                    # Trying to be smart. If there are transitions on both sides, however, I'm not sure we can be.
                    if start == "-1":
                        if end == "-1":
                            self.ingest_log += f"**** Removing shot {name}. Check for transitions in the cut and remove them, then export XML and run again!\n"
                            track.remove(clipitem)
                            continue

                        start = int(end) - (int(outp) - int(inp))
                        self.ingest_log += f"Auto-fixed shot {name} which still has a transition on its start. Check for accuracy!\n"

                    if end == "-1":
                        end = int(start) + (int(outp) - int(inp))
                        self.ingest_log += f"Auto-fixed shot {name} which still has a transition on its end. Check for accuracy!\n"

                    # Confirmed this is a story shot, and by here its name has been filtered/cleaned.
                    # It has valid start/end frames.
                    # let's create it as a formal shot and add to our list of shots
                    this_shot = UnrealShot(filteredname, start, end, inp, outp)
                    self.sshots.append(this_shot)

                    # check for editing filters that necessitate fixes in 3D
                    for fx in clipitem.findall("filter/effect"):
                        fx_type = fx.find("effectid").text

                        if fx_type == "timeremap":
                            params = {}
                            # this is also time reversing?
                            for param in fx.findall("parameter"):
                                for param_option in [
                                    "speed",
                                    "reverse",
                                    "variablespeed",
                                    "graphdict",
                                ]:
                                    if param.find("parameterid").text == param_option:
                                        if param_option == "graphdict":
                                            keys = ""
                                            for key in param.findall("keyframe"):
                                                when = key.find("when").text
                                                val = key.find("value").text
                                                keys += f"(f{val} @ f{when}) "
                                            params[param_option] = keys
                                        else:
                                            params[param_option] = param.find(
                                                "value"
                                            ).text
                            if params["reverse"] == "FALSE":
                                params.pop("reverse")
                            if params["speed"] == "100":
                                params.pop("speed")
                            this_shot.add_fx(fx_type, params)

                        if fx_type == "basic":
                            params = {}
                            # this is scaling/panning
                            for param in fx.findall("parameter"):
                                # the most basic xforms an editor might use that need to be matched in UE
                                for param_option in ["scale", "rotation"]:
                                    if param.find("parameterid").text == param_option:
                                        # check for animation
                                        keys = ""
                                        for key in param.findall("keyframe"):
                                            when = key.find("when").text
                                            val = key.find("value").text
                                            keys += f"(f{val} @ f{when}) "
                                        if keys != "":
                                            params[param_option] = keys
                                        else:
                                            params[param_option] = param.find(
                                                "value"
                                            ).text

                            # some cleaning; remove no-ops
                            if "scale" in params and params["scale"] == "100":
                                params.pop("scale")
                            if "rotation" in params and params["rotation"] == "0":
                                params.pop("rotation")

                            if len(params) > 0:
                                this_shot.add_fx(fx_type, params)

                        if len(this_shot.fx.keys()) > 0:
                            self.fx_shots.append(this_shot)

                elif self.is_image_file(name):
                    from pathlib import Path

                    ue_asset_name = Path(name).stem

                    # force timebase for images to match config
                    for tb in clipitem.findall("rate"):
                        tb.find("timebase").text = config["frame_rate"]

                    # here we're looking for burnin files specific to this pipeline (set details in config.yaml)
                    if self.is_conformshot_burnin(ue_asset_name):
                        self.cshots.append(
                            ConformShot(ue_asset_name, start, end, inp, outp)
                        )
                        clipitem.find("name").text = ue_asset_name

                    elif self.is_conformscene_burnin(ue_asset_name):
                        self.scenes.append(
                            ConformScene(ue_asset_name, start, end, inp, outp)
                        )
                        clipitem.find("name").text = ue_asset_name

                    else:
                        track.remove(clipitem)

                else:
                    track.remove(clipitem)

        self.ingest_log += "\nEpisode XML contains:\n"
        self.ingest_log += f"\t{len(self.sshots)} unreal shots,\n"
        self.ingest_log += f"\t{len(self.cshots)} conform shots,\n"
        self.ingest_log += f"\t{len(self.scenes)} conform scenes,\n"
        self.ingest_log += f"\t{len(self.audio_files)} unique audio files.\n\n"

        minF = 1000000
        maxF = -1
        for cshot in self.cshots:
            minF = min(minF, cshot.ef)
            maxF = max(maxF, cshot.ef)

        # map cshots to their scenes
        for cshot in self.cshots:
            # look for all possible scene matches for this shot
            possible_scenes = []
            for scene in self.scenes:
                if scene.contains(cshot):
                    possible_scenes.append(scene)

            # Now choose one, if there is one
            if len(possible_scenes) == 0:
                self.ingest_log += (
                    f"Burnin {cshot.rawname} is not contained in any scene!\n"
                )
                continue

            scene_to_assign = None

            if len(possible_scenes) == 1:
                # this is the easy case
                scene_to_assign = possible_scenes[0]

            elif len(possible_scenes) > 1:
                # This shot fits into multiple scenes. But we need to pick one.
                possible_scenes.sort()

                if cshot.is_first_shot():
                    # print("shot numbered 1, so probably use the last scene")
                    scene_to_assign = possible_scenes[-1]
                else:
                    # print("based on shot number {shotnum:d}, using the first scene")
                    scene_to_assign = possible_scenes[0]
                # logger.warning(
                #    f"Placed shot {cshot.name} in {scene_to_assign.name} but it matched {len(possible_scenes):d} scenes."
                # )

            cshot.container = scene_to_assign

        # Warn about unmapped story shots
        for sshot in self.sshots:
            in_scene = False
            for scene in self.scenes:
                if scene.contains(sshot):
                    in_scene = True
                    continue

            if not in_scene:
                self.ingest_log += f"Shot {sshot.name()} is not in any scene\n"
