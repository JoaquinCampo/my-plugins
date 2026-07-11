"""Small Typer CLI with config precedence for skill evaluation."""

import json
from pathlib import Path

import typer  # type: ignore[import-not-found]
from pydantic import TypeAdapter, ValidationError
from pydantic_settings import (  # type: ignore[import-not-found]
    BaseSettings,
    SettingsConfigDict,
)

JsonConfig = dict[str, object]
CONFIG_ADAPTER = TypeAdapter(JsonConfig)

app = typer.Typer(add_completion=False, no_args_is_help=True)


class CliSettings(BaseSettings):
    """Environment-backed CLI settings."""

    model_config = SettingsConfigDict(env_prefix="DEMO_")

    env_prefix: str | None = None


def load_config(path: Path) -> JsonConfig:
    """Load a JSON object from a config path."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON config: {path}") from exc

    try:
        return CONFIG_ADAPTER.validate_python(data)
    except ValidationError as exc:
        raise ValueError("config must be a JSON object") from exc


def normalize_config(
    config: JsonConfig, *, env_prefix: str | None = None
) -> JsonConfig:
    """Return a normalized config with optional environment prefix override."""
    normalized: JsonConfig = {str(key).lower(): value for key, value in config.items()}
    if env_prefix is not None:
        normalized["env_prefix"] = env_prefix
    return normalized


@app.command()
def main(
    config: Path,
    env_prefix: str | None = typer.Option(None, "--env-prefix"),
) -> None:
    """Print normalized JSON for a config file."""
    settings = CliSettings()
    resolved_env_prefix = env_prefix if env_prefix is not None else settings.env_prefix
    try:
        normalized = normalize_config(
            load_config(config), env_prefix=resolved_env_prefix
        )
    except ValueError as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(2) from exc

    typer.echo(json.dumps(normalized, sort_keys=True))


def cli() -> None:
    """CLI entry point."""
    app()
