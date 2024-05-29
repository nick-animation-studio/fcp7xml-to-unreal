def frames_to_TC(frames):
    if frames == -1:
        return "N/A"
    frames += 86160
    h = int(frames / 86400)
    m = int(frames / 1440) % 60
    s = int((frames % 1440) / 24)
    f = frames % 1440 % 24
    return "%02d:%02d:%02d:%02d" % (h, m, s, f)
