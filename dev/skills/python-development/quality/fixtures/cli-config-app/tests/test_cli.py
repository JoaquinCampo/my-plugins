"""Tests for the CLI fixture."""

from pathlib import Path

from typer.testing import CliRunner  # type: ignore[import-not-found]

from demo_cli_app.cli import app  # type: ignore[import-not-found]

runner = CliRunner()


def test_cli_prints_normalized_json(tmp_path: Path) -> None:
    """The CLI writes machine-readable output to stdout."""
    config_path = tmp_path / "config.json"
    config_path.write_text('{"Name": "Ada"}', encoding="utf-8")

    result = runner.invoke(app, [str(config_path), "--env-prefix", "APP"])

    assert result.exit_code == 0
    assert result.stdout == '{"env_prefix": "APP", "name": "Ada"}\n'
    assert result.stderr == ""


def test_cli_reads_environment_settings(tmp_path: Path, monkeypatch) -> None:
    """Environment-backed settings are loaded through pydantic-settings."""
    config_path = tmp_path / "config.json"
    config_path.write_text('{"Name": "Ada"}', encoding="utf-8")
    monkeypatch.setenv("DEMO_ENV_PREFIX", "ENV")

    result = runner.invoke(app, [str(config_path)])

    assert result.exit_code == 0
    assert result.stdout == '{"env_prefix": "ENV", "name": "Ada"}\n'
    assert result.stderr == ""


def test_cli_reports_config_errors_on_stderr(tmp_path: Path) -> None:
    """Malformed JSON returns a nonzero exit and stderr diagnostic."""
    config_path = tmp_path / "config.json"
    config_path.write_text("not json", encoding="utf-8")

    result = runner.invoke(app, [str(config_path)])

    assert result.exit_code == 2
    assert result.stdout == ""
    assert "invalid JSON config" in result.stderr
