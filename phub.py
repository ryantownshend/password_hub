"""
phub.py commandline password storage utility.


For the first round lets get the file sorted, then cipher it

- initialize local storage file
~/phub.yaml


"""

import os
import sys
import logging
import click
import click_log
import yaml
import pyperclip
from password_hub import PasswordHub

log = logging.getLogger(__name__)
click_log.basic_config(log)


def check_file_populated(filename):
    """check if the filename exists and has data."""
    exists = False
    try:
        size = os.path.getsize(filename)
        if size > 0:
            exists = True

    except FileNotFoundError:
        exists = False

    return exists


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
@click.pass_context
@click_log.simple_verbosity_option()
def cli(
    ctx,
    phub_file,
    phub_config_file,
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

    password = None

    if not check_file_populated(phub_file):

        password = click.prompt(
            "Create file password",
            hide_input=True,
            confirmation_prompt=True
        )

    else:
        password = click.prompt("Password", hide_input=True)

    try:
        ctx.obj = PasswordHub(config, phub_file, password)
        log.debug('ctx.obj : %s' % ctx)
    except IOError:
        # log.error(ioe)
        sys.exit(5)


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
@click.pass_obj
def edit_entry(ctx):
    log.debug('edit_entry()')

    # log.debug('   entry : %s' % entry)
    # log.debug('username : %s' % username)
    # log.debug('password : %s' % password)
    entry = click.prompt('Entry to edit')
    entries = ctx.find_entries(entry)
    print("len : %d" % len(entries))
    if len(entries) > 1:
        count = 0
        for item in entries:
            click.echo("(%d) %s" % (count, item['entry']))
            count += 1
        select = click.prompt("Select", type=int)
        click.echo(select)
        edit_entry_object(entries[select])
        ctx.save_data()

    elif len(entries) == 1:
        edit_entry_object(entries[0])
        ctx.save_data()


def edit_entry_object(entry):

    entry['entry'] = click.prompt(
        entry['entry'],
        default=entry['entry']
    )
    entry['username'] = click.prompt(
        entry['username'],
        default=entry['username']
    )
    entry['password'] = click.prompt(
        entry['password'],
        default=entry['password']
    )

    # try:
    #     ctx.edit_entry(entry, username, password)
    # except ValueError as verr:
    #     click.secho(str(verr), fg='red')


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


@cli.command('export', help="Dump entries list as yaml")
@click.pass_obj
def export_entries(ctx):
    """export entries."""
    log.debug('export_entries')
    print(ctx.data_to_yaml())


@cli.command('import', help="Import yaml entries list")
@click.pass_obj
def import_entries(ctx):
    """export entries."""
    log.debug('import_entries')
    print(ctx.yaml_to_data())


@cli.command('editfile', help="edit entries yaml in editor")
@click.pass_obj
def edit_file(ctx):
    """export entries."""
    log.debug('editfile')
    yaml_data = ctx.data_to_yaml()

    modified = click.edit(
        text=yaml_data,
        require_save=True,
        extension=".yaml",
    )

    print(modified)
    yaml_object = ctx.yaml_to_data(modified)
    ctx.data = yaml_object
    ctx.save_data()


if __name__ == '__main__':
    cli()
