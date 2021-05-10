import typer
import yaml
from typing import Optional
from tabulate import tabulate
import hopcolony

from hopcolony import auth, docs, drive

app = typer.Typer()


@app.command()
def user(uuid: str):
    try:
        client = auth.client()
    except hopcolony.ConfigNotFound as e:
        typer.secho(str(e), err=True, fg=typer.colors.RED)
        raise typer.Exit(code=1)
    snapshot = client.user(uuid).get()
    if snapshot.success:
        typer.echo(yaml.dump(snapshot.doc.source))
    else:
        typer.secho(f"User \"{uuid}\" not found", fg=typer.colors.RED)


@app.command()
def index(name: str, cols: str = None, doc: Optional[str] = None):
    try:
        client = docs.client()
    except hopcolony.ConfigNotFound as e:
        typer.secho(str(e), err=True, fg=typer.colors.RED)
        raise typer.Exit(code=1)
    if not doc:
        # Print all the documents in the index
        snapshot = client.index(name).get()
        if snapshot.success:
            columns = cols.split(',') if cols else []
            documents = tabulate([doc.printable(
                columns) for doc in snapshot.docs], headers=docs.Document.printable_headers(columns))
            typer.echo(documents)
        else:
            typer.secho(f"Index \"{name}\" not found", fg=typer.colors.RED)
    else:
        # Print the desired document
        snapshot = client.index(name).document(doc).get()
        if snapshot.success:
            typer.echo(yaml.dump(snapshot.doc.source))
        else:
            typer.secho(
                f"Document \"{doc}\" not found in index {name}", fg=typer.colors.RED)


@app.command()
def bucket(name: str, obj: Optional[str] = None):
    try:
        client = drive.client()
    except hopcolony.ConfigNotFound as e:
        typer.secho(str(e), err=True, fg=typer.colors.RED)
        raise typer.Exit(code=1)
    if not obj:
        # Print all the objects in the bucket
        snapshot = client.bucket(name).get()
        if snapshot.success:
            objects = tabulate(
                [object.printable for object in snapshot.objects], headers=drive.Object.printable_headers)
            typer.echo(objects)
        else:
            typer.secho(f"Bucket \"{name}\" not found", fg=typer.colors.RED)
    else:
        # Print the desired object
        snapshot = client.bucket(name).get()
        if snapshot.success:
            matching = [
                object for object in snapshot.objects if object.id == obj]
            if not matching:
                typer.secho(
                    f"Object \"{obj}\" not found in index {name}", fg=typer.colors.RED)
                raise typer.Exit()
            typer.echo(yaml.dump(matching[0].json))
        else:
            typer.secho(
                f"Object \"{obj}\" not found in index {name}", fg=typer.colors.RED)


@app.command()
def doc(uuid: str):
    try:
        client = docs.client()
    except hopcolony.ConfigNotFound as e:
        typer.secho(str(e), err=True, fg=typer.colors.RED)
        raise typer.Exit(code=1)
    snapshot = client.index(name).document(uuid).get()
    if snapshot.success:
        typer.echo(yaml.dump(snapshot.doc.source))
    else:
        typer.secho(f"Document \"{uuid}\" not found", fg=typer.colors.RED)


if __name__ == "__main__":
    app()
