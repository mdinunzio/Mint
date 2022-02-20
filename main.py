import click
import mintkit.settings as cfg
import mintkit.logs
import mintkit.paths


log = mintkit.logs.get_logger(cfg.PROJECT_NAME)


def open_logs():
    """Open the log directory.

    """
    cfg.paths.logs.open()


def setup():
    """Setup the credentials and driver.

    """
    mintkit.paths.setup_template_path(cfg.paths)
    mintkit.web.tasks.setup_chromedriver()
    mintkit.auth.tasks.setup_credentials()


def setup_paths():
    """Setup all configurable paths.

    """
    mintkit.paths.setup_template_path(cfg.paths)


_tasks = {'refresh': mintkit.core.tasks.refresh_accounts,
          'text': mintkit.core.tasks.send_texts,
          'setup': setup,
          'setup-paths': setup_paths,
          'setup-driver': mintkit.web.tasks.setup_chromedriver,
          'setup-creds': mintkit.auth.tasks.setup_credentials,
          'setup-gmail': mintkit.gmail.tasks.setup_gmail_credentials,
          'logs': open_logs}


def main(task):
    """Run the specified task."""
    try:
        _tasks[task]()
    except Exception as e:
        log.exception(e)
        raise


@click.command()
@click.option(
    "--task",
    type=click.Choice(_tasks.keys()),
    required=True,
    help="Name of task to execute."
)
def main_cli(task):
    """Run the specified task."""
    main(task)


if __name__ == "__main__":
    main_cli()
