#!/usr/bin/env python

import hopcolony_core
import typer, yaml

app = typer.Typer()

def load():
    try:
        hopcolony_core.initialize()
    except hopcolony_core.ConfigNotFound as e:
        pass
    except yaml.scanner.ScannerError as e:
        typer.secho("Check the format of your settings file", err = True, fg = typer.colors.RED)
        raise typer.Exit(code=1)

def main():
    load()
    # Import here so that the config is loaded when the modules come up
    from hopcolony_core.hopctl import config, jobs, get, describe
    app.add_typer(config.app, name="config")
    app.add_typer(jobs.app, name="jobs")
    app.add_typer(get.app, name="get")
    app.add_typer(describe.app, name="describe")
    app()

if __name__ == "__main__":
    main()