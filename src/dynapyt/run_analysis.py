import argparse
import importlib
from os.path import abspath
from os import environ
import sys
import signal

parser = argparse.ArgumentParser()
parser.add_argument(
    "--entry", help="Entry file for execution")
parser.add_argument(
    "--analysis", help="Analysis class name")
parser.add_argument(
    "--module", help="Adds external module paths")
parser.add_argument(
    "--name", help="Associates a given name with current run"
)
parser.add_argument(
    "--django", help="Runs django setup before running analysis", action="store_true"
)
parser.add_argument(
    "--django-settings", help="Settings file path for django"
)

import dynapyt.runtime as rt

if __name__ == '__main__':
    args = parser.parse_args()
    additional_module = args.module
    name = args.name
    analysis = args.analysis
    modulePath = 'dynapyt.analyses'
    if additional_module is not None:
        modulePath = additional_module
    try:
        module = importlib.import_module(modulePath + '.' + analysis)
    except TypeError as e:
        print(f'--module was used but no value specified {e}')
    except ImportError as e:
        print(f'module could not be imported {e}')

    if args.django:
        django_settings = args.django_settings
        if django_settings is not None:
            environ['DJANGO_SETTINGS_MODULE'] = django_settings
        try:
            import django
            django.setup()
        except ImportError as e:
            print(f'Could not import django {e}')
            exit(1)

    class_ = getattr(module, args.analysis)
    my_analysis = class_()
    rt.set_analysis(my_analysis)

    def end_execution():
        try:
            func = getattr(my_analysis, 'end_execution')
            func()
        except AttributeError:
            pass

    # allow dynapyt to exit gracefully
    # Note: this will almost certainly not work on Windows
    signal.signal(signal.SIGINT, end_execution)
    signal.signal(signal.SIGTERM, end_execution)

    if not name is None:
        getattr(my_analysis, 'add_metadata', lambda: None)({"name": name})

    try:
        func = getattr(my_analysis, 'begin_execution')
        func()
    except AttributeError:
        pass
    if args.entry.endswith('.py'):
        sys.argv = [args.entry]
        exec(open(abspath(args.entry)).read())
    else:
        importlib.import_module(args.entry, '*')
    end_execution()