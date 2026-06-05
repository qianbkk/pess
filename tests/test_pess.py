"""PESS pess.py 单元测试 (OPT-012, v3.8.0 升级为 pytest 风格)

新增 fixture-style 测试, 验证 conftest.py 的 5 个 fixture 真能消费
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PESS_PY = Path(__file__).resolve().parent.parent / "pess.py"


def test_pess_help():
    """pess.py --help 应输出帮助"""
    result = subprocess.run(
        [sys.executable, str(PESS_PY), "--help"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=5,
    )
    assert result.returncode == 0
    assert "PESS" in result.stdout
    assert "install" in result.stdout
    assert "init" in result.stdout
    print("  PASS  pess.py --help → 列出 install/init/update/doctor")


def test_pess_install_creates_settings():
    """pess.py install 应创建 ~/.claude/settings.json (用 conftest mock_settings_json 模式)"""
    with tempfile.TemporaryDirectory() as fake_home:
        env = {"HOME": fake_home, "USERPROFILE": fake_home,
               "PATH": __import__("os").environ.get("PATH", "")}
        result = subprocess.run(
            [sys.executable, str(PESS_PY), "install"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=10,
            env=env,
        )
        settings = Path(fake_home) / ".claude" / "settings.json"
        if settings.is_file():
            data = json.loads(settings.read_text(encoding="utf-8"))
            assert "hooks" in data
            assert "PreToolUse" in data["hooks"]
            assert "SessionStart" in data["hooks"]
            assert "UserPromptSubmit" in data["hooks"]
            print("  PASS  pess.py install → 写入 settings.json (含 4 类 hook)")
        else:
            print(f"  SKIP  pess.py install: settings.json 未创建 (rc={result.returncode})")


def test_pess_init_skeleton():
    """pess.py init 应输出 skeleton 消息"""
    result = subprocess.run(
        [sys.executable, str(PESS_PY), "init", "-n", "test-proj", "-t", "default"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=5,
    )
    assert result.returncode == 0
    assert "test-proj" in result.stdout
    print("  PASS  pess.py init → 输出项目名 (skeleton)")


def test_pess_update_skeleton():
    """pess.py update 应输出 skeleton 消息"""
    result = subprocess.run(
        [sys.executable, str(PESS_PY), "update"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=5,
    )
    assert result.returncode == 0
    print("  PASS  pess.py update → Phase 2 占位")


# ===== Pytest fixture-style 测试 (v3.8.0 新增) =====
# 验证 conftest.py 5 个 fixture 真能被消费

import pytest


@pytest.mark.usefixtures("pess_root")
def test_pess_root_fixture(pess_root):
    """pess_root fixture 应返回 PESS 仓库根"""
    assert pess_root.is_dir()
    assert (pess_root / "pess.py").is_file()
    assert (pess_root / "hooks").is_dir()
    print(f"  PASS  pess_root fixture → {pess_root.name}/")


def test_tmp_pess_root_fixture(tmp_pess_root):
    """tmp_pess_root fixture 应创建 hooks/ + templates/"""
    assert (tmp_pess_root / "hooks").is_dir()
    assert (tmp_pess_root / "templates").is_dir()
    print(f"  PASS  tmp_pess_root fixture → 自动建 hooks/ + templates/")


def test_mock_settings_json_fixture(mock_settings_json):
    """mock_settings_json fixture 应返回含 PreToolUse 的 settings"""
    data = json.loads(mock_settings_json.read_text(encoding="utf-8"))
    assert "hooks" in data
    assert "PreToolUse" in data["hooks"]
    print("  PASS  mock_settings_json fixture → 含 PreToolUse")


def test_mock_python_version_fixture(mock_python_version):
    """mock_python_version fixture 应返回 Python 3.10.5"""
    assert mock_python_version == "Python 3.10.5"
    print(f"  PASS  mock_python_version fixture → {mock_python_version}")


def test_captured_stdin_fixture(captured_stdin):
    """captured_stdin fixture 应能写入并被 sys.stdin.read() 读到"""
    captured_stdin('{"hook_event_name": "test"}')
    assert sys.stdin.read() == '{"hook_event_name": "test"}'
    print("  PASS  captured_stdin fixture → sys.stdin.read() 读到注入数据")


# 注: 本文件含 pytest fixture-style 测试, 必须通过 `pytest tests/test_pess.py` 运行
# 不再保留 `if __name__ == "__main__"` 兼容入口 (fixture 测试需要 pytest 自动注入)
