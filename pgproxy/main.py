import toml
import click
import psycopg2

from pgproxy.DbViewer import DbViewer


@click.command()
@click.option("-c", "--config", "config_file", default="config.toml", help="Config file name.")
def cli(config_file):
    config = toml.load(config_file)

    with psycopg2.connect(dbname=config["database"]["name"], user=config["database"]["user"],
                          password=config["database"]["password"], host=config["database"]["host"], port=config["database"]["port"]) as conn:
        db_viewer = DbViewer(config, conn)
        # print(db_viewer.schemas())
        print(db_viewer.procs("api"))
        # print(db_viewer.args("api", "common_user_insert"))


if __name__ == "__main__":
    cli()

