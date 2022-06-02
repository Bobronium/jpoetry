from jpoetry.utils import Timer


def test_timer(mocker):
    monotonic_patch = mocker.patch('jpoetry.utils.monotonic')
    with Timer('test') as timer:
        assert not hasattr(timer, 'elapsed')
        assert repr(timer) == "Timer('test', elapsed=...)"

    assert timer.name == 'test'
    expected_elapsed = monotonic_patch.return_value - monotonic_patch.return_value
    assert repr(timer) == f"Timer('test', elapsed={expected_elapsed})"
    assert timer.elapsed == expected_elapsed
