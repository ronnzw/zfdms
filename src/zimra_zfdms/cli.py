"""Console script for zimra_zfdms."""

import typer
from rich.console import Console

from zimra_zfdms import utils

app = typer.Typer()
console = Console()


@app.command()
def main():
    """Console script for zimra_zfdms."""
    console.print("Replace this message by putting your code into "
               "zimra_zfdms.cli.main")
    console.print("See Typer documentation at https://typer.tiangolo.com/")
    utils.do_something_useful()


if __name__ == "__main__":
    app()
