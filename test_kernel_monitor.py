import os
import signal
import subprocess
import time
from unittest import mock

import pytest

import kernel_monitor


@pytest.fixture
def mock_send_data():
    with mock.patch("kernel_monitor.send_data") as mock_send:
        yield mock_send


def test_handle_timeout(monkeypatch):
    mock_killpg = mock.Mock()
    monkeypatch.setattr(os, "killpg", mock_killpg)

    # with pytest.raises(SystemExit):
    kernel_monitor.handle_timeout(signal.SIGALRM, None)

    # mock_killpg.assert_called_once()


def test_receive_data(mock_send_data):
    data = {
        "timestamp": time.time(),
        "syscall": "open()",
    }
    assert kernel_monitor.receive_data(data) == "Data received"
    # assert mock_send_data.called


@pytest.mark.parametrize("line", ["/usr/bin/program", "path/to/program"])
def test_script_execution(line, mock_send_data, monkeypatch):
    mock_popen = mock.Mock()
    mock_popen.stderr.readline.side_effect = [
        b"syscall1",
        b"syscall2",
        b"",
    ]
    mock_popen.communicate.return_value = (b"remaining output",)

    mock_popen_context = mock.MagicMock(return_value=mock_popen)
    monkeypatch.setattr(subprocess, "Popen", mock_popen_context)

    mock_time = mock.Mock(side_effect=[1, 2, 4, 5])
    monkeypatch.setattr(time, "time", mock_time)

    monkeypatch.setenv("ARGUMENT", line)

    monkeypatch.setattr(
        os, "getpgid", lambda pid: 12345
    )  # Replace 12345 with the expected process group ID

    with mock.patch("kernel_monitor.os.killpg"):
        with mock.patch("kernel_monitor.signal.alarm"):
            with mock.patch("kernel_monitor.signal.signal"):
                with mock.patch("kernel_monitor.receive_data"):
                    with mock.patch("kernel_monitor.handle_timeout"):
                        kernel_monitor.main()

    assert mock_popen_context.called
    assert mock_popen.stderr.readline.call_count == 3
    # assert mock_send_data.call_count == 2

    mock_popen_context.assert_called_with(
        ["strace", line],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid,
    )
