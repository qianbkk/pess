"""PESS 共享 pytest fixtures (OPT-027)

5 个常用 fixture 供所有 test_*.py 复用:
- tmp_pess_root: 临时 PESS 仓库结构
- mock_settings_json: 模拟 ~/.claude/settings.json
- mock_python_version: 模拟 Python --version 输出
- captured_stdin: 捕获 hook stdin
- pess_root: 当前 PESS 仓库路径
"""
import os
import sys
import tempfile
from pathlib import Path

import pytest

PESS_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def pess_root():
    return PESS_ROOT


@pytest.fixture
def tmp_pess_root(tmp_path):
    """临时 PESS 仓库结构, 包含 hooks/ + templates/"""
    pess = tmp_path / "pess"
    (pess / "hooks").mkdir(parents=True)
    (pess / "templates").mkdir(parents=True)
    return pess


@pytest.fixture
def mock_settings_json(tmp_path):
    """模拟 ~/.claude/settings.json 路径"""
    s = tmp_path / "settings.json"
    s.write_text('{"hooks": {"PreToolUse": []}}', encoding="utf-8")
    return s


@pytest.fixture
def mock_python_version(monkeypatch):
    """模拟 python --version 返回值"""
    class MockResult:
        returncode = 0
        stdout = "Python 3.10.5"
        stderr = ""
    def fake_run(*args, **kwargs):
        return MockResult()
    monkeypatch.setattr("subprocess.run", fake_run)
    return "Python 3.10.5"


@pytest.fixture
def captured_stdin(monkeypatch):
    """捕获 stdin 写入"""
    captured = {"data": ""}
    class FakeStdin:
        def read(self):
            return captured["data"]
    monkeypatch.setattr("sys.stdin", FakeStdin())
    def set_data(d):
        captured["data"] = d
    return set_data
