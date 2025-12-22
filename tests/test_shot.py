import pytest

from premiere_to_ue.models.Shot import Shot


def test_init_and_scene_number_and_durations():
    s = Shot("shot_001_desc", 10, 20, 12, 18)
    assert s.name == "shot_001_desc"
    assert s.sf == 10
    assert s.ef == 20
    assert s.ip == 12
    assert s.op == 18
    # dur is sf - ef (intentional in implementation)
    assert s.dur == -10
    assert s.clipdur == 6
    assert s.scene_number() == "001"


def test_str_and_lt():
    a = Shot("a_001", 1, 2, 0, 0)
    b = Shot("b_001", 1, 2, 0, 0)
    assert a < b
    s = Shot("shot_abc", 123, 456, 0, 0)
    out = str(s)
    assert "shot_abc" in out
    assert "123" in out
    assert "456" in out


def test_match_perfect_close_none():
    s1 = Shot("s1", 10, 20, 0, 0)
    s2 = Shot("s2", 10, 20, 0, 0)
    assert s1.match(s2) == "perfect"

    # close: within the +/-2 window used by the implementation
    s3 = Shot("s3", 9, 21, 0, 0)
    assert s1.match(s3) == "close"

    s4 = Shot("s4", 0, 1000, 0, 0)
    assert s1.match(s4) is None


def test_contains_and_overlaps():
    outer = Shot("outer", 10, 50, 0, 0)
    inner = Shot("inner", 20, 30, 0, 0)
    assert outer.contains(inner)
    assert not inner.contains(outer)

    s = Shot("s", 100, 200, 0, 0)
    # range completely before -> no overlap
    assert not s.overlaps(50, 99)
    # touching end counts as overlap in implementation
    assert s.overlaps(200, 300)
    # partial overlap
    assert s.overlaps(150, 250)


def test_fx_handling_and_fx_str():
    s = Shot("fxshot", 1, 2, 0, 0)
    assert not s.has_fx()
    s.add_fx("blur", {"amount": "5", "quality": "high"})
    assert s.has_fx()
    fxstring = s.fx_str()
    assert "FX: blur" in fxstring
    assert "amount 5" in fxstring
    assert "quality high" in fxstring


def test_is_valid_returns_true():
    s = Shot("v", 1, 2, 3, 4)
    assert s.is_valid() is True
