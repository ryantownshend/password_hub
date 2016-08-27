"""
phub.py commandline password storage utility.


For the first round lets get the file sorted, then cipher it

- initialize local storage file
~/phub.yaml


"""

import os
import logging
import click
import click_log
import yaml
import pyperclip
from password_hub import PasswordHub

log = logging.getLogger()


def load_config(phub_config_file):
    """
    initialize / load config file.
    """
    log.debug('config %s' % phub_config_file)
    product = {}

    if os.path.isfile(phub_config_file):
        try:
            with open(phub_config_file, 'r') as f:
                product = yaml.load(f.read())

            if product is '':
                product = {}

        except yaml.YAMLError as exc:
            log.error("Error in data file: %s" % exc)

    return product


def save_config(config_dict, phub_config_file):
    """save config data."""
    log.debug('save_config')

    yaml_data = yaml.dump(config_dict, default_flow_style=False)
    with open(phub_config_file, 'w') as f:
        f.write(yaml_data)
    f.close()


@click.group()
@click.option(
    '--file',
    'phub_file',
    default='DEFAULT',
    type=click.Path(),
    help="phub yaml file, defaults to ~/phub.yaml",
)
@click.option(
    '--config',
    'phub_config_file',
    default='DEFAULT',
    type=click.Path(),
    help="phub config yaml file, defaults to ~/phub_config.yaml",
)
@click.option(
    '--password',
    prompt=True,
    hide_input=True
)
@click.pass_context
@click_log.simple_verbosity_option()
@click_log.init(log)
def cli(
    ctx,
    phub_file,
    phub_config_file,
    password,
):
    """Storage and retrieval of login details."""
    log.debug('cli')

    if phub_config_file in 'DEFAULT':
        phub_config_file = os.path.expanduser("~/phub_config.yaml")
        log.debug("phub_config_file : %s" % phub_config_file)

    if phub_file in 'DEFAULT':
        phub_file = os.path.expanduser("~/phub.yaml")
        log.debug("phub_file : %s" % phub_file)

    config = load_config(phub_config_file)

    salt = None
    if 'salt' in config:
        salt = config['salt']
    else:
        salt = os.urandom(16)
        config['salt'] = salt
        save_config(config, phub_config_file)

    ctx.obj = PasswordHub(config, phub_file, password)
    log.debug('ctx.obj : %s' % ctx)


@cli.command('list', help="List all entries")
@click.pass_obj
def list_entries(ctx):
    data = ctx.list_entries()
    click.secho("entries list :", fg='green')
    for item in data:
        click.echo(item)


@cli.command('create', help="Create new entry")
@click.option(
    '--entry',
    prompt="Enter asset"
)
@click.option(
    '--username',
    prompt=True
)
@click.option(
    '--password',
    prompt="Password",
    hide_input=True,
    confirmation_prompt=True
)
@click.pass_obj
def create_entry(ctx, entry, username, password):
    log.debug('create_entry()')

    log.debug('   entry : %s' % entry)
    log.debug('username : %s' % username)
    log.debug('password : %s' % password)

    try:
        ctx.create_entry(entry, username, password)
    except ValueError as verr:
        click.echo(verr)


@cli.command('edit', help="Edit existing entry")
@click.option(
    '--entry',
    prompt="Asset to edit"
)
@click.option(
    '--username',
    prompt=True
)
@click.option(
    '--password',
    prompt="Password",
    hide_input=True,
    confirmation_prompt=True
)
@click.pass_obj
def edit_entry(ctx, entry, username, password):
    log.debug('edit_entry()')

    log.debug('   entry : %s' % entry)
    log.debug('username : %s' % username)
    log.debug('password : %s' % password)

    try:
        ctx.edit_entry(entry, username, password)
    except ValueError as verr:
        click.secho(str(verr), fg='red')


@cli.command('get', help="Seek an entry")
@click.option(
    '--entry',
    prompt="Entry to seek"
)
@click.pass_obj
def get_entries(ctx, entry):
    log.debug('get : %s' % entry)
    log.debug('ctx : %s' % ctx)
    items = ctx.find_entries(entry)
    for item in items:
        click.echo(
            "   entry : %s" % click.style(item['entry'], fg='green')
        )
        click.echo(
            "username : %s" % item['username']
        )

    if len(items) == 1:
        click.echo('password copied to clipboard')
        pyperclip.copy(items[0]['password'])


if __name__ == '__main__':
    cli()
