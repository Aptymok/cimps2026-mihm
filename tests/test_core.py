import numpy as np
from mihm.core import robust_reference, normalized_distance, phi_s


def test_reference_nonzero():
    r = robust_reference([1, 1, 1, 1])
    assert r['scale'] >= 0.01


def test_distance_bounds():
    assert 0 <= normalized_distance(5, 0, 1) <= 1


def test_phi_bounds():
    assert 0 <= phi_s([0, .5, 1]) <= 1


def test_equal_weights_clean():
    assert abs(phi_s([0, 0, 0]) - 1) < 1e-12
