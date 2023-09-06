from subprocess import call
import os

pathname = os.path.dirname(os.path.abspath(__file__))
execpath = os.path.join(pathname, 'App')

call(['open', execpath])