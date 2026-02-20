"""Unit tests for the AudioFile model."""

from urllib.parse import unquote

from fcp7xml_to_unreal.models.Audio import AudioFile
from fcp7xml_to_unreal.models.helpers import frames_to_tc


def test_initialization_and_label():
    af = AudioFile(
        filename="myfile.wav",
        path="/some%20path/myfile.wav",
        masterclipid="MC123",
        startFrame=0,
        endFrame=24,
        trackName="A1",
        trackColor="Brown",
    )

    # path should be unquoted
    assert af.path == unquote("/some%20path/myfile.wav")
    assert af.filename == "myfile.wav"
    assert af.masterclipid == "MC123"

    # start/end frame numeric storage
    assert af.sf == 0
    assert af.ef == 24

    # starttime/endtime should use frames_to_tc
    assert af.starttime == frames_to_tc(0)
    assert af.endtime == frames_to_tc(24)

    # label should be taken from config track_colors via lowercase match
    assert af.label is not None


def test_is_music_sfx_dialogue():
    music = AudioFile(
        "m.wav", "/p", "mc", 0, 1, trackName="Music_Main", trackColor="yellow"
    )
    sfx = AudioFile("s.wav", "/p", "mc", 0, 1, trackName="SFX_01", trackColor="yellow")
    dialog = AudioFile("d.wav", "/p", "mc", 0, 1, trackName="VO_A", trackColor="yellow")

    assert music.is_music()
    assert not music.is_sfx()

    assert sfx.is_sfx()
    assert not sfx.is_music()

    assert dialog.is_dialogue()
    assert not dialog.is_music()
    assert not dialog.is_sfx()


def test_to_list_str_and_eq():
    a1 = AudioFile("f.wav", "/p", "mc", 10, 20, trackName="Track", trackColor="yellow")
    a2 = AudioFile("f.wav", "/p", "mc", 10, 20, trackName="Track", trackColor="yellow")
    a3 = AudioFile("f2.wav", "/p", "mc", 10, 21, trackName="Track", trackColor="yellow")

    audio_as_list = a1.to_list()
    # ensure output list matches declared OUTPUT_VALS length
    assert isinstance(audio_as_list, list)
    assert len(audio_as_list) == len(AudioFile.OUTPUT_VALS)

    s = str(a1)
    assert "," in s

    assert a1 == a2
    assert a1 != a3


def test_badTC_flag():
    bad1 = AudioFile("f.wav", "/p", "mc", -1, 10, trackName="T", trackColor="yellow")
    bad2 = AudioFile("f.wav", "/p", "mc", 1, -1, trackName="T", trackColor="yellow")
    good = AudioFile("f.wav", "/p", "mc", 1, 2, trackName="T", trackColor="yellow")

    assert bad1.badTC
    assert bad2.badTC
    assert not good.badTC
