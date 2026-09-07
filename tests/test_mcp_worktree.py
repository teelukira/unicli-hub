import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
RENDER_MCP_PATH = REPO_ROOT / ".unicli-hub" / "scripts" / "render_mcp.py"


def load_render_mcp():
    spec = importlib.util.spec_from_file_location("render_mcp", RENDER_MCP_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class McpWorktreeTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.main_root = Path(self.temp_dir.name) / "main repo"
        self.linked_root = Path(self.temp_dir.name) / "linked repo"
        scripts_dir = self.main_root / "scripts" / "mcp"
        scripts_dir.mkdir(parents=True)
        for name in ("project-env.sh", "run-with-env.sh"):
            source = REPO_ROOT / "scripts" / "mcp" / name
            target = scripts_dir / name
            shutil.copy2(source, target)
            target.chmod(0o755)
        probe = scripts_dir / "probe.sh"
        probe.write_text(
            "#!/usr/bin/env bash\n"
            "printf '%s\\n' \"${SHARED_VALUE}|${WORKTREE_VALUE}|${OVERRIDE_VALUE}|${INHERITED_VALUE}\"\n",
            encoding="utf-8",
        )
        probe.chmod(0o755)

        self.run_git("init", "-b", "main", cwd=self.main_root)
        self.run_git("add", "scripts", cwd=self.main_root)
        self.run_git(
            "-c",
            "user.name=UniCLI Test",
            "-c",
            "user.email=unicli@example.invalid",
            "commit",
            "-m",
            "test fixture",
            cwd=self.main_root,
        )
        (self.main_root / ".env").write_text(
            "SHARED_VALUE=primary\nOVERRIDE_VALUE=primary\nINHERITED_VALUE=file\n",
            encoding="utf-8",
        )
        self.run_git("worktree", "add", str(self.linked_root), "-b", "linked", cwd=self.main_root)
        (self.linked_root / ".env.local").write_text(
            "WORKTREE_VALUE=linked\nOVERRIDE_VALUE=linked\nINHERITED_VALUE=linked\n",
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def run_git(self, *args, cwd):
        subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)

    def test_launcher_resolves_nested_worktree_and_merges_environment(self):
        nested = self.linked_root / "nested" / "directory"
        nested.mkdir(parents=True)
        probe = self.main_root / "scripts" / "mcp" / "probe.py"
        probe.write_text(
            "import os\n"
            "print('|'.join(["
            "os.environ.get('SHARED_VALUE',''),"
            "os.environ.get('WORKTREE_VALUE',''),"
            "os.environ.get('OVERRIDE_VALUE',''),"
            "os.environ.get('INHERITED_VALUE',''),"
            "]))\n",
            encoding="utf-8",
        )
        env = os.environ.copy()
        env["INHERITED_VALUE"] = "process"
        completed = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "mcp" / "run_with_env.py"),
                sys.executable,
                str(probe),
            ],
            cwd=nested,
            env=env,
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertEqual(
            completed.stdout.strip().split("|"),
            ["primary", "linked", "linked", "process"],
        )

    def test_renderer_loads_primary_and_linked_env_files(self):
        render_mcp = load_render_mcp()
        values = render_mcp.load_project_env(self.linked_root)

        self.assertEqual(values["SHARED_VALUE"], "primary")
        self.assertEqual(values["WORKTREE_VALUE"], "linked")
        self.assertEqual(values["OVERRIDE_VALUE"], "linked")

    def test_renderer_wraps_stdio_server_and_supports_opt_out(self):
        render_mcp = load_render_mcp()
        wrapped = render_mcp.wrap_project_env(
            {"command": "uvx", "args": ["example-server"], "env": {"MODE": "test"}}
        )
        self.assertEqual(wrapped["command"], "python")
        self.assertEqual(wrapped["args"][0:2], ["scripts/mcp/run_with_env.py", "uvx"])
        self.assertEqual(wrapped["args"][2:], ["example-server"])
        self.assertEqual(wrapped["env"], {"MODE": "test"})

        original = {"command": "uvx", "_project_env": False}
        self.assertIs(render_mcp.wrap_project_env(original), original)


if __name__ == "__main__":
    unittest.main()
