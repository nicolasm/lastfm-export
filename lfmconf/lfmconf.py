import yaml
import os

XDG_CONFIG_HOME = os.environ['XDG_CONFIG_HOME']

with open('%s/lastfm-export/lastfm-export.yml' % XDG_CONFIG_HOME, 'r') as stream:
    conf = yaml.safe_load(stream)


def get_lastfm_conf():
    return conf
