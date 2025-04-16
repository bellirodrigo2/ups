from datetime import datetime

import pytest

from domain.vo.date import Flextimedelta


@pytest.fixture
def fixtures():
    """
    dt1: 2025‑04‑16 10:00
    delta1: 1 ano, 1 mês, 2 dias
    delta2: 0 ano, 0 mês, 3 dias
    """
    dt1 = datetime(2025, 4, 16, 10, 0, 0)
    delta1 = Flextimedelta(years=1, months=1, days=2)
    delta2 = Flextimedelta(days=3)
    return dt1, delta1, delta2


def test_add_to_datetime(fixtures):
    dt1, delta1, _ = fixtures
    # 2025‑04‑16 + (1y,1m,2d) => 2026‑05‑18 10:00
    assert dt1 + delta1 == datetime(2026, 5, 18, 10, 0, 0)


def test_radd_datetime(fixtures):
    dt1, delta1, _ = fixtures
    # delta1 + dt1 deve ser igual a dt1 + delta1
    assert delta1 + dt1 == dt1 + delta1


def test_sub_from_datetime(fixtures):
    dt1, delta1, _ = fixtures
    # 2025‑04‑16 – (1y,1m,2d) => 2024‑03‑14 10:00
    assert dt1 - delta1 == datetime(2024, 3, 14, 10, 0, 0)


def test_rsub_datetime(fixtures):
    dt1, delta1, _ = fixtures
    # dt1.__rsub__(delta1) não é usado; teste reverso via expressão
    # delta1 olarak for datetime – Flextimedelta não faz sentido,
    # então garantimos que datetime – delta1 funciona simetricamente
    assert dt1 - delta1 == dt1 + (delta1 * -1)


def test_add_flextimedelta(fixtures):
    _, delta1, delta2 = fixtures
    s = delta1 + delta2
    assert isinstance(s, Flextimedelta)
    # (1y1m2d) + (0y0m3d) = (1y1m5d)
    assert (s.years, s.months, s.days) == (1, 1, 5)


def test_sub_flextimedelta(fixtures):
    _, delta1, delta2 = fixtures
    s = delta1 - delta2
    # (1y1m2d) - 3d = (1y1m-1d)
    assert (s.years, s.months, s.days) == (1, 1, -1)


def test_mul_and_rmul(fixtures):
    _, delta1, _ = fixtures
    d2 = delta1 * 2
    assert isinstance(d2, Flextimedelta)
    assert (d2.years, d2.months, d2.days) == (2, 2, 4)
    # rmul
    assert 2 * delta1 == d2


def test_floordiv(fixtures):
    _, delta1, _ = fixtures
    half = delta1 // 2
    # floor div de (1y,1m,2d) por 2 => (0y,0m,1d)
    assert (half.years, half.months, half.days) == (0, 0, 1)


def test_truediv(fixtures):
    _, delta1, _ = fixtures
    div = delta1 / 2
    # true div mantém float
    assert div.years == 0.5
    assert div.months == 0.5
    assert div.days == 1.0


def test_mod(fixtures):
    _, delta1, delta2 = fixtures
    # modulo de dias: 2 % 3 == 2
    assert (delta1 % delta2) == 2


def test_eq_ne(fixtures):
    _, delta1, delta2 = fixtures
    assert delta1 == delta1
    assert not (delta1 != delta1)
    assert delta1 != delta2


def test_bool_and_repr(fixtures):
    _, delta1, delta2 = fixtures
    assert bool(delta1)
    zero = Flextimedelta()
    assert not zero
    # repr contém os componentes
    r = repr(delta1)
    assert "years=1" in r and "months=1" in r and "days=2" in r
