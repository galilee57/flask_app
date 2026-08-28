from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory


def test_alembic_revision_graph_has_a_single_head():
    repository_root = Path(__file__).resolve().parents[1]
    config = Config()
    config.set_main_option("script_location", str(repository_root / "migrations"))

    script = ScriptDirectory.from_config(config)
    assert tuple(script.get_heads()) == ("9ad4c7e0b812",)
