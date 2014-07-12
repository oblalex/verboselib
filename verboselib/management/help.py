# -*- coding: utf-8 -*-
"""
List available commands or show help for a particular command.
"""
from verboselib.management import get_commands, print_out, print_err

__usage__ = 'help [<command>]'


def execute(args=None):
    if args:
        command = args[0]
        commands = get_commands()
        if command in commands:
            print_module_help(commands[command])
        else:
            print_err("Unknown command '{:}'.".format(command))
            _list_commands()
    else:
        _list_commands()


def print_module_help(module):
    messages = []

    usage = getattr(module, '__usage__', None)
    if usage:
        messages.append("Usage:")
        messages.append(usage.strip())
        messages.append("")

    description = _description(module)
    if description:
        messages.append("Description:")
        messages.append(_description(module))
    else:
        messages.append("No description.")

    print_out('\n'.join(messages))


def _list_commands():
    messages = [
        "Available commands:",
        "",
    ]
    commands = get_commands()
    for name in sorted(commands.keys()):
        module = commands[name]
        description = _description(module)
        if description:
            message = "{:} ({:})".format(name, description.split('\n')[0])
        else:
            message = name
        messages.append("    - " + message)

    print_out('\n'.join(messages))


_description = lambda module: module.__doc__.strip() if module.__doc__ else None
