#!/usr/bin/env python

import hopcolony
from hopcolony import auth
import typer, yaml

app = typer.Typer()

@app.command()
def login():
    hopcolony.initialize(username="core@hopcolony.io", project="core", token="supersecret")
    client = auth.client()
    auth_result = client.sign_in_with_hopcolony(scopes=["projects"])
    if auth_result.success:
        if not auth_result.user.projects:
            hopcolony.HopConfig(username=auth_result.user.email).commit()
            typer.secho("You have no projects yet. Create one at https://console.hopcolony.io", fg = typer.colors.YELLOW)
        else:
            typer.echo(f"Welcome {auth_result.user.name}! Please, select the project:")
            project = client.select_project(auth_result.user)
            if not project:
                typer.secho(f"Something went wrong retrieving the projects. Contact your administrator", err=True, fg = typer.colors.RED)
                return 
            project.commit()
            typer.secho(f"Successfully configured \"{project.project}\" project", fg = typer.colors.GREEN)
    else:
        typer.secho(auth_result.reason, err=True, fg = typer.colors.RED)

def load():
    try:
        hopcolony.initialize()
    except hopcolony.ConfigNotFound as e:
        pass
    except yaml.scanner.ScannerError as e:
        typer.secho("Check the format of your settings file", err = True, fg = typer.colors.RED)
        raise typer.Exit(code=1)

def main():
    load()
    # Import here so that the config is loaded when the modules come up
    from hopcolony.hopctl import config, jobs, get, describe
    app.add_typer(config.app, name="config")
    app.add_typer(jobs.app, name="jobs")
    app.add_typer(get.app, name="get")
    app.add_typer(describe.app, name="describe")
    app()

if __name__ == "__main__":
    main()