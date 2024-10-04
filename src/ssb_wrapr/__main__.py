"""Command-line interface."""

import click


@click.command()
@click.version_option()
def main() -> None:
    """SSB WrapR."""


if __name__ == "__main__":
    main(prog_name="ssb-wrapr")  # pragma: no cover
