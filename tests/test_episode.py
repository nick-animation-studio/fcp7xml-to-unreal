import os

from fcp7xml_to_unreal import config
from fcp7xml_to_unreal.models.Episode import Episode


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
            <name>scene_001.png</name>
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
            <name>shot_005.png</name>
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


def test_episode_parses_audio_and_shots(tmp_path):
    xmlfile = make_xml(tmp_path)

    ep = Episode(xmlfile)

    # audio: should have created one AudioFile and track name
    assert len(ep.audio_files) == 1
    assert "MusicMain" in ep.track_names
    af = ep.audio_files[0]
    assert af.filename == "audio1"
    assert af.masterclipid == "mc1"
    # label comes from config mapping for 'yellow'
    assert af.trackcolor == "yellow"
    assert af.label is not None

    # video: should have created one scene and one cshot mapped to it
    assert len(ep.scenes) == 1
    assert len(ep.cshots) == 1
    cshot = ep.cshots[0]
    assert cshot.name() == "001_005"
    assert ep.scenes[0].name() == "001"
    # name should have been rewritten to include scene prefix
    assert "_" in cshot.name()


def test_episode_write_filtered(tmp_path):
    xmlfile = make_xml(tmp_path)

    ep = Episode(xmlfile)
    ep.write_filtered()

    # Check if the filtered file is created
    filtered_file = xmlfile[:-4] + "_filtered.xml"
    assert os.path.exists(filtered_file)  # Ensure the filtered file exists

    # Clean up the created file
    os.remove(filtered_file)


def test_episode_removes_disabled_video_tracks(tmp_path):
    content = """
<root>
  <sequence>
    <media>
      <video>
        <track>
          <enabled>FALSE</enabled>
          <clipitem>
            <enabled>TRUE</enabled>
            <name>scene_001.png</name>
            <start>0</start>
            <end>100</end>
            <in>0</in>
            <out>100</out>
          </clipitem>
        </track>
        <track>
          <enabled>TRUE</enabled>
          <clipitem>
            <enabled>TRUE</enabled>
            <name>scene_002.png</name>
            <start>100</start>
            <end>200</end>
            <in>100</in>
            <out>200</out>
          </clipitem>
        </track>
      </video>
      <audio/>
    </media>
  </sequence>
</root>
"""
    p = tmp_path / "test_disabled_tracks.xml"
    p.write_text(content)

    ep = Episode(str(p))
    assert len(ep.scenes) == 1
    assert ep.scenes[0].name() == "002"


def test_episode_removes_disabled_clips(tmp_path):
    content = """
<root>
  <sequence>
    <media>
      <video>
        <track>
          <enabled>TRUE</enabled>
          <clipitem>
            <enabled>FALSE</enabled>
            <name>scene_001.png</name>
            <start>0</start>
            <end>100</end>
            <in>0</in>
            <out>100</out>
          </clipitem>
          <clipitem>
            <enabled>TRUE</enabled>
            <name>scene_002.png</name>
            <start>100</start>
            <end>200</end>
            <in>100</in>
            <out>200</out>
          </clipitem>
        </track>
      </video>
      <audio/>
    </media>
  </sequence>
</root>
"""
    p = tmp_path / "test_disabled_clips.xml"
    p.write_text(content)

    ep = Episode(str(p))
    assert len(ep.scenes) == 1
    assert ep.scenes[0].name() == "002"


def test_is_movie_file(tmp_path):
    xmlfile = make_xml(tmp_path)
    ep = Episode(xmlfile)

    assert ep.is_movie_file("video.mov") is True
    assert ep.is_movie_file("image.png") is False
    assert ep.is_movie_file("file.mp4") is False


def test_is_image_file(tmp_path):
    xmlfile = make_xml(tmp_path)
    ep = Episode(xmlfile)

    assert ep.is_image_file("frame.png") is True
    assert ep.is_image_file("photo.jpg") is True
    assert ep.is_image_file("clip.mov") is False


def test_is_conformshot_burnin(tmp_path):
    xmlfile = make_xml(tmp_path)
    ep = Episode(xmlfile)

    assert ep.is_conformshot_burnin("shot_001") is True
    assert ep.is_conformshot_burnin("scene_001") is False
    assert ep.is_conformshot_burnin("other_001") is False


def test_is_conformscene_burnin(tmp_path):
    xmlfile = make_xml(tmp_path)
    ep = Episode(xmlfile)

    assert ep.is_conformscene_burnin("scene_001") is True
    assert ep.is_conformscene_burnin("shot_001") is False
    assert ep.is_conformscene_burnin("other_001") is False


def test_audio_missing_masterclipid(tmp_path):
    content = """
<root>
  <sequence>
    <media>
      <audio>
        <track MZ.TrackName="SFXTrack">
          <clipitem>
            <enabled>TRUE</enabled>
            <name>sound1</name>
            <file>
              <pathurl>file://sound.wav</pathurl>
            </file>
            <start>0</start>
            <end>100</end>
            <labels>
              <label2>brown</label2>
            </labels>
            <filter>
              <effect>
                <name>compression</name>
              </effect>
            </filter>
          </clipitem>
        </track>
      </audio>
      <video/>
    </media>
  </sequence>
</root>
"""
    p = tmp_path / "test_audio_nomcid.xml"
    p.write_text(content)

    ep = Episode(str(p))
    assert len(ep.audio_files) == 1
    assert ep.audio_files[0].masterclipid == "undefined"


def test_audio_with_transition_start(tmp_path):
    content = """
<root>
  <sequence>
    <media>
      <audio>
        <track MZ.TrackName="AudioTrack">
          <transitionitem>
            <start>0</start>
            <end>100</end>
          </transitionitem>
          <clipitem>
            <enabled>TRUE</enabled>
            <name>audio_with_transition</name>
            <masterclipid>mc1</masterclipid>
            <file>
              <pathurl>file://audio.wav</pathurl>
            </file>
            <start>-1</start>
            <end>200</end>
            <labels>
              <label2>yellow</label2>
            </labels>
          </clipitem>
        </track>
      </audio>
      <video/>
    </media>
  </sequence>
</root>
"""
    p = tmp_path / "test_audio_transition_start.xml"
    p.write_text(content)

    ep = Episode(str(p))
    assert len(ep.audio_files) == 1
    assert ep.audio_files[0].sf == 0


def test_audio_with_transition_end(tmp_path):
    content = """
<root>
  <sequence>
    <media>
      <audio>
        <track MZ.TrackName="AudioTrack">
          <clipitem>
            <enabled>TRUE</enabled>
            <name>audio_with_transition</name>
            <masterclipid>mc1</masterclipid>
            <file>
              <pathurl>file://audio.wav</pathurl>
            </file>
            <start>100</start>
            <end>-1</end>
            <labels>
              <label2>yellow</label2>
            </labels>
          </clipitem>
          <transitionitem>
            <start>300</start>
            <end>400</end>
          </transitionitem>
        </track>
      </audio>
      <video/>
    </media>
  </sequence>
</root>
"""
    p = tmp_path / "test_audio_transition_end.xml"
    p.write_text(content)

    ep = Episode(str(p))
    assert len(ep.audio_files) == 1
    assert ep.audio_files[0].ef == 400


def test_audio_files_deduplication(tmp_path):
    content = """
<root>
  <sequence>
    <media>
      <audio>
        <track MZ.TrackName="AudioTrack">
          <clipitem>
            <enabled>TRUE</enabled>
            <name>audio1</name>
            <masterclipid>mc1</masterclipid>
            <file>
              <pathurl>file://audio.wav</pathurl>
            </file>
            <start>0</start>
            <end>100</end>
            <labels>
              <label2>yellow</label2>
            </labels>
          </clipitem>
          <clipitem>
            <enabled>TRUE</enabled>
            <name>audio1</name>
            <masterclipid>mc1</masterclipid>
            <file>
              <pathurl>file://audio.wav</pathurl>
            </file>
            <start>0</start>
            <end>100</end>
            <labels>
              <label2>yellow</label2>
            </labels>
          </clipitem>
        </track>
      </audio>
      <video/>
    </media>
  </sequence>
</root>
"""
    p = tmp_path / "test_audio_dedup.xml"
    p.write_text(content)

    ep = Episode(str(p))
    assert len(ep.audio_files) == 1


def test_movie_file_invalid_shot_naming(tmp_path):
    content = """
<root>
  <sequence>
    <media>
      <video>
        <track>
          <enabled>TRUE</enabled>
          <clipitem>
            <enabled>TRUE</enabled>
            <name>invalid_clip.mov</name>
            <start>0</start>
            <end>100</end>
            <in>0</in>
            <out>100</out>
          </clipitem>
          <clipitem>
            <enabled>TRUE</enabled>
            <name>001_TEST_shot_A.mov</name>
            <start>100</start>
            <end>200</end>
            <in>100</in>
            <out>200</out>
          </clipitem>
        </track>
      </video>
      <audio/>
    </media>
  </sequence>
</root>
"""
    p = tmp_path / "test_movie_naming.xml"
    p.write_text(content)

    ep = Episode(str(p))
    assert len(ep.sshots) == 1
    assert "001" in ep.sshots[0].name()


def test_movie_file_both_transitions(tmp_path):
    content = """
<root>
  <sequence>
    <media>
      <video>
        <track>
          <enabled>TRUE</enabled>
          <clipitem>
            <enabled>TRUE</enabled>
            <name>001_TEST_shot_A.mov</name>
            <start>-1</start>
            <end>-1</end>
            <in>0</in>
            <out>100</out>
          </clipitem>
        </track>
      </video>
      <audio/>
    </media>
  </sequence>
</root>
"""
    p = tmp_path / "test_both_transitions.xml"
    p.write_text(content)

    ep = Episode(str(p))
    assert len(ep.sshots) == 0
    assert "Check for transitions" in ep.ingest_log


def test_movie_file_transition_start_only(tmp_path):
    content = """
<root>
  <sequence>
    <media>
      <video>
        <track>
          <enabled>TRUE</enabled>
          <clipitem>
            <enabled>TRUE</enabled>
            <name>001_TEST_shot_A.mov</name>
            <start>-1</start>
            <end>100</end>
            <in>0</in>
            <out>100</out>
          </clipitem>
        </track>
      </video>
      <audio/>
    </media>
  </sequence>
</root>
"""
    p = tmp_path / "test_transition_start.xml"
    p.write_text(content)

    ep = Episode(str(p))
    assert len(ep.sshots) == 1
    assert "Auto-fixed shot" in ep.ingest_log


def test_movie_file_transition_end_only(tmp_path):
    content = """
<root>
  <sequence>
    <media>
      <video>
        <track>
          <enabled>TRUE</enabled>
          <clipitem>
            <enabled>TRUE</enabled>
            <name>001_TEST_shot_A.mov</name>
            <start>0</start>
            <end>-1</end>
            <in>0</in>
            <out>100</out>
          </clipitem>
        </track>
      </video>
      <audio/>
    </media>
  </sequence>
</root>
"""
    p = tmp_path / "test_transition_end.xml"
    p.write_text(content)

    ep = Episode(str(p))
    assert len(ep.sshots) == 1
    assert "Auto-fixed shot" in ep.ingest_log


def test_movie_file_timeremap_reverse(tmp_path):
    content = """
<root>
  <sequence>
    <media>
      <video>
        <track>
          <enabled>TRUE</enabled>
          <clipitem>
            <enabled>TRUE</enabled>
            <name>001_TEST_shot_A.mov</name>
            <start>0</start>
            <end>100</end>
            <in>0</in>
            <out>100</out>
            <filter>
              <effect>
                <effectid>timeremap</effectid>
                <parameter>
                  <parameterid>reverse</parameterid>
                  <value>TRUE</value>
                </parameter>
                <parameter>
                  <parameterid>speed</parameterid>
                  <value>100</value>
                </parameter>
              </effect>
            </filter>
          </clipitem>
        </track>
      </video>
      <audio/>
    </media>
  </sequence>
</root>
"""
    p = tmp_path / "test_timeremap_reverse.xml"
    p.write_text(content)

    ep = Episode(str(p))
    assert len(ep.sshots) == 1
    assert len(ep.fx_shots) == 1
    shot = ep.sshots[0]
    assert "timeremap" in shot.fx
    assert "reverse" in shot.fx["timeremap"]
    assert shot.fx["timeremap"]["reverse"] == "TRUE"
    assert "speed" not in shot.fx["timeremap"]


def test_movie_file_timeremap_with_graphdict(tmp_path):
    content = """
<root>
  <sequence>
    <media>
      <video>
        <track>
          <enabled>TRUE</enabled>
          <clipitem>
            <enabled>TRUE</enabled>
            <name>001_TEST_shot_A.mov</name>
            <start>0</start>
            <end>100</end>
            <in>0</in>
            <out>100</out>
            <filter>
              <effect>
                <effectid>timeremap</effectid>
                <parameter>
                  <parameterid>reverse</parameterid>
                  <value>FALSE</value>
                </parameter>
                <parameter>
                  <parameterid>speed</parameterid>
                  <value>100</value>
                </parameter>
                <parameter>
                  <parameterid>graphdict</parameterid>
                  <keyframe>
                    <when>0</when>
                    <value>0</value>
                  </keyframe>
                  <keyframe>
                    <when>50</when>
                    <value>25</value>
                  </keyframe>
                  <keyframe>
                    <when>100</when>
                    <value>100</value>
                  </keyframe>
                </parameter>
              </effect>
            </filter>
          </clipitem>
        </track>
      </video>
      <audio/>
    </media>
  </sequence>
</root>
"""
    p = tmp_path / "test_timeremap_graphdict.xml"
    p.write_text(content)

    ep = Episode(str(p))
    assert len(ep.fx_shots) == 1
    shot = ep.sshots[0]
    assert "timeremap" in shot.fx
    assert "graphdict" in shot.fx["timeremap"]
    assert "(f0 @ f0)" in shot.fx["timeremap"]["graphdict"]


def test_movie_file_basic_scale_effect(tmp_path):
    content = """
<root>
  <sequence>
    <media>
      <video>
        <track>
          <enabled>TRUE</enabled>
          <clipitem>
            <enabled>TRUE</enabled>
            <name>001_TEST_shot_A.mov</name>
            <start>0</start>
            <end>100</end>
            <in>0</in>
            <out>100</out>
            <filter>
              <effect>
                <effectid>basic</effectid>
                <parameter>
                  <parameterid>scale</parameterid>
                  <value>150</value>
                </parameter>
                <parameter>
                  <parameterid>rotation</parameterid>
                  <value>0</value>
                </parameter>
              </effect>
            </filter>
          </clipitem>
        </track>
      </video>
      <audio/>
    </media>
  </sequence>
</root>
"""
    p = tmp_path / "test_basic_scale.xml"
    p.write_text(content)

    ep = Episode(str(p))
    assert len(ep.fx_shots) == 1
    shot = ep.sshots[0]
    assert "basic" in shot.fx
    assert "scale" in shot.fx["basic"]
    assert shot.fx["basic"]["scale"] == "150"
    assert "rotation" not in shot.fx["basic"]


def test_movie_file_basic_rotation_effect(tmp_path):
    content = """
<root>
  <sequence>
    <media>
      <video>
        <track>
          <enabled>TRUE</enabled>
          <clipitem>
            <enabled>TRUE</enabled>
            <name>001_TEST_shot_A.mov</name>
            <start>0</start>
            <end>100</end>
            <in>0</in>
            <out>100</out>
            <filter>
              <effect>
                <effectid>basic</effectid>
                <parameter>
                  <parameterid>rotation</parameterid>
                  <value>45</value>
                </parameter>
                <parameter>
                  <parameterid>scale</parameterid>
                  <value>100</value>
                </parameter>
              </effect>
            </filter>
          </clipitem>
        </track>
      </video>
      <audio/>
    </media>
  </sequence>
</root>
"""
    p = tmp_path / "test_basic_rotation.xml"
    p.write_text(content)

    ep = Episode(str(p))
    assert len(ep.fx_shots) == 1
    shot = ep.sshots[0]
    assert "rotation" in shot.fx["basic"]
    assert shot.fx["basic"]["rotation"] == "45"
    assert "scale" not in shot.fx["basic"]


def test_movie_file_basic_with_keyframes(tmp_path):
    content = """
<root>
  <sequence>
    <media>
      <video>
        <track>
          <enabled>TRUE</enabled>
          <clipitem>
            <enabled>TRUE</enabled>
            <name>001_TEST_shot_A.mov</name>
            <start>0</start>
            <end>100</end>
            <in>0</in>
            <out>100</out>
            <filter>
              <effect>
                <effectid>basic</effectid>
                <parameter>
                  <parameterid>scale</parameterid>
                  <keyframe>
                    <when>0</when>
                    <value>100</value>
                  </keyframe>
                  <keyframe>
                    <when>50</when>
                    <value>150</value>
                  </keyframe>
                </parameter>
              </effect>
            </filter>
          </clipitem>
        </track>
      </video>
      <audio/>
    </media>
  </sequence>
</root>
"""
    p = tmp_path / "test_basic_keyframes.xml"
    p.write_text(content)

    ep = Episode(str(p))
    assert len(ep.fx_shots) == 1
    shot = ep.sshots[0]
    assert "basic" in shot.fx
    assert "(f100 @ f0)" in shot.fx["basic"]["scale"]
    assert "(f150 @ f50)" in shot.fx["basic"]["scale"]


def test_image_non_burnin_removed(tmp_path):
    content = """
<root>
  <sequence>
    <media>
      <video>
        <track>
          <enabled>TRUE</enabled>
          <clipitem>
            <enabled>TRUE</enabled>
            <name>random_image.png</name>
            <start>0</start>
            <end>100</end>
            <in>0</in>
            <out>100</out>
            <rate>
              <timebase>30</timebase>
            </rate>
          </clipitem>
        </track>
      </video>
      <audio/>
    </media>
  </sequence>
</root>
"""
    p = tmp_path / "test_non_burnin.xml"
    p.write_text(content)

    ep = Episode(str(p))
    assert len(ep.scenes) == 0
    assert len(ep.cshots) == 0


def test_image_timebase_updated(tmp_path):
    content = """
<root>
  <sequence>
    <media>
      <video>
        <track>
          <enabled>TRUE</enabled>
          <clipitem>
            <enabled>TRUE</enabled>
            <name>scene_001.png</name>
            <start>0</start>
            <end>100</end>
            <in>0</in>
            <out>100</out>
            <rate>
              <timebase>30</timebase>
            </rate>
          </clipitem>
        </track>
      </video>
      <audio/>
    </media>
  </sequence>
</root>
"""
    p = tmp_path / "test_timebase.xml"
    p.write_text(content)

    ep = Episode(str(p))
    timebase = ep.root.find(".//rate/timebase").text
    assert timebase == config["frame_rate"]


def test_cshot_not_in_any_scene(tmp_path):
    content = """
<root>
  <sequence>
    <media>
      <video>
        <track>
          <enabled>TRUE</enabled>
          <clipitem>
            <enabled>TRUE</enabled>
            <name>scene_001.png</name>
            <start>0</start>
            <end>50</end>
            <in>0</in>
            <out>50</out>
          </clipitem>
          <clipitem>
            <enabled>TRUE</enabled>
            <name>shot_100.png</name>
            <start>500</start>
            <end>600</end>
            <in>500</in>
            <out>600</out>
          </clipitem>
        </track>
      </video>
      <audio/>
    </media>
  </sequence>
</root>
"""
    p = tmp_path / "test_uncontained.xml"
    p.write_text(content)

    ep = Episode(str(p))
    assert len(ep.cshots) == 1
    assert ep.cshots[0].container is None
    assert "not contained in any scene" in ep.ingest_log


def test_story_shot_not_in_any_scene(tmp_path):
    content = """
<root>
  <sequence>
    <media>
      <video>
        <track>
          <enabled>TRUE</enabled>
          <clipitem>
            <enabled>TRUE</enabled>
            <name>scene_001.png</name>
            <start>0</start>
            <end>100</end>
            <in>0</in>
            <out>100</out>
          </clipitem>
          <clipitem>
            <enabled>TRUE</enabled>
            <name>001_TEST_shot_A.mov</name>
            <start>500</start>
            <end>600</end>
            <in>500</in>
            <out>600</out>
          </clipitem>
        </track>
      </video>
      <audio/>
    </media>
  </sequence>
</root>
"""
    p = tmp_path / "test_story_uncontained.xml"
    p.write_text(content)

    ep = Episode(str(p))
    assert len(ep.sshots) == 1
    assert "is not in any scene" in ep.ingest_log


def test_audio_track_without_name_attribute(tmp_path):
    content = """
<root>
  <sequence>
    <media>
      <audio>
        <track>
          <clipitem>
            <enabled>TRUE</enabled>
            <name>audio1</name>
            <masterclipid>mc1</masterclipid>
            <file>
              <pathurl>file://audio.wav</pathurl>
            </file>
            <start>0</start>
            <end>100</end>
            <labels>
              <label2>yellow</label2>
            </labels>
          </clipitem>
        </track>
      </audio>
      <video/>
    </media>
  </sequence>
</root>
"""
    p = tmp_path / "test_audio_noname.xml"
    p.write_text(content)

    ep = Episode(str(p))
    assert len(ep.audio_files) == 1
    assert ep.audio_files[0].trackname == "undefined"
    assert "undefined" not in ep.track_names
