import sys
import os

_this_path = __file__
_app_path = os.path.dirname(_this_path)
_proj_path = os.path.dirname(_app_path)
sys.path.append(_proj_path)

import click
import mintkit.config as cfg
import mintkit.utils.logging
import mintkit.core.tasks
import mintkit.web.tasks
import mintkit.auth.tasks


log = mintkit.utils.logging.get_logger(cfg.PROJECT_NAME)

_tasks = {'refresh': mintkit.core.tasks.refresh_accounts,
          'text': mintkit.core.tasks.send_spending_update_text,
          'setup-driver': mintkit.web.tasks.setup_chromedriver,
          'setup-creds': mintkit.auth.tasks.setup_credentials}


@click.command()
@click.option(
    "--task",
    type=click.Choice(_tasks.keys()),
    required=True,
    help="Name of task to execute."
)
def main_cli(task):
    """Run the specified task.

    """
    try:
        _tasks[task]()
    except Exception as e:
        log.exception(e)
        raise


if __name__ == "__main__":
    main_cli()
