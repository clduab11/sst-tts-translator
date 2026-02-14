"""Git operations manager for voice-driven development."""

import asyncio
from pathlib import Path
from typing import Any, Dict, List, Tuple


class GitManager:
    """Manages git operations for voice-driven development."""

    def __init__(self, repo_path: str = ".") -> None:
        """Initialize with repository path."""
        self.repo_path: Path = Path(repo_path).resolve()

    async def _run_git(self, *args: str) -> Tuple[str, str, int]:
        """Run a git command and return (stdout, stderr, returncode)."""
        process = await asyncio.create_subprocess_exec(
            "git",
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(self.repo_path),
        )
        stdout, stderr = await process.communicate()
        returncode = process.returncode if process.returncode is not None else -1
        return (
            stdout.decode().strip(),
            stderr.decode().strip(),
            returncode,
        )

    async def status(self) -> Dict[str, Any]:
        """Get repository status.

        Returns dict with 'branch', 'clean', and 'output' keys.
        """
        stdout, stderr, returncode = await self._run_git("status", "--porcelain", "-b")
        if returncode != 0:
            return {"branch": "", "clean": False, "output": stderr, "error": True}

        lines = stdout.splitlines()
        branch = ""
        if lines and lines[0].startswith("##"):
            branch_info = lines[0][3:]
            branch = branch_info.split("...")[0] if "..." in branch_info else branch_info

        # Lines after the branch header are file changes
        changes = [line for line in lines[1:] if line.strip()]
        return {
            "branch": branch,
            "clean": len(changes) == 0,
            "output": stdout,
        }

    async def diff(self, staged: bool = False) -> str:
        """Get diff output.

        If staged=True, show staged changes.
        """
        args = ["diff", "--staged"] if staged else ["diff"]
        stdout, stderr, returncode = await self._run_git(*args)
        if returncode != 0:
            return stderr or "Error getting diff"
        return stdout

    async def log(self, count: int = 10) -> List[Dict[str, str]]:
        """Get recent commit log.

        Returns list of dicts with 'hash', 'author', 'date', and 'message' keys.
        """
        stdout, stderr, returncode = await self._run_git(
            "log",
            f"-{count}",
            "--format=%H|%an|%ai|%s",
        )
        if returncode != 0:
            return []

        commits: List[Dict[str, str]] = []
        for line in stdout.splitlines():
            if not line.strip():
                continue
            parts = line.split("|", 3)
            if len(parts) == 4:
                commits.append({
                    "hash": parts[0],
                    "author": parts[1],
                    "date": parts[2],
                    "message": parts[3],
                })
        return commits

    async def branch_list(self) -> List[str]:
        """List branches."""
        stdout, stderr, returncode = await self._run_git("branch", "--list")
        if returncode != 0:
            return []

        branches: List[str] = []
        for line in stdout.splitlines():
            # Strip leading whitespace and the '* ' marker for current branch
            branch = line.strip().lstrip("* ")
            if branch:
                branches.append(branch)
        return branches

    async def current_branch(self) -> str:
        """Get current branch name."""
        stdout, stderr, returncode = await self._run_git(
            "rev-parse", "--abbrev-ref", "HEAD",
        )
        if returncode != 0:
            return ""
        return stdout

    async def commit(self, message: str) -> Dict[str, Any]:
        """Stage all changes and commit with message.

        Returns a dict with 'success' and 'output' or 'error' keys.
        """
        # Stage all changes
        _, stderr, returncode = await self._run_git("add", "-A")
        if returncode != 0:
            return {"success": False, "error": f"Failed to stage changes: {stderr}"}

        # Commit with the provided message
        stdout, stderr, returncode = await self._run_git("commit", "-m", message)
        if returncode != 0:
            return {"success": False, "error": stderr}

        return {"success": True, "output": stdout}

    async def create_branch(self, branch_name: str) -> Dict[str, Any]:
        """Create and switch to a new branch.

        Returns a dict with 'success' and 'branch' or 'error' keys.
        """
        stdout, stderr, returncode = await self._run_git(
            "checkout", "-b", branch_name,
        )
        if returncode != 0:
            return {"success": False, "error": stderr}

        return {"success": True, "branch": branch_name, "output": stdout}
