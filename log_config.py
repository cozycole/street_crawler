import os
from os.path import join
print (os.getcwd())

LOGGING_CONFIG = {
    'version' : 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
    },
    'handlers': {
        'default': { 
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',  # Default is stderr
        },
        'error_handler': {
            'level': 'ERROR',
            'formatter': 'standard',
            'class': 'logging.FileHandler',
            'filename': join(os.getcwd(), 'logs/error.log') # You can change this by doing LOG_CONFIG['handlers']['error_handler']['filename'] 
        },
        'debug_handler': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.FileHandler',
            'filename': join(os.getcwd(), 'logs/debug.log')
        },
        'debug_stdout':{
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        }
    },
    'loggers' : {
        '' : {
            'handlers': ['default'],
            'level': 'ERROR',
            'propagate' : False
        },
        'main': { 
            'handlers': ['debug_handler','error_handler','debug_stdout'],
            'level': 'DEBUG',
            'propagate' : False
        },
        'crawler': { 
            'handlers': ['debug_handler','error_handler', 'debug_stdout'],
            'level': 'DEBUG',
            'propagate' : False
        }
    }
}