from datetime import datetime, timedelta

import freezegun

from jpoetry.utils import TimeAwareCounter, Timer


def test_timer(mocker):
    monotonic_patch = mocker.patch('jpoetry.utils.monotonic')
    with Timer('test') as timer:
        assert not hasattr(timer, 'elapsed')
        assert repr(timer) == "Timer('test', elapsed=...)"

    assert timer.name == 'test'
    expected_elapsed = monotonic_patch.return_value - monotonic_patch.return_value
    assert repr(timer) == f"Timer('test', elapsed={expected_elapsed})"
    assert timer.elapsed == expected_elapsed


@freezegun.freeze_time(datetime.now())
def test_counter():
    now = datetime.now()
    counter = TimeAwareCounter[None](5)
    assert counter.count() == 0
    counter.add(None)
    assert counter.count() == 1

    with freezegun.freeze_time(now + timedelta(seconds=1)):
        counter.add(None)
        assert counter.count() == 2

    with freezegun.freeze_time(now + timedelta(seconds=4)):
        counter.add(None)
        assert counter.count() == 3

    with freezegun.freeze_time(now + timedelta(seconds=6)):
        counter.add(None)
        assert counter.count() == 3

    with freezegun.freeze_time(now + timedelta(seconds=7)):
        assert counter.count() == 2

    with freezegun.freeze_time(now + timedelta(seconds=11)):
        assert counter.count() == 1

    with freezegun.freeze_time(now + timedelta(seconds=13)):
        assert counter.count() == 0


@freezegun.freeze_time(datetime.now())
def test_counter_unique():
    now = datetime.now()
    counter = TimeAwareCounter[int](5)
    assert counter.count() == 0
    assert counter.count_unique() == 0
    counter.add(1)
    assert counter.count() == 1
    assert counter.count_unique() == 1

    with freezegun.freeze_time(now + timedelta(seconds=1)):
        counter.add(1)
        assert counter.count() == 2
        assert counter.count_unique() == 1

    with freezegun.freeze_time(now + timedelta(seconds=4)):
        counter.add(1)
        assert counter.count_unique() == 1
        assert counter.count() == 3

    with freezegun.freeze_time(now + timedelta(seconds=6)):
        counter.add(2)
        assert counter.count_unique() == 2
        assert counter.count() == 3

    with freezegun.freeze_time(now + timedelta(seconds=7)):
        assert counter.count_unique() == 2
        assert counter.count() == 2

    with freezegun.freeze_time(now + timedelta(seconds=11)):
        assert counter.count_unique() == 1
        assert counter.count() == 1

    with freezegun.freeze_time(now + timedelta(seconds=13)):
        assert counter.count() == 0
