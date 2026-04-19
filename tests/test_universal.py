import pytest
import os
from opendesk.tools.filesystem import read_file, write_file, list_directory, get_disk_usage
from opendesk.tools.system import get_system_info
from opendesk.tools.clipboard import get_clipboard, set_clipboard


def test_list_directory_home():
    result = list_directory(path="~")
    assert "items" in result or "error" in result


def test_clipboard_round_trip():
    test_content = "opendesk_test_12345"
    set_result = set_clipboard(content=test_content)
    if set_result.get("success", False):
        get_result = get_clipboard()
        assert get_result.get("content") == test_content


def test_system_info_shape():
    result = get_system_info()
    assert "cpu_percent" in result
    assert "memory_percent" in result
    assert 0 <= result.get("cpu_percent", 0) <= 100


def test_disk_usage():
    result = get_disk_usage(path="/")
    assert "total_gb" in result or "error" in result


def test_read_nonexistent_file():
    result = read_file(path="/nonexistent_file_12345.txt")
    assert "error" in result


def test_write_and_read():
    test_path = "/tmp/opendesk_test.txt"
    test_content = "Hello, opendesk!"
    write_result = write_file(path=test_path, content=test_content)
    assert write_result.get("success", False)

    read_result = read_file(path=test_path)
    assert test_content in read_result.get("content", "")

    if os.path.exists(test_path):
        os.remove(test_path)