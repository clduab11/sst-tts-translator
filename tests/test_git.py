"""Tests for Git integration module."""

import pytest
from sst_tts_translator.git import GitManager


@pytest.mark.asyncio
async def test_git_manager_initialization():
    """Test GitManager initialization."""
    gm = GitManager()
    assert gm.repo_path.is_absolute()


@pytest.mark.asyncio
async def test_git_status():
    """Test getting git status in the current repo."""
    gm = GitManager(".")
    result = await gm.status()
    assert "branch" in result
    assert "clean" in result
    assert isinstance(result["clean"], bool)


@pytest.mark.asyncio
async def test_git_current_branch():
    """Test getting current branch name."""
    gm = GitManager(".")
    branch = await gm.current_branch()
    assert isinstance(branch, str)
    assert len(branch) > 0


@pytest.mark.asyncio
async def test_git_log():
    """Test getting commit log."""
    gm = GitManager(".")
    commits = await gm.log(count=5)
    assert isinstance(commits, list)
    if commits:
        assert "hash" in commits[0]
        assert "author" in commits[0]
        assert "date" in commits[0]
        assert "message" in commits[0]


@pytest.mark.asyncio
async def test_git_branch_list():
    """Test listing branches."""
    gm = GitManager(".")
    branches = await gm.branch_list()
    assert isinstance(branches, list)
    assert len(branches) > 0


@pytest.mark.asyncio
async def test_git_diff():
    """Test getting diff."""
    gm = GitManager(".")
    diff = await gm.diff()
    assert isinstance(diff, str)


@pytest.mark.asyncio
async def test_git_diff_staged():
    """Test getting staged diff."""
    gm = GitManager(".")
    diff = await gm.diff(staged=True)
    assert isinstance(diff, str)


@pytest.mark.asyncio
async def test_git_status_invalid_path():
    """Test git status with invalid repo path returns error."""
    gm = GitManager("/tmp/nonexistent_repo_path_xyz")
    result = await gm.status()
    assert result.get("error") is True
