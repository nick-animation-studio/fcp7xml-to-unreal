from fcp7xml_to_unreal.models import helpers


def test_tc_to_frames_valid():
    assert helpers.tc_to_frames("00:00:00:00") == 0
    assert helpers.tc_to_frames("00:00:00:01") == 1
    # one second = 24 frames
    assert helpers.tc_to_frames("00:00:01:00") == 24
    # one minute = 24*60 frames
    assert helpers.tc_to_frames("00:01:00:00") == 24 * 60


def test_tc_to_frames_invalid_values(caplog):
    # invalid frames (>23)
    assert helpers.tc_to_frames("00:00:00:24") == -1
    assert "Timecode error" in caplog.text

    # invalid seconds
    assert helpers.tc_to_frames("00:00:60:00") == -1
    # invalid minutes
    assert helpers.tc_to_frames("00:60:00:00") == -1


def test_frames_to_tc_none_and_basic():
    # None returns the offset TC
    assert helpers.frames_to_tc(None) == "00:59:50:00"

    # frame 0 also returns the offset TC
    assert helpers.frames_to_tc(0) == "00:59:50:00"


def test_frames_to_tc_additional_frames_and_rounding():
    # additional_frames should increment the final frame value
    assert helpers.frames_to_tc(1, additional_frames=1) == "00:59:50:02"

    # for_srt formatting uses comma and milliseconds (frame 0 -> ,000)
    srt = helpers.frames_to_tc(0, for_srt=True)
    assert srt.startswith("00:59:50,")
    assert srt.endswith(",000")
