import pickle
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta

from domain.vo.date import Flextimedelta, Itimedelta


@pytest.fixture
def sample():
    # 1 dia, 2 segundos, 3000 micros; sem meses/anos
    return Flextimedelta(days=1, seconds=2, microseconds=3000)


def test_instance_identified_as_protocol(sample):
    # runtime_checkable
    assert isinstance(sample, Itimedelta)


def test_divmod_returns_int_and_itimedelta(sample):
    # divmod(Itimedelta, Itimedelta) → (int, Itimedelta)
    a = sample  # 1d,2s,3ms
    b = Flextimedelta(days=1)  # 1d
    q, r = divmod(a, b)
    assert isinstance(q, int) and q == 1
    assert isinstance(r, Flextimedelta)
    # resto tem menos de 1 dia
    assert r.days == 0 and r.seconds == 2


def test_hashable_and_uses_total_seconds(sample):
    # deve ser hashable
    h1 = hash(sample)
    h2 = hash(sample)
    assert h1 == h2


def test_bool_zero_and_nonzero():
    nonzero = Flextimedelta(days=1)
    zero = Flextimedelta()
    assert bool(nonzero) is True
    assert bool(zero) is False


def test_reduce_and_pickle_roundtrip(sample):
    data = pickle.dumps(sample)
    loaded = pickle.loads(data)
    assert isinstance(loaded, Flextimedelta)
    assert loaded == sample


def test_to_relativedelta_matches_components(sample):
    rd = sample.to_relativedelta()
    # Como sample não tem meses/anos, rd.months e rd.years zero
    assert isinstance(rd, relativedelta)
    assert rd.days == 1 and rd.seconds == 2 and rd.microseconds == 3000
    assert rd.months == 0 and rd.years == 0


def test_interop_with_builtin_timedelta():
    ft = Flextimedelta(days=1, seconds=5)
    td = timedelta(days=2, seconds=10)

    # soma Flextimedelta + timedelta
    s1 = ft + td
    s2 = td + ft
    assert isinstance(s1, Flextimedelta)
    assert (s1.days, s1.seconds) == (3, 15)

    # subtração
    d1 = ft - td
    assert isinstance(d1, Flextimedelta)

    # timedelta normaliza: (-1, -5) → (-2, 86395)
    expected = ft._timedelta - td
    assert (d1.days, d1.seconds) == (expected.days, expected.seconds)


def test_comparisons_with_protocol(sample):
    a = sample
    b = Flextimedelta(days=1, seconds=1)
    assert a > b
    assert b < a
    assert a >= b and b <= a
    # igualdade com ele mesmo
    assert a == a and not (a != a)


def test_str_and_repr_protocol(sample):
    s = str(sample)
    r = repr(sample)
    # deve conter dias, segundos e micros no repr
    assert "days=1" in r and "seconds=2" in r and "microseconds=3000" in r
    # str deve ser string legível
    assert s.startswith("Flextimedelta(") and isinstance(s, str)
