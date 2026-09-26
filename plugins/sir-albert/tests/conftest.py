"""Shared pytest fixtures for sir-albert hook tests."""
import shutil
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"
PLUGIN_ROOT = Path(__file__).parent.parent


@pytest.fixture
def plugin_root():
    return str(PLUGIN_ROOT)


@pytest.fixture
def tmp_project_gtm(tmp_path):
    shutil.copytree(FIXTURES_DIR / "project_gtm", tmp_path / "project_gtm")
    return tmp_path / "project_gtm"


@pytest.fixture
def tmp_project_n8n(tmp_path):
    shutil.copytree(FIXTURES_DIR / "project_n8n", tmp_path / "project_n8n")
    return tmp_path / "project_n8n"


@pytest.fixture
def tmp_project_kb(tmp_path):
    shutil.copytree(FIXTURES_DIR / "project_kb", tmp_path / "project_kb")
    return tmp_path / "project_kb"


@pytest.fixture
def tmp_project_plain(tmp_path):
    shutil.copytree(FIXTURES_DIR / "project_plain", tmp_path / "project_plain")
    return tmp_path / "project_plain"
