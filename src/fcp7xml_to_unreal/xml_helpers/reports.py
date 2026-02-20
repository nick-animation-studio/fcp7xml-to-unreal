import csv
import os
import subprocess
import tempfile

from fcp7xml_to_unreal.models.Audio import AudioFile


def audio_report(episode, to_csv=False):
    # create a dictionary of master clip id to name so we can get the path of any audiofile
    master_clip_dict = {}
    for af in episode.audio_files:
        mcid = af.masterclipid
        mcpath = af.path
        if (mcid not in master_clip_dict) & (mcpath is not None):
            master_clip_dict[mcid] = mcpath

    # set the master clip paths
    for af in episode.audio_files:
        if af.masterclipid in master_clip_dict:
            af.path = master_clip_dict[af.masterclipid]

    # go through dialogue files, try and identify which scenes they're in.
    for af in episode.audio_files:
        if af.is_dialogue():
            for cshot in episode.cshots:
                if cshot.overlaps(af.sf, af.ef):
                    af.shotlist.append(cshot.name())

    # now write out

    if to_csv:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", newline="", delete=False
        ) as tmpfile:
            csvwriter = csv.writer(tmpfile, dialect="excel", quoting=csv.QUOTE_MINIMAL)
            csvwriter.writerow(episode.audio_files[0].dump_header())
            for tn in episode.track_names:
                for af in episode.audio_files:
                    if (af.trackname == tn) & (not af.printed):
                        csvwriter.writerow(af.to_list())
                        af.printed = True
        tmpfile.close()
        try:
            os.startfile(tmpfile.name)  # Windows only
        except BaseException:
            subprocess.call(("open", tmpfile.name))  # macOS
        return None

    else:
        output = ""
        output += ",".join(AudioFile.OUTPUT_VALS) + "\n"
        for af in episode.audio_files:
            output += str(af) + "\n"
            af.printed = True
        return output


def conform_report(episode):
    # see if we can match every conformed shot to a story shot.
    # if we can't let the user know about it.

    # unmatched_shots = 0
    boarded_shots = 0
    cg_shots = 0
    output = ""

    for cshot in episode.cshots:
        matched = []
        for sshot in episode.sshots:
            result = cshot.match(sshot)
            if result == "perfect":
                matched.append(sshot)
                cshot.matched_shot = sshot
                continue
            elif result == "close":
                matched.append(sshot)
                cshot.matched_shot = sshot

        if len(matched) == 0:
            boarded_shots += 1
            output += f"Warning: Conformed shot {cshot.name()} doesn't have a matching unreal shot.\n"
        else:
            cg_shots += 1
            for m in matched:
                mtype = cshot.match(m)
                if mtype != "perfect":
                    output += f"Possible conform mismatch detected:\n\t{cshot}\n\t{m}\n"

    output += "\n"

    # check to make sure we have consecutive scenes.
    sorted_scenes = [s.name() for s in episode.scenes]
    sorted_scenes.sort()
    if len(sorted_scenes) > 0:
        last_scene = sorted_scenes[0]
        for scene in sorted_scenes[1:]:
            if last_scene == scene:
                output += f"SCENE BURNIN WARNING: scene {last_scene} burnin exists multiple times\n"
            # TODO: Can't do this one because we're losing the idea that scene names must be numbers.
            # elif last_scene + 1 < scene:
            #    output += f"SCENE BURNIN WARNING: scene burnin may be missing between {last_scene} and {scene}\n"
            last_scene = scene

    output += "\n"

    # now check each sequence for consecutive shots (looking for skipped burnins)
    # how to do this? Is this still a #TODO?

    # check each scene for consecutive shots (aka look for skipped burnins)
    # TODO: either figure out a way to include the A, B, C shot logic or remove this entirely.

    for scene in episode.scenes:
        shotlist = []
        for cshot in episode.cshots:
            if cshot.container == scene:
                shotlist.append(cshot.name())

        # report the count, that's useful, and name the first and last shots too
        shotlist.sort()

        output += (
            f"Conform scene {scene.name()} has {len(shotlist)} shot"
            + ("s" if len(shotlist) != 1 else "")
            + ":"
        )
        output += "\n" + "\t".join([f"{shot}" for shot in shotlist]) + "\n"

        """
        # we have a sorted list of shot names. Let's go through them in order, see what their CG
        # counterpart is, and flag consecutive duplicates.
        # This code is ugly, I'm sorry. If you're reading this, forgive me. It's production code.
        last_cg_shot = "boarded"
        for cshotname in shotlist:
            this_shot = None
            for cshot in episode.cshots:
                if cshotname == cshot.name:
                    this_shot = cshot
                    break
            if this_shot is None:
                output += f"Error: couldn't find shot {cshotname} in cshot list. Shouldn't be possible \n"
                continue
            if this_shot.matched_shot is None:
                last_cg_shot = "boarded"
                continue
            # if we're here we have a real CG shot, let's compare names.
            if last_cg_shot == this_shot.matched_shot.name:
                output += f"WARNING: shot {cshot.name} references same CG shot ({this_shot.matched_shot.name}) as the previous shot.\n"
            last_cg_shot = this_shot.matched_shot.name
        """
    return output


def cgfixes_report(episode):
    # this report is to loop over all shots, identify those with editorial fx and print them
    # ideally in an easy-to-use CSV style

    # TODO: do we need/want the CSV aspect of this?

    # want to sort this list by starting frame
    episode.sshots.sort(key=lambda x: x.sf)

    # for CSV-type reporting:
    # initial_output = "Shot,Fix Type,Report Text\n"
    initial_output = ""
    output = initial_output
    lastshotname = None
    last_ef = None
    for shot in episode.sshots:
        if shot.name() == lastshotname and last_ef == shot.sf:  # check for frame parity
            output += f"Warning: {lastshotname} appears back to back in the edit. This may be fine if it's a cut, but worth checking.\n"
            # output += f"{lastshotname},CG Conform,appears back to back\n"
        lastshotname = shot.name()
        last_ef = shot.ef

    for shot in episode.sshots:
        if shot.has_fx():
            output += (
                # f"{shot.name()},CG Conform, {shot.fx_str()}\n"
                f"Warning: {shot.name()} has editorial FX applied that may need CG fixes: {shot.fx_str()}\n"
            )
    if output == initial_output:
        return "No CG fixes found!"
    return output
