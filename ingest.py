from matm.Audio import AudioFile
from matm.Episode import Episode
from matm.Note import Note
from matm.Shot import Shot

import xml.etree.ElementTree as ET
import re

RENDER_FILE_TYPES = {"mov"}

BAD_CLIP_NAMES = {
    "Max_animation_promo_may14_v4.mp4",
    "Screen Recording 2022-08-19 at 4.35.35 PM.mp4",
    "MATM_101_Welcome_to_Byjovia_ColdOpenWIP_220830.mp4",
    "MATM_Main-Tilte-Placeholder_220819.mp4",
    "8mm overlay film borders.mp4",
    "Light-flicker.mp4",
}


def process_audio(episode: Episode):
    #
    # AUDIO
    # Clipitems are audio files, and they may have transitionitems connecting them.
    # For some reason, FCP XML doesn't write accurate start/end frame counts (it uses -1)
    # if there's a transition. That necessitates a 2-pass process over each track.
    #

    important_tags = ["clipitem", "transitionitem"]

    for audio in episode.root.findall("./sequence/media/audio"):

        for track in audio.findall("track"):

            if "MZ.TrackName" in track.attrib:
                track_name = track.attrib["MZ.TrackName"]
                episode.track_names.append(track_name)
            else:
                track_name = "undefined"

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
                masterclipid = thing.find("masterclipid").text
                pathurl = thing.find("./file/pathurl")
                if pathurl is not None:
                    # remove the leading "file://localhost" URL stuff
                    path = pathurl.text[16:]
                else:
                    path = ""
                start_frame = int(thing.find("start").text)
                end_frame = int(thing.find("end").text)
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
                    name, path, masterclipid, start_frame, end_frame, track_name, color
                )
                af.effects = filters

                found = False
                for a in episode.audio_files:
                    if a == af:
                        found = True
                        continue
                if not found:
                    episode.audio_files.append(af)

            audio.remove(track)


def process_video(episode: Episode):
    for track in episode.root.findall("./sequence/media/video/track"):

        for clipitem in track.findall("clipitem"):

            name = clipitem.find("name").text
            # remove disabled clips entirely
            if clipitem.find("enabled").text == "FALSE":
                track.remove(clipitem)
                continue
            start = clipitem.find("start").text
            end = clipitem.find("end").text

            inp = clipitem.find("in").text
            outp = clipitem.find("out").text

            this_shot = Shot(name, start, end, inp, outp)
            episode.shots.append(this_shot)

            if name[-3:] in RENDER_FILE_TYPES:

                # hard-coding some known bad mp4 names
                if name in BAD_CLIP_NAMES:
                    track.remove(clipitem)
                    episode.shots.remove(this_shot)
                    continue

                # get rid of (2) and such if there
                newname = re.sub(r"\(.*\)", "", name)

                # get rid of _SB if it's there
                newname = newname.replace("_SB", "")

                # get rid of date _xxxxxxxx if it's there
                newname = re.sub(r"\_\d\d\d\d\d\d\d\d", "", newname)

                if newname != name:
                    clipitem.find("name").text = newname

                this_shot.name = newname

                # the start and end values will be bad if there's a transition.
                # It's not clear how to fix this automatically!

                if (this_shot.ef == -1) | (this_shot.ef == -1):
                    print(f"**** Shot {newname} has bogus start/end frames.")
                    print("Need to fix, but for now eliminating entirely.")
                    track.remove(clipitem)
                    episode.shots.remove(this_shot)
                    continue

                episode.sshots.append(this_shot)

                # check for premiere filters that necessiate fixes in 3D
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
                                        params[param_option] = param.find("value").text
                        if params["reverse"] == "FALSE":
                            params.pop("reverse")
                        if params["speed"] == "100":
                            params.pop("speed")
                        this_shot.add_fx(fx_type, params)

                    if fx_type == "basic":
                        params = {}
                        # this is scaling/panning
                        for param in fx.findall("parameter"):
                            for param_option in ["scale", "rotation"]:
                                if param.find("parameterid").text == param_option:
                                    params[param_option] = param.find("value").text
                        # some cleaning
                        if "scale" in params:
                            if params["scale"] == "100":
                                params.pop("scale")
                        if "rotation" in params:
                            if params["rotation"] == "0":
                                params.pop("rotation")
                        this_shot.add_fx(fx_type, params)

                    if len(this_shot.fx.keys()) > 0:
                        episode.fx_shots.append(this_shot)

            elif name[-3:] == "png":

                basename = name[:-4]

                # set timebase to 24fps
                for tb in clipitem.findall("rate"):
                    tb.find("timebase").text = "24"

                if basename[:3] in ["Sc_"]:
                    # this is a valid conform burnin shot marker

                    episode.cshots.append(this_shot)

                    # rename to match the corresponding level sequence in UE
                    clipitem.find("name").text = basename

                elif basename[:3] in ["seq"]:
                    episode.seqs.append(this_shot)

                else:
                    episode.shots.remove(this_shot)
                    track.remove(clipitem)

            else:
                episode.shots.remove(this_shot)
                track.remove(clipitem)

    # figure out full TC of episode, minus slate
    minF = 10000
    maxF = -1
    for cshot in episode.cshots:
        minF = min(minF, cshot.ef)
        maxF = max(maxF, cshot.ef)

    # map cshots to their sequences
    for cshot in episode.cshots:
        in_seq = False
        for seq in episode.seqs:
            if seq.contains(cshot):
                cshot.name = seq.name[3:-4] + "_" + cshot.name[3:-4]
                cshot.seq = seq.name
                in_seq = True
                continue
        if in_seq == False:
            print(f"Shot {cshot.name} not in any sequence")

    # Removed unmapped story shots
    for sshot in episode.sshots:
        in_seq = False
        for seq in episode.seqs:
            if seq.contains(sshot):
                in_seq = True
                continue
        if in_seq == False:
            print(f"Shot {sshot.name} not in any sequence, removing")
            for track in episode.root.findall("./sequence/media/video/track"):
                for clipitem in track.findall("clipitem"):
                    name = clipitem.find("name").text
                    if name == sshot.name:
                        track.remove(clipitem)
            episode.sshots.remove(sshot)
            episode.shots.remove(sshot)


def process_notes(episode: Episode):
    for track in episode.root.findall("./sequence/media/video/track"):
        for clipitem in track.findall("clipitem"):
            for note in clipitem.findall("filter/effect"):
                if note.find("effectid").text == "GraphicAndType":
                    start = clipitem.find("start").text
                    end = clipitem.find("end").text

                    text = note.find("name").text
                    if not text:
                        continue
                    words = text.split(" ")
                    tags = [w for w in words if w.startswith("#")]
                    all_tags = ",".join(tags)
                    nontags = [word for word in words if word not in all_tags]
                    comment_without_tags = " ".join(nontags)

                    episode.add_note(Note(start, end, tags, comment_without_tags))


def ingest(xml_file):
    episode = Episode(xml_file)

    video_tracks = episode.root.findall("./sequence/media/video")
    for video in video_tracks:
        tracks_removed = 0
        for track in video.findall("track"):
            if track.find("enabled").text == "FALSE":
                tracks_removed += 1
                video.remove(track)
                continue

    process_audio(episode)
    process_video(episode)
    process_notes(episode)

    return episode
