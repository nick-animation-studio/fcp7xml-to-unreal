import types

from fcp7xml_to_unreal import xml_ui as xu


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
        self.grid_args = None

    def grid(self, **kwargs):
        self.grid_args = kwargs

    def config(self, state=None):
        self._state = state


class FakeScrollbar:
    def __init__(self, *args, **kwargs):
        self.config_args = None
        self.set = lambda *a, **k: None

    def pack(self, **kwargs):
        self.pack_args = kwargs

    def config(self, **kwargs):
        self.config_args = kwargs


class FakeText:
    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs
        self.inserted = []
        self.yview = lambda *a, **k: None

    def insert(self, *args):
        self.inserted.append(args)

    def pack(self, **kwargs):
        self.pack_args = kwargs


class FakeToplevel:
    def __init__(self, root=None):
        self.root = root
        self.title_text = None

    def title(self, text):
        self.title_text = text


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


def test_create_button_grid_column_increments(monkeypatch):
    fakefrm = object()
    ui = xu.xmlUI(frm=fakefrm)

    monkeypatch.setattr(
        xu,
        "ttk",
        types.SimpleNamespace(
            Button=FakeButton, Frame=lambda *a, **k: None, Label=lambda *a, **k: None
        ),
    )

    ui.create_button("First", lambda: None)
    ui.create_button("Second", lambda: None)

    assert ui.xml_functions[0].grid_args["column"] == 0
    assert ui.xml_functions[1].grid_args["column"] == 1


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


def test_output_audio_none_does_not_show(monkeypatch):
    called = {}

    def fake_show_output(self, output):
        called["out"] = output

    monkeypatch.setattr(xu, "audio_report", lambda ep: None)
    monkeypatch.setattr(xu.xmlUI, "show_output", fake_show_output)

    ui = xu.xmlUI()
    ui.current_episode = object()
    ui.output_audio()
    assert "out" not in called


def test_output_filtered_xml_calls_episode_write(monkeypatch):
    called = {}

    def fake_write_filtered():
        called["called"] = True

    ui = xu.xmlUI()
    ui.current_episode = types.SimpleNamespace(write_filtered=fake_write_filtered)
    ui.output_filtered_xml()

    assert called.get("called") is True


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
    # output should include ingest log and reports
    assert "INGEST" in recorded["out"]


def test_xml_to_episode_includes_report_sections(monkeypatch, tmp_path):
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
      <end>10</end>
      <in>0</in>
      <out>10</out>
      </clipitem>
    </track>
    </video>
    <audio/>
  </media>
  </sequence>
</root>
"""
    p = tmp_path / "x.xml"
    p.write_text(content)

    ui = xu.xmlUI()
    ui.xml_file_string = DummyStringVar()
    ui.xml_functions = []

    monkeypatch.setattr(xu.filedialog, "askopenfilename", lambda **k: str(p))
    fake_episode = types.SimpleNamespace(ingest_log="INGEST", file=str(p))
    monkeypatch.setattr(xu, "Episode", lambda path: fake_episode)
    monkeypatch.setattr(xu, "conform_report", lambda ep: "CONF")
    monkeypatch.setattr(xu, "cgfixes_report", lambda ep: "CGF")

    recorded = {}
    monkeypatch.setattr(
        xu.xmlUI, "show_output", lambda self, out: recorded.setdefault("out", out)
    )

    ui.xml_to_episode()
    output = recorded["out"]
    assert output.index("Ingest logs") < output.index("Conform Report")
    assert output.index("Conform Report") < output.index("CG Fixes Report")
    assert ui.xml_file_string.get() == str(p)


def test_show_output_empty_string_defaults_message(monkeypatch):
    ui = xu.xmlUI(root=object())

    created = {}

    def fake_scrollbar(*args, **kwargs):
        created["scroll"] = FakeScrollbar(*args, **kwargs)
        return created["scroll"]

    def fake_text(*args, **kwargs):
        created["text"] = FakeText(*args, **kwargs)
        return created["text"]

    monkeypatch.setattr(xu, "Toplevel", FakeToplevel)
    monkeypatch.setattr(xu.tk, "Scrollbar", fake_scrollbar)
    monkeypatch.setattr(xu.tk, "Text", fake_text)

    ui.show_output("")

    assert created["text"].inserted
    assert created["text"].inserted[0][1] == "No errors found!"


def test_show_output_wires_scrollbar_and_text(monkeypatch):
    ui = xu.xmlUI(root=object())
    created = {}

    def fake_scrollbar(*args, **kwargs):
        created["scroll"] = FakeScrollbar(*args, **kwargs)
        return created["scroll"]

    def fake_text(*args, **kwargs):
        created["text"] = FakeText(*args, **kwargs)
        return created["text"]

    monkeypatch.setattr(xu, "Toplevel", FakeToplevel)
    monkeypatch.setattr(xu.tk, "Scrollbar", fake_scrollbar)
    monkeypatch.setattr(xu.tk, "Text", fake_text)

    ui.show_output("Hello")

    assert created["text"].kwargs.get("yscrollcommand") == created["scroll"].set
    assert created["scroll"].config_args["command"] == created["text"].yview


def test_main_wires_ui(monkeypatch):
    called = {"create_button": 0}

    class FakeRoot:
        def resizable(self, *args, **kwargs):
            pass

        def title(self, *args, **kwargs):
            pass

        def mainloop(self):
            pass

    class FakeEntry:
        def __init__(self, *args, **kwargs):
            self.kwargs = kwargs

        def grid(self, **kwargs):
            self.grid_args = kwargs

    class FakeFrame:
        def __init__(self, *args, **kwargs):
            pass

        def grid(self, **kwargs):
            pass

    class FakeUIButton:
        def __init__(self, *args, **kwargs):
            pass

        def grid(self, **kwargs):
            pass

    def fake_create_button(self, label, function):
        called["create_button"] += 1
        self.xml_functions.append(FakeButton())

    monkeypatch.setattr(xu.tk, "Tk", lambda: FakeRoot())
    monkeypatch.setattr(xu.tk, "StringVar", DummyStringVar)
    monkeypatch.setattr(xu.ttk, "Frame", FakeFrame)
    monkeypatch.setattr(xu.tk, "Entry", FakeEntry)
    monkeypatch.setattr(xu.ttk, "Button", FakeUIButton)
    monkeypatch.setattr(xu.xmlUI, "create_button", fake_create_button)

    xu.main()

    assert called["create_button"] == 2
