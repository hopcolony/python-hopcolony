import typer
import yaml
from typing import Optional
import hopcolony

app = typer.Typer()
cfg = hopcolony.config()


def echo(json):
    missing = []
    for key, value in json.items():
        fg = typer.colors.WHITE
        if not value:
            fg = typer.colors.RED
            missing.append(key)

        typer.secho(f"{key}: {value}", fg=fg)

    if "username" in missing:
        cmd = typer.style("hopctl login", fg=typer.colors.YELLOW)
        typer.echo(f"\nRemember to login with: {cmd}")
        return
    if "project" in missing:
        typer.secho(
            "\nYou have no projects yet. Create one at https://console.hopcolony.io", fg=typer.colors.YELLOW)
        return


@app.command()
def get():
    if cfg:
        echo(cfg.json)
    else:
        typer.secho("Hop Config not found. Run 'hopctl login' or place a .hop.config file here.",
                    err=True, fg=typer.colors.RED)


def commit(config):
    json = config.commit()
    typer.secho(f"Updated config!\n", fg=typer.colors.GREEN)
    echo(json)


@app.command()
def set(username: Optional[str] = None, project: Optional[str] = None,
        token: Optional[str] = None, file: Optional[str] = None):

    if not username and not project and not token and not file:
        typer.secho(f"Nothing to set", err=True, fg=typer.colors.RED)
        raise typer.Exit(code=1)

    if file:
        try:
            config = hopcolony.HopConfig.fromFile(file)
            commit(config)
            raise typer.Exit()
        except FileNotFoundError:
            typer.secho(
                f"Could not find the file {file}", err=True, fg=typer.colors.RED)
            raise typer.Exit(code=1)

    config = hopcolony.HopConfig.update(
        username=username, project=project, token=token)
    commit(config)
    raise typer.Exit()


if __name__ == "__main__":
    app()
