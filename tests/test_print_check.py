import pytest

# This test runs last to catch unintentional prints
@pytest.mark.usefixtures("capsys")
def test_no_print_statements(capsys):
    captured = capsys.readouterr()
    assert captured.out.strip() == "", f"Unexpected print output:\n{captured.out}"
    assert captured.err.strip() == "", f"Unexpected error output:\n{captured.err}"
