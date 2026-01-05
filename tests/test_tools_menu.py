from pathlib import Path
from unittest import mock

from tui.tools import (
    run_shell_script_screen,
    diagnostics_screen,
)


class FakeScreen:
    def __init__(self, keys) -> None:
        self._keys = list(keys)
        self.lines: list[str] = []
        self.height = 24
        self.width = 80

    def clear(self) -> None:
        self.lines.clear()

    def erase(self) -> None:
        self.lines.clear()

    def getmaxyx(self):
        return (self.height, self.width)

    def addstr(self, *args):
        text = args[-1]
        self.lines.append(str(text))

    def move(self, y, x):
        # Cursor movement is ignored in tests.
        pass

    def attron(self, *args, **kwargs):
        # Color attributes are ignored in tests.
        pass

    def attroff(self, *args, **kwargs):
        # Color attributes are ignored in tests.
        pass

    def refresh(self) -> None:
        pass

    def getch(self) -> int:
        if self._keys:
            return self._keys.pop(0)
        # Default to 'q' to avoid infinite loops.
        return ord("q")


def test_run_shell_script_screen_runs_script_and_shows_output(tmp_path: Path) -> None:
    case_dir = tmp_path / "case"
    case_dir.mkdir()
    script = case_dir / "hello.sh"
    script.write_text("#!/bin/sh\necho hello-from-script\n")

    # Select first script, then 'q' to exit viewer.
    screen = FakeScreen(keys=[ord("\n"), ord("q")])

    run_shell_script_screen(screen, case_dir)

    # Expect the command and output to have been written to the screen.
    joined = "\n".join(screen.lines)
    assert "sh hello.sh" in joined
    assert "hello-from-script" in joined


def test_run_shell_script_screen_handles_no_scripts(tmp_path: Path) -> None:
    case_dir = tmp_path / "case"
    case_dir.mkdir()

    screen = FakeScreen(keys=[ord("q")])

    run_shell_script_screen(screen, case_dir)

    joined = "\n".join(screen.lines)
    assert "No *.sh scripts found in case directory." in joined


def test_diagnostics_screen_runs_selected_tool(tmp_path: Path) -> None:
    case_dir = tmp_path / "case"
    case_dir.mkdir()

    # Select first diagnostics entry, then 'q' to exit viewer.
    screen = FakeScreen(keys=[ord("\n"), ord("q")])

    completed = mock.Mock()
    completed.returncode = 0
    completed.stdout = "ok\n"
    completed.stderr = ""

    with mock.patch("tui.tools.subprocess.run", return_value=completed) as run:
        diagnostics_screen(screen, case_dir)

    # Ensure a diagnostics command was invoked.
    assert run.called
    # And that output was sent to the viewer.
    joined = "\n".join(screen.lines)
    assert "stdout:" in joined
    assert "ok" in joined

