# coding: utf-8
"""
Rich display for a variety of Python objects.

Use the followign to enable permanently.

>>> import disp; disp.install()


The following activate rich repr on a couple of builtins types:

    - functions/methods
    - types
    - modules

>>> import disp; disp.activate_builtins()

As this may have side-effect the setting does not persist across sessions


Some object are not enabled by default, you can activate with:

>>> import disp; disp.activate_for(something)

For example, a `requests`'s response. 

>>> import requests
>>> response = requests.get(...)
>>> disp.activate+for(response)
>>> response


"""

import sys
import json
from os import path

from IPython import get_ipython, paths
from .spark import repr_spark_context_html, repr_spark_session_html

if sys.version_info < (3,):
    FileNotFoundError = IOError
    JSONDecodeError = ValueError
else:
    from json.decoder import JSONDecodeError


def load_ipython_extension(ipython):
    """
    Load an extension with IPython that tells it how to represent specifc
    objects.
    """
    html = ipython.display_formatter.formatters['text/html']

    html.for_type_by_name('pyspark.context','SparkContext', repr_spark_context_html)
    html.for_type_by_name('pyspark.sql', 'SparkSession', repr_spark_session_html)


def activate_builtins():
    """
    Install html_repr for a couple of the builtin
    """
    if sys.version_info > (3, 6):
        ipython = get_ipython()
        html = ipython.display_formatter.formatters['text/html']
        import types
        from .py3only import html_formatter_for_builtin_function_or_method, html_formatter_for_type, html_formatter_for_module
        html.for_type(types.FunctionType, html_formatter_for_builtin_function_or_method)
        html.for_type(types.BuiltinFunctionType, html_formatter_for_builtin_function_or_method)
        html.for_type(types.BuiltinMethodType, html_formatter_for_builtin_function_or_method)
        html.for_type(types.MethodType, html_formatter_for_builtin_function_or_method)
        html.for_type(types.ModuleType, html_formatter_for_module)

        html.for_type(type, html_formatter_for_type)


def activate_for(obj):
    ip = get_ipython()
    html = ip.display_formatter.formatters['text/html']

    if sys.version_info < (3,6):
        raise RuntimeError('Sorry need python 3.6 or greater')
    else:
        from . import py3only
    if type(obj) is type:
        target = obj
    else:
        target = type(obj)

    attr = getattr(py3only, 'html_formatter_for_'+target.__name__.replace('.', '_'))
    html.for_type(target, attr)

def gen_help(obj):
    ip = get_ipython()
    from . import py3only
    html = ip.display_formatter.formatters['text/html']
    html.for_type(type(obj), py3only.gen_help)


    

config_value = "disp"
shell_key = "extensions"
app_key = "InteractiveShellApp"

def get_config():
    ip = get_ipython()

    if ip is None:
        profile_dir = paths.locate_profile()
    else:
        profile_dir = ip.profile_dir.location

    json_path = path.join(profile_dir, "ipython_config.json")

    try:
        with open(json_path, 'r') as f:
            config = json.load(f)
    except (FileNotFoundError, JSONDecodeError):
        config = {}
    return config, json_path



def install():
    """Register `disp` as a default extension for IPython.

    When you run this inside IPython, the preference gets applied to the
    current IPython profile. When run using plain Python, the preference gets
    applied to the default profile.

    Run `uninstall()` if you ever change your mind and want to revert to the
    default IPython behavior.
    """

    cfg, json_path = get_config()

    installed = config_value in cfg.get(app_key, {}).get(shell_key, [])

    if installed:
        print("😕 Looks like disp is already installed.😕")
        return

    with open(json_path, 'w') as f:
        x = cfg.get(app_key, {}).get(shell_key, [])
        x.append(config_value)
        cfg.update({app_key: {shell_key: x}})
        json.dump(cfg, f)

    print("💖 Installation succeeded: enjoy disp ! 💖")

def uninstall():
    cfg, json_path = get_config()
    if config_value not in cfg.get(app_key, {}).get(shell_key, []):
        print('😕 Disp is not installed. Aborting. 😕')
        return
    with open(json_path, 'w') as f:
        cfg.get(app_key, {}).get(shell_key).remove(config_value)
        json.dump(cfg, f)

    print(" 💖 Uninstalled disp. 😢")
