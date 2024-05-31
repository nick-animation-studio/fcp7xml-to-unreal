from matm.Episode import Episode


def write_filtered(episode: Episode, xml_file):
    output = "Check FX Shots: \n"
    for shot in episode.fx_shots:
        output += str(shot) + "\n"
    outfile = xml_file[:-4] + "_filtered" + ".xml"
    episode.tree.write(outfile)
    return output
