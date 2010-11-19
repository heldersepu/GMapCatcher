## @package gmapcatcher.mapLogging
# Logging for gmapcatcher


"""
Logging for GMapCatcher

Purpose - primary for developers to manage debug messages. Secondary - users after setting 
'--logging-path=/tmp/maps.log' will catch all messages in file and can send them for checking
what went wrong in error reporting.

 
Usage:
- don't use print / print_exc etc commands for output debug/info/error messages
- in module import logging 'import logging'
- get logger 'log = logging.getLogger()' 
That's 2 lines at the top of the module.

In source code use:
log.debug(msg)
log.info(msg)
log.warning(msg)
log.error(msg)
log.exception(exception)
log.critical(msg)


Now use log.<method> to print debug/info/error messages anywhere in the code.

In mapConst configure what messages you want to see.


For users:
==========
Production setup is:
- output to stdout: info, warning
- output to stderr: error, critical
- output to file: default None. If set on command line '--logging-path=/tmp/map.log' 
All messages from debug are logged in file.  


For developers:
===============
- it is possible/welcom/convenient to put many debug outputs in the source code. While debugging it's good to 
have this helper output. After things are OK, just set log level to production setting and messages
woun't be displayed. 
If there is a need to see debug messages again just set logging level to debug.

There will be plenty of debug messages printed on the screen/file. It's simple to use 'grep' for
selecting what messages shold be listed.

cat maps.log | grep "only_my_module"
cat maps.log | grep -v "not_this_module" | grep -v "not_that_module"
after setting DEBUG for stdout: maps.py | grep -v "not_this_module" | grep -v "not_that_module"
Use grep from gnuwin32 for windows (http://gnuwin32.sourceforge.net/packages/grep.htm).



"""


import sys
import logging
from traceback import print_exc
log = logging.getLogger()
import fileUtils

from mapConst import *


class LoggingFilenameNotSetError(Exception):
    pass

 
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


## Returns the Path to the logging file
def get_loggingpath( loggingpath = None ):
    if loggingpath is None:
        if LOGGING_FILE_NAME is None:
            raise LoggingFilenameNotSetError("LOGGING_FILE_NAME is None")
        # the config file must be found at DEFAULT_PATH
        loggingpath = os.path.expanduser(DEFAULT_PATH)
        fileUtils.check_dir(loggingpath)
        loggingpath = os.path.join(loggingpath, LOGGING_FILE_NAME)

        return loggingpath 
    else:
        return loggingpath
    
    

def init_logging( loggingpath = None ):
    """initialization of logging
    
    LOGGING_STDOUT / LOGGING_STDERR / LOGGING_FILE - True/False - allow/deny strem
    only STDOUT has 'LOGGING_STDOUT_LEVEL_BELOW'
    LOGGING_FILE_NAME is None or just a filename. If it's None it means only option how to set up
    logging is using command line. If LOGGING_FILE_NAME is used, optional commandline parameter
    overrides LOGGING_FILE_NAME. 
    """
    cur_level = logging.ERROR
    log.setLevel( cur_level )

    if LOGGING_STDOUT:
        hsout = None
        try:
            hsout = logging.StreamHandler( sys.stdout )
            hsout.setFormatter( logging.Formatter(LOGGING_STDOUT_FORMAT) )
            hsout.setLevel( LOGGING_STDOUT_LEVEL_ABOVE_OR_EQUAL )
            hsout.addFilter( FilterSevereOut(name=None, severity=LOGGING_STDOUT_LEVEL_BELOW) )
            log.addHandler(hsout)
            
            if( LOGGING_STDOUT_LEVEL_ABOVE_OR_EQUAL < cur_level ):
                cur_level = LOGGING_STDOUT_LEVEL_ABOVE_OR_EQUAL
                log.setLevel(cur_level)
            log.info("Logging to stdout is set.")
        except Exception, ex:
            if hsout is not None:
                log.removeHandler(hsout)
            print_exc()
            

    if LOGGING_STDERR:
        hserr = None
        try:
            hserr = logging.StreamHandler( sys.stderr )
            hserr.setFormatter( logging.Formatter( LOGGING_STDERR_FORMAT ) )
            hserr.setLevel( LOGGING_STDERR_LEVEL_ABOVE_OR_EQUAL )
            log.addHandler(hserr)
            
            if( LOGGING_STDERR_LEVEL_ABOVE_OR_EQUAL < cur_level ):
                cur_level = LOGGING_STDERR_LEVEL_ABOVE_OR_EQUAL
                log.setLevel(cur_level)
            log.info("Logging to stderror is set.")
        except Exception, ex:
            if hserr is not None:
                log.removeHandler(hserr)
            log.exception(ex)

    if LOGGING_FILE:
        try:
            filename = get_loggingpath(loggingpath)
        except LoggingFilenameNotSetError, ex:
            log.debug("LOGGING_FILE_NAME is not set.")
            return
            
        hf = None
        try:
            hf = logging.FileHandler( filename, LOGGING_FILE_MODE )
            hf.setFormatter( logging.Formatter(LOGGING_FILE_FORMAT) )
            hf.setLevel( LOGGING_FILE_LEVEL_ABOVE_OR_EQUAL )
            log.addHandler(hf)
            if( LOGGING_FILE_LEVEL_ABOVE_OR_EQUAL < cur_level ):
                cur_level = LOGGING_FILE_LEVEL_ABOVE_OR_EQUAL
                log.setLevel(cur_level)
            log.info("Logging to file is set to "+str(filename)+".")
        except Exception, ex:
            # we have error while logging to file, remove handler and continue
            if hf is not None:
                log.removeHandler(hf)
            log.exception(ex)
            

