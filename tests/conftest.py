import pytest

from fcp7xml_to_unreal.models import Note


@pytest.fixture(
    params=[(1, 101, ["example note tag1", "example note tag2"], "example note text")]
)
def note(request):
    start_frame, end_frame, tags, text = request.param
    return Note.Note(start_frame, end_frame, tags, text)
