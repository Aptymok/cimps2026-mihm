from mihm.epistemic import EpistemicStatus


def test_missing_is_not_zero():
    assert EpistemicStatus.MISSING_NOT_OBSERVED.value != "0"
