import yaml


with open("config.yml", "r") as ymlfile:
    cfg = yaml.safe_load(ymlfile)

for section in cfg:
    print(section)

for key in cfg["keys"]:
    print(key)
    print(cfg["keys"][key])