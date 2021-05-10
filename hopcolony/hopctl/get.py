import typer
from tabulate import tabulate
import hopcolony

from hopcolony import auth, docs, drive

app = typer.Typer()


@app.command()
def user():
    try:
        client = auth.client()
    except hopcolony.ConfigNotFound as e:
        typer.secho(str(e), err=True, fg=typer.colors.RED)
        raise typer.Exit(code=1)
    users = client.get()
    users = tabulate([user.printable for user in users],
                     headers=auth.HopUser.printable_headers)
    typer.echo(users)


@app.command()
def index():
    try:
        client = docs.client()
    except hopcolony.ConfigNotFound as e:
        typer.secho(str(e), err=True, fg=typer.colors.RED)
        raise typer.Exit(code=1)
    indices = client.get()
    indices = tabulate([index.printable for index in indices],
                       headers=docs.Index.printable_headers)
    typer.echo(indices)


@app.command()
def bucket():
    try:
        client = drive.client()
    except hopcolony.ConfigNotFound as e:
        typer.secho(str(e), err=True, fg=typer.colors.RED)
        raise typer.Exit(code=1)
    buckets = client.get()
    buckets = tabulate([bucket.printable for bucket in buckets],
                       headers=drive.Bucket.printable_headers)
    typer.echo(buckets)


if __name__ == "__main__":
    app()
