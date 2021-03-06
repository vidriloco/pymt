'''
PyMT: multitouch toolkit

PyMT is a python module for developing multi-touch enabled media rich applications.

Currently the aim is to allow for quick and easy interaction design and rapid prototype development. There is also a focus on logging tasks or sessions of user interaction to quantitative data and the analysis/visualization of such data.

You can visit http://pymt.txzone.net/ for more informations !
'''

__version__ = '0.4.0b2'

import sys
import getopt
import os
from logger import pymt_logger, LOG_LEVELS
import logger

# Version number of current configuration format
PYMT_CONFIG_VERSION = 7

# Start !
pymt_logger.info('PyMT v%s' % (__version__))

# Global settings options for pymt
options = {
    'shadow_window': True,
    'window': ('pygame', 'glut'),
    'text': ('pil', 'cairo', 'pygame'),
    'video': ('gstreamer', 'pyglet' ),
    'audio': ('pygame', 'gstreamer', ),
    'image': ('pil', 'pygame'),
    'camera': ('opencv', 'gstreamer', 'videocapture'),
}

# Read environment
for option in options:
    key = 'PYMT_%s' % option.upper()
    if key in os.environ:
        try:
            if type(options[option]) in (list, tuple):
                options[option] = (str(os.environ[key]),)
            else:
                options[option] = os.environ[key].lower() in \
                    ('true', '1', 'yes', 'yup')
        except:
            pymt_logger.warning('Core: Wrong value for %s environment key' % key)
            pymt_logger.exception('')

# Extract all needed path in pymt
#: PyMT directory
pymt_base_dir        = os.path.dirname(sys.modules[__name__].__file__)
#: PyMT external libraries directory
pymt_libs_dir        = os.path.join(pymt_base_dir, 'lib')
#: PyMT modules directory
pymt_modules_dir     = os.path.join(pymt_base_dir, 'modules')
#: PyMT data directory
pymt_data_dir        = os.path.join(pymt_base_dir, 'data')
#: PyMT input provider directory
pymt_providers_dir   = os.path.join(pymt_base_dir, 'input', 'providers')
#: PyMT user-home storage directory
pymt_home_dir        = None
#: PyMT configuration filename
pymt_config_fn       = None
#: PyMT user modules directory
pymt_usermodules_dir = None

# Add lib in pythonpath
sys.path           = [pymt_libs_dir] + sys.path

# Don't go further if we generate documentation
if os.path.basename(sys.argv[0]) in ('sphinx-build', 'autobuild.py'):
    os.environ['PYMT_DOC'] = '1'
if os.path.basename(sys.argv[0]) in ('sphinx-build', ):
    os.environ['PYMT_DOC_INCLUDE'] = '1'
if not 'PYMT_DOC_INCLUDE' in os.environ:

    # Configuration management
    pymt_home_dir = os.path.expanduser('~/.pymt/')
    pymt_config_fn = os.path.join(pymt_home_dir, 'config')
    if not os.path.exists(pymt_home_dir):
        os.mkdir(pymt_home_dir)
    pymt_usermodules_dir = os.path.expanduser('~/.pymt/mods/')
    if not os.path.exists(pymt_usermodules_dir):
        os.mkdir(pymt_usermodules_dir)

    # configuration
    from config import *

    # Set level of logger
    level = LOG_LEVELS.get(pymt_config.get('pymt', 'log_level'))
    pymt_logger.setLevel(level=level)

    # save sys argv, otherwize, gstreamer use it and display help..
    sys_argv = sys.argv
    sys.argv = sys.argv[:1]

    # Note: import are done after logger module initialization,
    # and configuration applied to logger.

    # no dependices at all
    from baseobject import *
    from exceptions import *
    from cache import Cache

    # system dependices
    from utils import *
    from event import *
    from clock import *
    from texture import *
    from plugin import *

    # internal dependices
    from graphx import *
    from vector import *

    # dependices
    from core import *
    from modules import *
    from input import *
    from base import *

    # after dependices
    from gesture import *
    from obj import OBJ
    from loader import *

    # widgets
    from ui import *

    # Can be overrided in command line
    try:
        opts, args = getopt.getopt(sys_argv[1:], 'hp:fkawFem:sn',
            ['help', 'fullscreen', 'windowed', 'fps', 'event',
             'module=', 'save', 'fake-fullscreen', 'auto-fullscreen',
             'display=', 'size='])

        # set argv to the non-read args
        sys.argv = sys_argv[0:1] + args

        need_save = False
        for opt, arg in opts:
            if opt in ('-h', '--help'):
                pymt_usage()
                sys.exit(0)
            elif opt in ('-p', '--provider'):
                id, args = arg.split(':', 1)
                pymt_config.set('input', id, args)
            elif opt in ('-a', '--auto-fullscreen'):
                pymt_config.set('graphics', 'fullscreen', 'auto')
            elif opt in ('-k', '--fake-fullscreen'):
                pymt_config.set('graphics', 'fullscreen', 'fake')
            elif opt in ('-f', '--fullscreen'):
                pymt_config.set('graphics', 'fullscreen', '1')
            elif opt in ('-w', '--windowed'):
                pymt_config.set('graphics', 'fullscreen', '0')
            elif opt in ('-F', '--fps'):
                pymt_config.set('pymt', 'show_fps', '1')
            elif opt in ('-e', '--eventstats'):
                pymt_config.set('pymt', 'show_eventstats', '1')
            elif opt in ('--size', ):
                w, h = str(arg).split('x')
                pymt_config.set('graphics', 'width', w)
                pymt_config.set('graphics', 'height', h)
            elif opt in ('--display', ):
                pymt_config.set('graphics', 'display', str(arg))
            elif opt in ('-m', '--module'):
                if str(arg) == 'list':
                    pymt_modules.usage_list()
                    sys.exit(0)
                args = arg.split(':', 1)
                if len(args) == 1:
                    args += ['']
                pymt_config.set('modules', args[0], args[1])
            elif opt in ('-s', '--save'):
                need_save = True
            elif opt in ('-n', ):
                options['shadow_window'] = False

        if need_save:
            try:
                with open(pymt_config_fn, 'w') as fd:
                    pymt_config.write(fd)
            except Exception, e:
                pymt_logger.exception('Core: error while saving default configuration file')
            pymt_logger.info('Core: PyMT configuration saved.')
            sys.exit(0)

        # last initialization
        if options['shadow_window']:
            pymt_logger.debug('Core: Creating PyMT Window')
            shadow_window = MTWindow()

    except getopt.GetoptError, err:
        pymt_logger.error('Core: %s' % str(err))
        pymt_usage()
        sys.exit(2)
