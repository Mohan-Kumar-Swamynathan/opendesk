"""Path safety tests."""
import pytest
from pathlib import Path


def test_protected_paths_readonly():
    from opendesk.safety import validate_path
    from opendesk.errors import PathSafetyError

    with pytest.raises(PathSafetyError):
        validate_path("~/.ssh", "write")


def test_absolute_paths_work():
    from opendesk.safety import validate_path

    result = validate_path("/Users", "read")
    assert result == Path("/Users")