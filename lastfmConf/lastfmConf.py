import yaml

with open('lastfm-export.yml', 'r') as stream:
    conf = yaml.safe_load(stream)


def get_lastfm_conf():
    return conf
