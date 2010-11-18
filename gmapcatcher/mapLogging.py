## @package gmapcatcher.mapLogging
# Initilization of logging


import sys
import logging
log = logging.getLogger()
import fileUtils

from mapConst import *

 
class FilterSevereOut( logging.Filter ):

    def __init__(self, name = None, severity = logging.NOTSET):
        self.severeout = severity 
        if name is not None:
            logging.Filter.__init__(self, name)
        else:
            logging.Filter.__init__(self)
    
    def filter(self, record):
        if record.levelno < self.severeout:
            # we allow everything below severity self.severeout
            return 1
        else:
            return 0


## Returns the Path to the configuration file
def get_loggingpath( loggingpath = None ):
    if loggingpath is None:
    # the config file must be found at DEFAULT_PATH
        loggingpath = os.path.expanduser(DEFAULT_PATH)
        fileUtils.check_dir(loggingpath)
        loggingpath = os.path.join(loggingpath, LOGGING_FILE_NAME)

        return loggingpath 
    else:
        return loggingpath
    
    

def init_logging( loggingpath = None ):
    
    log.setLevel(logging.DEBUG)

    if LOGGING_STDOUT:
        hsout = logging.StreamHandler( sys.stdout )
        hsout.setFormatter( logging.Formatter(LOGGING_STDOUT_FORMAT) )
        hsout.setLevel( LOGGING_STDOUT_LEVEL_ABOVE )
        hsout.addFilter( FilterSevereOut(name=None, severity=LOGGING_STDOUT_LEVEL_BELOW) )
        log.addHandler(hsout)

    if LOGGING_STDERR:
        hserr = logging.StreamHandler( sys.stderr )
        hserr.setFormatter( logging.Formatter( LOGGING_STDERR_FORMAT ) )
        hserr.setLevel( LOGGING_STDERR_LEVEL_ABOVE )
        log.addHandler(hserr)

    if LOGGING_FILE:
        hf = logging.FileHandler( get_loggingpath(loggingpath), LOGGING_FILE_MODE )
        hf.setFormatter( logging.Formatter(LOGGING_FILE_FORMAT) )
        hf.setLevel( LOGGING_FILE_LEVEL_ABOVE )
        log.addHandler(hf)


