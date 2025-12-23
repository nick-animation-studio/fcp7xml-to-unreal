from premiere_to_ue.models.Audio import AudioFile
from premiere_to_ue.models.Shot import Shot
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
        self.seqs = []


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
    s = Shot("001_005", 12, 30, 0, 0)
    ep.cshots = [s]

    out = audio_report(ep, to_csv=False)
    assert ",".join(AudioFile.OUTPUT_VALS) in out
    # af_no_path should receive the master clip path from af_with_path
    assert af_no_path.path == af_with_path.path
    # dialogue detection should add overlapping shot name to shotlist
    assert s.name in af_no_path.shotlist


def test_cgfixes_report_no_fx_and_with_fx():
    ep = SimpleEpisode()
    # no sshots -> no fixes
    ep.sshots = []
    assert cgfixes_report(ep) == "No cg fixes found!"

    # with a shot that has fx
    s = Shot("001_001.png", 1, 2, 0, 0)
    s.add_fx("basic", {"scale": "50"})
    ep.sshots = [s]
    out = cgfixes_report(ep)
    assert "FX: basic" in out or "basic" in out


def test_conform_report_reports_unmatched_and_scene_warnings():
    ep = SimpleEpisode()

    # create seqs that are non-consecutive to trigger scene burnin warning
    class Seq:
        def __init__(self, name):
            self.name = name

    ep.seqs = [Seq("seq001.png"), Seq("seq003.png")]

    # unmatched cshot
    c_unmatched = Shot("c_un", 1, 2, 0, 0)
    # add a cshot that is mapped to seq001.png and has a 6-char name so conform_report
    # can build a shotlist without raising an IndexError
    c_for_seq = Shot("S01001", 1, 2, 0, 0)
    c_for_seq.seq = "seq001.png"
    c_for_seq2 = Shot("S02002", 1, 2, 0, 0)
    c_for_seq2.seq = "seq003.png"
    ep.cshots = [c_unmatched, c_for_seq, c_for_seq2]

    # no story shots to match => should warn about boarded shot
    out = conform_report(ep)
    assert "doesn't match any story shot" in out
    assert "SCENE BURNIN WARNING" in out
