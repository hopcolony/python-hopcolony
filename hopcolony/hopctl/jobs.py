import typer
import yaml
import os
import inspect
import sys
import json
import subprocess
import click_spinner
import requests
import time
from typing import Optional
import hopcolony
from hopcolony import jobs

app = typer.Typer()
cfg = hopcolony.config()


@app.command()
def create(name: str):
    try:
        os.mkdir(name)
    except FileExistsError as e:
        typer.secho(f"Project {name} already exists",
                    err=True, fg=typer.colors.RED)
        raise typer.Exit(code=1)
    with open(f"{name}/settings.yaml", "w") as f:
        f.write(jobs.default_settings.format(name))
    with open(f"{name}/pipelines.py", "w") as f:
        f.write(jobs.example_pipeline)
    os.mkdir(f"{name}/jobs")
    with open(f"{name}/jobs/example.py", "w") as f:
        f.write(jobs.example_job)

    typer.secho(f"New project created!", fg=typer.colors.GREEN)
    cmd = typer.style(
        f"hopctl jobs run example --project {name}", fg=typer.colors.YELLOW, bold=True)
    typer.echo(f"Run {cmd} to run the example.")


class Pipeline:
    def __init__(self, name, args={}, is_custom=False):
        self.name = name
        self.args = args
        self.is_custom = is_custom
        self.cls = None

        # Find the pipeline cls
        modules = sys.modules[__name__ if is_custom else "hopcolony.jobs"]
        for _, obj in inspect.getmembers(modules):
            if inspect.isclass(obj) and issubclass(obj, jobs.JobPipeline) and obj.name == name:
                self.cls = obj

    @classmethod
    def fromJson(cls, json):
        if type(json) == str:
            # No args passed to the pipeline
            return cls(json)

        assert len(json) == 1, "Invalid pipeline settings..."
        name, definition = next(iter(json.items()))
        definition = definition or {}
        if "custom" in definition and definition["custom"]:
            del definition["custom"]
            return cls(name, args=definition, is_custom=True)
        else:
            return cls(name, args=definition)

    def instanciate(self, job):
        return self.cls(job, **self.args)

    @property
    def error(self):
        return f"{self.name} not found in pipelines.py..." if self.is_custom else \
            f"{self.name} not found in built-in pipelines..."


@app.command()
def run(name: str, project: Optional[str] = ".", skip: Optional[bool] = False):
    # Read project settings
    try:
        with open(f"{project}/settings.yaml") as file:
            settings = yaml.load(file.read(), Loader=yaml.FullLoader)
    except FileNotFoundError as e:
        typer.secho(
            f"settings.yaml file not found on project {project}", err=True, fg=typer.colors.RED)
        raise typer.Exit(code=1)

    # Install the requirements if not skipped
    if not skip and name in settings and settings[name] and "requirements" in settings[name] and settings[name]["requirements"]:
        requirements = settings[name]["requirements"].strip().split(' ')
        with click_spinner.spinner():
            typer.echo(f"Installing requirements: {requirements}")
            try:
                with open(os.devnull, 'w') as devnull:
                    subprocess.check_call(
                        [sys.executable, "-m", "pip", "install", *requirements], stdout=devnull)
            except Exception as e:
                typer.secho(e, err=True, fg=typer.colors.RED)
                raise typer.Exit(code=1)

    # Load all the jobs and custom pipelines into memory
    try:
        for filename in os.listdir(f"{project}/jobs/"):
            with open(f"{project}/jobs/{filename}") as file:
                exec(file.read(), globals())

        with open(f"{project}/pipelines.py") as file:
            exec(file.read(), globals())
    except ModuleNotFoundError as e:
        typer.secho(f"{e.name} module(s) not found. Be sure to add them to the job settings in settings.yaml",
                    err=True, fg=typer.colors.RED)
        raise typer.Exit(code=1)
    except FileNotFoundError as e:
        pass
    except Exception as e:
        typer.secho(e, err=True, fg=typer.colors.RED)
        raise typer.Exit(code=1)

    # Get the classes for the pipelines
    pipelines = None
    if name in settings and settings[name] and "pipelines" in settings[name] and settings[name]["pipelines"]:
        pipelines = [Pipeline.fromJson(pipeline)
                     for pipeline in settings[name]["pipelines"]]
        for pipeline in pipelines:
            assert pipeline.cls != None, pipeline.error

    # Find the job class
    job_cls = None
    for _, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isclass(obj) and issubclass(obj, jobs.Job) and obj.name == name:
            assert job_cls == None, f"Duplicated job with name {name}"
            job_cls = obj
    assert job_cls != None, f"No job found with name {name}"

    # Find the args for the job
    args = {}
    if name in settings and settings[name] and "args" in settings[name] and settings[name]["args"]:
        args = settings[name]["args"]

    # Inistanciate the job, pipelines and engine
    job = job_cls(**args)
    pipelines = [pipeline.instanciate(job)
                 for pipeline in pipelines] if pipelines else []

    client = jobs.client()
    client.run(job, pipelines=pipelines)


def find_filename(name, project):
    found = None
    for filename in os.listdir(f"{project}/jobs/"):
        duplicity_counter = 0
        with open(f"{project}/jobs/{filename}") as file:
            exec(file.read(), globals())
            for _, obj in inspect.getmembers(sys.modules[__name__]):
                if inspect.isclass(obj) and issubclass(obj, jobs.Job) and obj.name == name:
                    if not found:
                        found = filename
                    duplicity_counter += 1
            assert duplicity_counter <= 1, f"Duplicated job with name {name}"

    return found


@app.command()
def deploy(name: str, project: Optional[str] = ".", schedule: Optional[str] = None):
    if not cfg.valid:
        typer.secho(f"Something is wrong with your config",
                    err=True, fg=typer.colors.RED)
        config.echo(cfg.json)
        raise typer.Exit(code=1)

    try:
        with open(f"{project}/settings.yaml") as file:
            settings = yaml.load(file.read(), Loader=yaml.FullLoader)
    except FileNotFoundError as e:
        typer.secho(
            f"settings.yaml file not found on project {project}", err=True, fg=typer.colors.RED)
        raise typer.Exit(code=1)

    # Find the source code for the desired job
    filename = find_filename(name, project)
    assert filename is not None, f"No job found with name {name}"
    with open(f"{project}/jobs/{filename}") as f:
        job_code = f.read()

    # Get custom pipelines code
    try:
        with open(f"{project}/pipelines.py") as f:
            pipelines_code = f.read()
    except:
        pipelines_code = ""

    try:
        jobs.client().deploy(name, job_code, pipelines=pipelines_code,
                             settings=settings, schedule=schedule)
    except jobs.ResourceAlreadyExists:
        typer.secho(f"Cron Job \"{name}\" already exists..",
                    err=True, fg=typer.colors.RED)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
