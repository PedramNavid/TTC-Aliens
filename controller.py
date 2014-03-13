import configobj
import os
import sys
from validate import Validator

appPath = os.path.abspath(os.path.dirname(os.path.join(sys.argv[0])))
inifile = os.path.join(appPath, "settings.ini")


def createConfig():
    """
    Create the configuration file
    """
    config = configobj.ConfigObj(unrepr=True)
    config.filename = inifile
    config['apikey'] = False
    config['apisecret'] = False
    config['tokenkey'] = False
    config['tokensecret'] = False
    config['transitname'] = 'TTCNotices'
    config.write()


def getConfig():
    """
    Open the config file and return a configobj
    """
    if not os.path.exists(inifile):
        open(inifile, 'w').close()
        createConfig()

    localDir = os.path.dirname(os.path.realpath(sys.argv[0]))
    if not os.path.exists(localDir+'\\configspec.ini'):
        conf_ini = file(localDir+'\\configspec.ini', 'w')
        conf_ini.write("apikey = boolean(default=False)\n")
        conf_ini.write("apisecret = boolean(default=False)\n")
        conf_ini.write("tokenkey = boolean(default=False)\n")
        conf_ini.write("tokensecret = boolean(default=False)\n")
        conf_ini.write("transitname = string(default='')\n")
        conf_ini.close()

    config = configobj.ConfigObj(inifile, unrepr=True, configspec=localDir+'\\configspec.ini')
    validator = Validator()
    result = config.validate(validator)
    if result:
        return config
    else:
        raise Exception ("Config file is not valid.")