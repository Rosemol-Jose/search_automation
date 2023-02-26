import configparser
import os


def get_value():
    config = configparser.RawConfigParser()
    target_dir = os.path.join(os.getcwd(), ".\configuration\config.cfg")
    config.read(target_dir)
    details_dict = dict(config.items('DETAILS'))
    #print(details_dict["brand_check"])
    return details_dict


if __name__ == "__main__":
    get_value()
