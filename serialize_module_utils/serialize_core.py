import yaml

def serialize():
    with open("rtmbot.conf") as stream:
        return yaml.load(stream)