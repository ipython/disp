from .spark import repr_spark_context_html, repr_spark_session_html

def load_ipython_extension(ipython):
    """
    Load an extension with IPython that tells it how to represent specifc
    objects.
    """
    html = ipython.display_formatter.formatters['text/html']

    html.for_type_by_name('pyspark.context','SparkContext', repr_spark_context_html)
    html.for_type_by_name('pyspark.sql', 'SparkSession', repr_spark_session_html)



config_value = "disp"
shell_key = "extensions"
app_key = "InteractiveShellApp"

from os import path
import json


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
    except (FileNotFoundError, json.decoder.JSONDecodeError):
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

    if get_ipython() is None:
        log.warning(_default_warning + json_path)

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
