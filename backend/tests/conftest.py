"""Top level pytest configuration for backend tests."""

from __future__ import annotations

pytest_plugins = [
    "backend.tests.shared.fixtures.api_fixtures",
    "backend.tests.shared.fixtures.db_fixtures",
    "backend.tests.shared.fixtures.mock_fixtures",
]
