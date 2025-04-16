from datetime import timedelta

from domain.vo.date import Flextimedelta


def test_comparisons_with_timedelta():
    ft = Flextimedelta(days=1)
    td = timedelta(days=1)
    assert not (ft == td)  # tipos diferentes
    assert not (ft < td)


def test_pos_operator():
    delta = Flextimedelta(days=1)
    assert (+delta) == delta


def test_mod_and_floordiv_with_int():
    d = Flextimedelta(days=5)
    assert (d % 3) == 2
    assert (d // 2).days == 2


def test_floordiv_flextimedelta():
    d1 = Flextimedelta(days=10)
    d2 = Flextimedelta(days=3)
    assert (d1 // d2) == 3


def test_abs_operator():
    d = Flextimedelta(days=-3, months=-2, years=-1)
    abs_d = abs(d)
    assert (abs_d.days, abs_d.months, abs_d.years) == (3, 2, 1)


def test_total_seconds_with_months_years():
    d = Flextimedelta(days=1, months=1, years=1)
    # Aproximado: 1y ≈ 365.25d, 1m ≈ 30.44d
    expected = (1 + 30.44 + 365.25) * 86400
    assert abs(d.total_seconds() - expected) < 1  # margem de erro aceitável


def test_hash_equality():
    a = Flextimedelta(days=1, months=2, years=3)
    b = Flextimedelta(days=1, months=2, years=3)
    assert hash(a) == hash(b)


def test_rsub_timedelta():
    td = timedelta(days=5)
    ft = Flextimedelta(days=2)
    result = td - ft
    assert isinstance(result, Flextimedelta)
    assert result.days == 3
