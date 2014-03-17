import configobj
import os
import sys
from validate import Validator

# appPath = os.path.abspath(os.path.dirname(os.path.join(sys.argv[0])))
appPath = os.getcwd()
inifile = os.path.join(appPath, "settings.ini")


def create_config():
    """
    Create the configuration file
    """
    config = configobj.ConfigObj(unrepr=True)
    config.filename = inifile
    config['apikey'] = ''
    config['apisecret'] = ''
    config['tokenkey'] = ''
    config['tokensecret'] = ''
    config['transitname'] = 'TTCNotices'
    config.write()


def get_config():
    """
    Open the config file and return a configobj
    """
    if not os.path.exists(inifile):
        open(inifile, 'w').close()
        create_config()

    local_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
    if not os.path.exists(local_dir+'\\configspec.ini'):
        conf_ini = file(local_dir+'\\configspec.ini', 'w')
        conf_ini.write("apikey = string(default='')\n")
        conf_ini.write("apisecret = string(default='')\n")
        conf_ini.write("tokenkey = string(default='')\n")
        conf_ini.write("tokensecret = string(default='')\n")
        conf_ini.write("transitname = string(default='')\n")
        conf_ini.close()

    config = configobj.ConfigObj(inifile, unrepr=True, configspec=local_dir+'\\configspec.ini')
    validator = Validator()
    result = config.validate(validator)
    if result:
        return config
    else:
        raise Exception ("Config file is not valid.")
