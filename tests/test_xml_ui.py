import types

from premiere_to_ue import xml_ui as xu


class DummyStringVar:
    def __init__(self):
        self._val = ""

    def set(self, v):
        self._val = v

    def get(self):
        return self._val


class FakeButton:
    def __init__(self, frm=None, text=None, command=None):
        self.frm = frm
        self.text = text
        self.command = command
        self._state = None

    def grid(self, **kwargs):
        pass

    def config(self, state=None):
        self._state = state


def test_create_button_appends_and_disabled(monkeypatch):
    fakefrm = object()
    ui = xu.xmlUI(frm=fakefrm)

    # patch ttk.Button to our FakeButton
    monkeypatch.setattr(
        xu,
        "ttk",
        types.SimpleNamespace(
            Button=FakeButton, Frame=lambda *a, **k: None, Label=lambda *a, **k: None
        ),
    )

    ui.create_button("Label", lambda: None)
    assert len(ui.xml_functions) == 1
    btn = ui.xml_functions[0]
    assert isinstance(btn, FakeButton)
    # initially disabled
    assert btn._state == xu.DISABLED


def test_output_methods_call_show_output(monkeypatch):
    called = {}

    def fake_show_output(self, output):
        called["out"] = output

    monkeypatch.setattr(xu.xmlUI, "show_output", fake_show_output)

    # audio_report
    monkeypatch.setattr(xu, "audio_report", lambda ep: "AUDIO")
    ui = xu.xmlUI()
    ui.current_episode = object()
    ui.output_audio()
    assert called["out"] == "AUDIO"

    # cgfixes
    monkeypatch.setattr(xu, "cgfixes_report", lambda ep: "CGFIXES")
    ui.output_cgfixes()
    assert called["out"] == "CGFIXES"

    # conform
    monkeypatch.setattr(xu, "conform_report", lambda ep: "CONFORM")
    ui.output_conform()
    assert called["out"] == "CONFORM"


def test_output_filtered_xml_calls_write_filtered(monkeypatch):
    ui = xu.xmlUI()

    class FEp:
        def write_filtered(self):
            return "FILTERED"

    ui.current_episode = FEp()
    recorded = {}
    monkeypatch.setattr(
        xu.xmlUI, "show_output", lambda self, out: recorded.setdefault("o", out)
    )
    ui.output_filtered_xml()
    assert recorded["o"] == "FILTERED"


def test_confirm_upload_shows_error_when_get_name_none(monkeypatch):
    ui = xu.xmlUI()
    ui.root = object()
    ui.ss_link = DummyStringVar()
    ui.ss_link.set("link")

    monkeypatch.setattr(xu, "get_name", lambda link: None)
    called = {}
    monkeypatch.setattr(
        xu.messagebox,
        "showerror",
        lambda title, msg: called.setdefault("err", (title, msg)),
    )

    ui.confirm_upload()
    assert "err" in called


def test_confirm_upload_creates_window_when_get_name(monkeypatch):
    ui = xu.xmlUI()
    ui.root = object()
    ui.ss_link = DummyStringVar()
    ui.ss_link.set("link")

    monkeypatch.setattr(xu, "get_name", lambda link: "ItemName")

    created = {}

    class FakeTop:
        def __init__(self, root):
            created["top"] = True

        def resizable(self, a, b):
            pass

        def title(self, t):
            created["title"] = t

    monkeypatch.setattr(xu, "Toplevel", FakeTop)
    # stub ttk widgets used inside confirm_upload
    monkeypatch.setattr(
        xu,
        "ttk",
        types.SimpleNamespace(
            Frame=lambda *a, **k: types.SimpleNamespace(grid=lambda *a, **k: None),
            Label=lambda *a, **k: types.SimpleNamespace(grid=lambda *a, **k: None),
            Button=lambda *a, **k: types.SimpleNamespace(grid=lambda *a, **k: None),
        ),
    )

    ui.current_episode = types.SimpleNamespace(file="/path/to/file.xml")
    ui.confirm_upload()
    assert created.get("top", False) is True


def test_xml_to_episode_no_file_shows_info(monkeypatch):
    ui = xu.xmlUI()
    ui.xml_file_string = DummyStringVar()
    ui.xml_functions = []

    monkeypatch.setattr(xu.filedialog, "askopenfilename", lambda **k: "")
    called = {}
    monkeypatch.setattr(
        xu.messagebox,
        "showinfo",
        lambda title, msg: called.setdefault("info", (title, msg)),
    )

    ui.xml_to_episode()
    assert "info" in called


def test_xml_to_episode_success_enables_buttons_and_shows_output(monkeypatch, tmp_path):
    # create a minimal xml file similar to earlier tests
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
            <end>10</end>
            <in>0</in>
            <out>10</out>
          </clipitem>
        </track>
      </video>
      <audio>
        <track MZ.TrackName="T1">
          <enabled>TRUE</enabled>
          <clipitem>
            <enabled>TRUE</enabled>
            <name>aud1</name>
            <masterclipid>m1</masterclipid>
            <file>
              <pathurl>file://localhost/C:/a.wav</pathurl>
            </file>
            <start>0</start>
            <end>1</end>
            <labels>
              <label2>yellow</label2>
            </labels>
          </clipitem>
        </track>
      </audio>
    </media>
  </sequence>
</root>
"""
    p = tmp_path / "x.xml"
    p.write_text(content)

    ui = xu.xmlUI()
    ui.xml_file_string = DummyStringVar()

    # add two fake buttons that should be enabled
    btn1 = FakeButton()
    btn2 = FakeButton()
    ui.xml_functions = [btn1, btn2]

    monkeypatch.setattr(xu.filedialog, "askopenfilename", lambda **k: str(p))
    # stub Episode to avoid complex parsing side effects; provide ingest_log and file
    fake_episode = types.SimpleNamespace(ingest_log="INGEST", file=str(p))
    monkeypatch.setattr(xu, "Episode", lambda path: fake_episode)
    # stub reports
    monkeypatch.setattr(xu, "conform_report", lambda ep: "CONF")
    monkeypatch.setattr(xu, "cgfixes_report", lambda ep: "CGF")

    recorded = {}
    monkeypatch.setattr(
        xu.xmlUI, "show_output", lambda self, out: recorded.setdefault("out", out)
    )

    ui.xml_to_episode()
    # buttons should be enabled (state set to NORMAL)
    assert btn1._state == xu.NORMAL
    assert btn2._state == xu.NORMAL
    assert "Aggregate Reports" in recorded["out"]
