import re

import pytest

from jpoetry.utils import InverseMapping, Timer


def test_inverse_mapping():
    inverse_mapping = InverseMapping({'a', 'b'}, 'NOT IN SET')
    assert 'a' not in inverse_mapping
    assert 'b' not in inverse_mapping
    assert 'c' in inverse_mapping
    assert inverse_mapping['c'] == 'NOT IN SET'
    assert inverse_mapping.get('b') is None
    assert len(inverse_mapping) == 2
    assert inverse_mapping.keys() == {'a', 'b'}
    assert set(iter(inverse_mapping)) == {'a', 'b'}
    with pytest.raises(KeyError, match=re.escape(f"Key 'a' found in {inverse_mapping}")):
        inverse_mapping['a']


def test_timer(mocker):
    monotonic_patch = mocker.patch('jpoetry.utils.monotonic')
    with Timer('test') as timer:
        assert not hasattr(timer, 'elapsed')
        assert repr(timer) == "Timer('test', elapsed=...)"

    assert timer.name == 'test'
    expected_elapsed = monotonic_patch.return_value - monotonic_patch.return_value
    assert repr(timer) == f"Timer('test', elapsed={expected_elapsed})"
    assert timer.elapsed == expected_elapsed
