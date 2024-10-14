import csv
import os
import subprocess
import tempfile

from matm.Audio import AudioFile


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
                    af.shotlist.append(cshot.name)

    # now write out

    if to_csv:
        tmpfile = tempfile.NamedTemporaryFile(suffix=".csv", delete=False)
        with open(tmpfile.name, "w", newline="") as writefile:
            csvwriter = csv.writer(
                writefile, dialect="excel", quoting=csv.QUOTE_MINIMAL
            )
            csvwriter.writerow(episode.audio_files[0].dump_header())
            for tn in episode.track_names:
                for af in episode.audio_files:
                    if (af.trackname == tn) & (af.printed == False):
                        csvwriter.writerow(af.to_list())
                        af.printed = True
        tmpfile.close()
        try:
            os.startfile(tmpfile.name)
        except:
            subprocess.call(("open", tmpfile.name))
        return None

    else:
        output = ""
        output += ",".join(AudioFile.OUTPUT_VALS) + "\n"
        for af in episode.audio_files:
            output += str(af) + "\n"
            af.printed = True
        return output


def cgfixes_report(episode):
    # this report is to loop over all shots, identify those with fx and print them
    # ideally in an easy-to-use CSV style

    # want to sort this list by starting frame
    episode.sshots.sort(key=lambda x: x.sf)
    output = ""
    lastshot = None
    last_ef = None
    for shot in episode.sshots:
        if shot.name == lastshot:
            # check for frame parity
            if last_ef == shot.sf:
                output += f"{shot.name[:-4]}, appears back to back\n"
        lastshot = shot.name
        last_ef = shot.ef

    for shot in episode.sshots:
        if shot.name.split(".")[0].split("_")[-1].isdigit():
            output += f"{shot.name[:-4]}, likely versioned incorrectly in premiere\n"

    for shot in episode.sshots:
        if shot.has_fx():
            output += f"{shot.name[:-4]},{shot.fx_str()}\n"
    return output


def conform_report(episode):
    # this report should flag any odd conform boundary issues
    # now validate. Go over each cshot looking for matches in the sshots

    boarded_shots = 0
    cg_shots = 0
    output = ""

    # map cshots to their sequences
    for cshot in episode.cshots:
        in_seq = False
        for seq in episode.seqs:
            if seq.contains(cshot):
                in_seq = True
                continue
        if in_seq == False:
            output += f"Shot {cshot.name} not in any sequence!\n"
                
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
            else:
                pass

        if len(matched) == 0:
            boarded_shots += 1
        else:
            cg_shots += 1
            for m in matched:
                mtype = cshot.match(m)
                if mtype != "perfect":
                    output += f"Conform mismatch detected:\n\t{cshot}\n\t{m}\n"

    # check to make sure we have consecutive scenes.
    sorted_seqs = [int(s.name[3:-4]) for s in episode.seqs]
    sorted_seqs.sort()
    if len(sorted_seqs) > 0:
        last_seq = sorted_seqs[0]
        for seq in sorted_seqs[1:]:
            if last_seq == seq:
                output += f"SCENE BURNIN WARNING: scene {last_seq} burnin exists multiple times\n"
            elif last_seq +1 < seq:
                output += f"SCENE BURNIN WARNING: scene burnin may be missing between {last_seq} and {seq}\n"
            last_seq = seq

    # now check each sequence for consecutive shots (looking for skipped burnins)
    # how to do this? Is this still a #TODO?

    for seq in episode.seqs:
        shotlist = []
        for cshot in episode.cshots:
            if cshot.seq == seq.name:
                # ignore A, B, etc shots for counting purposes
                if len(cshot.name) == 6:
                    shotlist.append(cshot.name)
        shotlist.sort()

        last_shot_num = int(shotlist[-1][-3:])
        if last_shot_num != len(shotlist):
            output += f"SHOT COUNT WARNING: sequence {seq.name}!\n"
            output += shotlist + "\n"

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
            if this_shot == None:
                output += f"Error: couldn't find shot {cshotname} in cshot list. Shouldn't be possible \n"
                continue
            if this_shot.matched_shot == None:
                last_cg_shot = "boarded"
                continue
            # if we're here we have a real CG shot, let's compare names.
            if last_cg_shot == this_shot.matched_shot.name:
                output += f"WARNING: shot {cshot.name} references same CG shot ({this_shot.matched_shot.name}) as the previous shot.\n"
            last_cg_shot = this_shot.matched_shot.name
    return output
