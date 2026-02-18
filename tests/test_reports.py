from premiere_to_ue.models.Audio import AudioFile
from premiere_to_ue.models.Shot import ConformScene, ConformShot, UnrealShot
from premiere_to_ue.xml_helpers.reports import (
    audio_report,
    cgfixes_report,
    conform_report,
)


class SimpleEpisode:
    def __init__(self):
        self.audio_files = []
        self.track_names = []
        self.cshots = []
        self.sshots = []
        self.scenes = []


def test_audio_report_assigns_master_path_and_detects_shots():
    ep = SimpleEpisode()

    # create an audio file with path and another with same masterclipid but empty path
    af_with_path = AudioFile(
        "a1", "C:/audio/file.wav", "mc1", 10, 20, "Track1", "yellow"
    )
    af_no_path = AudioFile("a2", "", "mc1", 15, 25, "Track1", "yellow")
    ep.audio_files = [af_with_path, af_no_path]
    ep.track_names = ["Track1"]

    # create a shot that overlaps the second audio file
    s = ConformShot("001_005", 12, 30, 0, 0)
    # create a scene that overlaps the shot so it gets added to the audio file's shotlist
    scn = ConformScene("001", 0, 100, 0, 0)
    s.container = scn
    ep.scenes = [scn]
    ep.cshots = [s]

    out = audio_report(ep, to_csv=False)
    assert ",".join(AudioFile.OUTPUT_VALS) in out
    # af_no_path should receive the master clip path from af_with_path
    assert af_no_path.path == af_with_path.path
    # dialogue detection should add overlapping shot name to shotlist
    assert s.name() in af_no_path.shotlist


def test_cgfixes_report_no_fx_and_with_fx():
    ep = SimpleEpisode()
    # no sshots -> no fixes
    ep.sshots = []
    assert cgfixes_report(ep) == "No CG fixes found!"

    # with a shot that has fx
    s = UnrealShot("001_001.png", 1, 2, 0, 0)
    s.add_fx("basic", {"scale": "50"})
    ep.sshots = [s]
    out = cgfixes_report(ep)
    assert "FX: basic" in out or "basic" in out


def test_conform_report_unmatched_and_matched_shots():
    ep = SimpleEpisode()
    scn = ConformScene("scene_001", 0, 100, 0, 0)
    ep.scenes = [scn]
    nomatch_scn = ConformScene("scene_002", 0, 100, 0, 0)
    ep.scenes.append(nomatch_scn)
    # create a conformed shot with no matching scene shot
    cs_unmatched = ConformShot("shot_001", 10, 20, 0, 0)
    cs_unmatched.container = nomatch_scn
    ep.cshots = [cs_unmatched]

    out = conform_report(ep)
    assert "doesn't have a matching unreal shot" in out
    assert "No unmatched shots found!" not in out

    ushot = UnrealShot("shot_005", 12, 30, 0, 0)
    ep.sshots = [ushot]

    # now add a conformed shot that matches the Unreal shot and should be detected as a match
    s_matched = ConformShot("shot_005", 12, 30, 0, 0)
    s_matched.container = scn
    ep.cshots.append(s_matched)

    out = conform_report(ep)
    assert "Conform scene 001 has 1 shot:" in out
