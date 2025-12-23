from premiere_to_ue.models.Episode import Episode
from premiere_to_ue.models.Note import Note


def make_xml(tmp_path):
    content = """
<root>
  <sequence>
    <media>
      <video>
        <track>
          <enabled>TRUE</enabled>
          <clipitem>
            <enabled>TRUE</enabled>
            <name>seq001.png</name>
            <start>0</start>
            <end>100</end>
            <in>0</in>
            <out>100</out>
            <filter>
              <effect>
                <effectid>GraphicAndType</effectid>
                <name>Test note #tag1</name>
              </effect>
            </filter>
          </clipitem>
          <clipitem>
            <enabled>TRUE</enabled>
            <name>Sc_005.png</name>
            <start>10</start>
            <end>20</end>
            <in>10</in>
            <out>20</out>
          </clipitem>
        </track>
      </video>
      <audio>
        <track MZ.TrackName="MusicMain">
          <enabled>TRUE</enabled>
          <clipitem>
            <enabled>TRUE</enabled>
            <name>audio1</name>
            <masterclipid>mc1</masterclipid>
            <file>
              <pathurl>file://localhost/C:/audio/file.wav</pathurl>
            </file>
            <start>0</start>
            <end>10</end>
            <labels>
              <label2>yellow</label2>
            </labels>
            <filter>
              <effect>
                <name>reverb</name>
              </effect>
            </filter>
          </clipitem>
        </track>
      </audio>
    </media>
  </sequence>
</root>
"""

    p = tmp_path / "test_ep.xml"
    p.write_text(content)
    return str(p)


def test_episode_parses_notes_audio_and_shots(tmp_path):
    xmlfile = make_xml(tmp_path)

    ep = Episode(xmlfile)

    # notes: the GraphicAndType effect should produce one Note
    assert len(ep.notes) == 1
    note = ep.notes[0]
    assert isinstance(note, Note)
    assert note.tags == ["#tag1"]
    assert "Test note" in note.text

    # audio: should have created one AudioFile and track name
    assert len(ep.audio_files) == 1
    assert "MusicMain" in ep.track_names
    af = ep.audio_files[0]
    assert af.filename == "audio1"
    assert af.masterclipid == "mc1"
    # label comes from config mapping for 'yellow'
    assert af.trackcolor == "yellow"
    assert af.label is not None

    # video: should have created one sequence and one cshot mapped to it
    assert len(ep.seqs) == 1
    assert len(ep.cshots) == 1
    cshot = ep.cshots[0]
    assert cshot.seq == ep.seqs[0].name
    # name should have been rewritten to include sequence prefix
    assert "_" in cshot.name

    # write_filtered should produce an output string (even if no fx shots exist)
    out = ep.write_filtered()
    assert out.startswith("Check FX Shots:")
