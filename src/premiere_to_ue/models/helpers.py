from premiere_to_ue import logger


def tc_to_frames(tc="00:59:50:00"):
    # tc is in the following format:
    # HH:MM:SS:FF

    (hours, minutes, seconds, frames) = [int(c) for c in tc.split(":", 3)]

    if (frames < 0) | (frames > 23):
        logger.error(f"Timecode error: illegal frame value in {tc}")
        return -1
    if (seconds < 0) | (seconds > 59):
        logger.error(f"Timecode error: illegal seconds value in {tc}")
        return -1
    if (minutes < 0) | (minutes > 59):
        logger.error(f"Timecode error: illegal minutes value in {tc}")
        return -1

    return frames + 24 * seconds + 24 * 60 * minutes + 24 * 60 * 60 * hours


def frames_to_tc(frame, for_srt=False, additional_frames: int = 0):
    # Add 00:59:50:00 offset
    if frame is None:
        return "00:59:50:00"
    else:
        frame = int(frame) + additional_frames
    frame = frame + (59 * 60 * 24) + (50 * 24)
    h = int(frame / 86400)
    m = int(frame / 1440) % 60
    s = int((frame % 1440) / 24)
    f = frame % 1440 % 24
    if not for_srt:
        return f"{h:02d}:{m:02d}:{s:02d}:{f:02d}"
    else:
        ms = int(f / 24 * 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
