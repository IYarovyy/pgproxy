import toml
import click
import psycopg2

from pgproxy.DbViewer import DbViewer
from pgproxy.TemplateProcessor import TemplateProcessor


@click.command()
@click.option("-c", "--config", "config_file", default="config.toml", help="Config file name.")
@click.option("-i", "--in", "in_folder", default="in", help="Input folder name.")
@click.option("-o", "--out", "out_folder", default="out", help="Output folder name.")
def cli(config_file, in_folder, out_folder):
    config = toml.load(config_file)

    with psycopg2.connect(dbname=config["database"]["name"], user=config["database"]["user"],
                          password=config["database"]["password"], host=config["database"]["host"], port=config["database"]["port"]) as conn:
        db_viewer = DbViewer(config, conn)
        processor = TemplateProcessor(in_folder, out_folder, db_viewer)
        processor.run()


if __name__ == "__main__":
    cli()

