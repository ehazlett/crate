from crate.management import *
import fabric.state
from fabric.api import env

fabric.state.output['running'] = False
env.output_prefix = False
