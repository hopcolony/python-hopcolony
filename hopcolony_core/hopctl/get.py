import typer 
from tabulate import tabulate
import hopcolony_core

from hopcolony_core import auth, docs, drive

app = typer.Typer()

@app.command()
def user():
    client = auth.client()
    users = client.get()
    users = tabulate([user.printable for user in users], headers=auth.HopUser.printable_headers)
    typer.echo(users)

@app.command()
def index():
    client = docs.client()
    indices = client.get()
    indices = tabulate([index.printable for index in indices], headers=docs.Index.printable_headers)
    typer.echo(indices)

@app.command()
def bucket():
    client = drive.client()
    buckets = client.get()
    buckets = tabulate([bucket.printable for bucket in buckets], headers=drive.Bucket.printable_headers)
    typer.echo(buckets)
    
if __name__ == "__main__":
    app()