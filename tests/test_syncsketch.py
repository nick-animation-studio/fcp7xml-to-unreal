from premiere_to_ue.models.Note import Note
from premiere_to_ue.xml_helpers import syncsketch as ss_mod


class FakeAPI:
    def __init__(self, username=None, key=None):
        self.username = username
        self.key = key
        self._last_added = None

    def get_projects(self):
        return {"objects": []}

    def get_reviews_by_project_id(self, project_id, limit=1000):
        return {"objects": []}

    def get_media_by_review_id(self, review_id):
        return {"objects": []}

    def get_item(self, item_id):
        return {"id": item_id, "name": "ItemName", "first_frame": 100}

    def add_comment(self, item_id, comment, review_id, start_frame):
        self._last_added = (item_id, comment, review_id, start_frame)


def test_connect_to_syncsketch_no_env(monkeypatch, caplog):
    # Ensure env vars absent
    monkeypatch.delenv("SYNCSKETCH_USERNAME", raising=False)
    monkeypatch.delenv("SYNCSKETCH_API_KEY", raising=False)

    res = ss_mod.connect_to_syncsketch()
    assert res is None
    assert "missing values" in caplog.text


def test_connect_to_syncsketch_success(monkeypatch):
    monkeypatch.setenv("SYNCSKETCH_USERNAME", "u")
    monkeypatch.setenv("SYNCSKETCH_API_KEY", "k")

    # patch the syncsketch.SyncSketchAPI constructor used inside the module
    monkeypatch.setattr(ss_mod, "syncsketch", type("M", (), {"SyncSketchAPI": FakeAPI}))

    api = ss_mod.connect_to_syncsketch()
    assert isinstance(api, FakeAPI)
    assert api.username == "u"
    assert api.key == "k"


def test_get_project_id_variants():
    class S:
        def __init__(self, projects):
            self._projects = projects

        def get_projects(self):
            return {"objects": self._projects}

    s_empty = S([])
    assert ss_mod.get_project_id(s_empty) is None

    s_one = S([{"id": "p1"}])
    assert ss_mod.get_project_id(s_one) == "p1"


def test_get_review_id_and_item_id():
    class S:
        def __init__(self):
            pass

        def get_reviews_by_project_id(self, project_id, limit=1000):
            return {
                "objects": [
                    {"reviewURL": "https://www.syncsketch.com/review/abc/", "id": "r1"}
                ]
            }

        def get_media_by_review_id(self, review_id):
            return {"objects": [{"id": 42}, {"id": 43}]}

    s = S()
    # review link normalization: nick. -> www., and #/ -> /
    assert (
        ss_mod.get_review_id(s, "p", "https://nick.syncsketch.com/review/abc/#/")
        == "r1"
    )
    # item id matching by string presence
    assert ss_mod.get_item_id(s, "r1", "https://.../42") == 42


def test_max_post_comment_calls_add_comment(monkeypatch, capsys):
    s = FakeAPI()
    # get_item returns first_frame 100 by FakeAPI
    ss_mod.max_post_comment(s, 7, "hello", "rid", 10)
    # ensure add_comment was called with expected tuple
    assert s._last_added == (7, "hello", "rid", 10)


def test_upload_posts_comments_and_returns_warning(monkeypatch):
    # build a fake episode object with notes (one tagged, one not)
    class Ep:
        def __init__(self):
            self.notes = [
                Note(1, 2, ["#ok"], "Tagged note"),
                Note(5, 6, [], "NoTag note"),
            ]

    ep = Ep()

    # monkeypatch connection and id resolution helpers to return a fake API and ids
    fake_api = FakeAPI()
    monkeypatch.setattr(ss_mod, "connect_to_syncsketch", lambda: fake_api)
    monkeypatch.setattr(ss_mod, "get_project_id", lambda s: "pid")
    monkeypatch.setattr(ss_mod, "get_review_id", lambda s, pid, link: "rid")
    monkeypatch.setattr(ss_mod, "get_item_id", lambda s, rid, link: 123)

    # replace max_post_comment with a stub that records calls
    calls = []

    def fake_max_post_comment(s, item_id, comment, review_id, start_frame):
        calls.append((item_id, comment, review_id, start_frame))

    monkeypatch.setattr(ss_mod, "max_post_comment", fake_max_post_comment)

    res = ss_mod.upload(ep, "dummy_link")
    # should have attempted to post two comments
    assert len(calls) == 2
    # because one note lacked tags, upload should return a warning string
    assert "Warning, found the following comments missing tags" in res
