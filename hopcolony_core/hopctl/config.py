import typer, yaml
from typing import Optional
import hopcolony_core

app = typer.Typer()
cfg = hopcolony_core.config()

def echo(json):
    missing = False
    for key, value in json.items():
        fg = typer.colors.WHITE 
        if not value:
            fg = typer.colors.RED
            missing = True

        typer.secho(f"{key}: {value}", fg = fg)

    if missing:
        cmd = typer.style("hopctl config set", fg = typer.colors.YELLOW)
        typer.echo(f"\nRemember to set the missing values with: {cmd}")

@app.command()
def get():
    echo(cfg.json)

def commit(config):
    json = config.commit()
    typer.secho(f"Updated config!\n", fg = typer.colors.GREEN)
    echo(json)

@app.command()
def set(app: Optional[str] = None, project: Optional[str] = None,
        token: Optional[str] = None, file: Optional[str] = None):
    
    if not app and not project and not token and not file:
        typer.secho(f"Nothing to set", err = True, fg=typer.colors.RED)
        raise typer.Exit(code=1)

    if file:
        try:
            config = hopcolony_core.HopConfig.fromFile(file)
            commit(config)
            raise typer.Exit()
        except FileNotFoundError:
            typer.secho(f"Could not find the file {file}", err = True, fg=typer.colors.RED)
            raise typer.Exit(code=1)
    
    config = hopcolony_core.HopConfig.update(app = app, project = project, token = token)
    commit(config)
    raise typer.Exit()

if __name__ == "__main__":
    app()