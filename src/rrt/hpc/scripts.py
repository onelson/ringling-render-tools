"""
These functions serve as script entry points.
They identify the job style based on the environment, then pass the request off
to application specific implementations.
"""

import os, sys, shutil, platform, datetime
from pkg_resources import Requirement, resource_filename

from rrt import RinglingException, get_log
from rrt.hpc import env
LOG = get_log(platform.uname()[1], True)

class MissingDelegateError(RinglingException):pass

class Delegator(object):
    __delegates__ = {
                     'maya_render_sw': 'rrt.hpc.maya.sw',
                     'maya_render_rman': 'rrt.hpc.maya.rman', 
                     'max': 'rrt.hpc.max'
                     }
    _delegate = None
    
    def __init__(self):
        LOG.debug("Params: %r" % env())
        jobtype = os.getenv('RENDERER', None)
        if jobtype not in self.__delegates__:
            raise MissingDelegateError
        self._delegate = self.__delegates__[jobtype]
        LOG.debug("Got delegate: %s" % self._delegate)
        __import__(self._delegate, globals(), locals())
        
    def prep(self):
        # Generic Prep
        log_dir = os.path.dirname(os.getenv('LOGS', None))
        output_dir = os.path.dirname(os.getenv('OUTPUT', None))
        for d in (log_dir, output_dir):
            if not os.path.exists(d):
                try: os.makedirs(d)
                except Exception, e:
                    LOG.warning(e)
        # Delegate access to implementation
        return sys.modules[self._delegate].prep()

    def release(self):
        """ Delegate access to implementation """
        return sys.modules[self._delegate].release()


def prep_delegator():
    start = datetime.datetime.now()
    LOG.info("Starting node prep. %s" % str(start))
    Delegator().prep()
    end = datetime.datetime.now()
    LOG.info("Elapsed time: %s" % str(end - start))
    LOG.info("Done.")
    sys.exit(0)

def release_delegator():
    start = datetime.datetime.now()
    LOG.info("Starting node release. %s" % str(start))
    Delegator().release()
    end = datetime.datetime.now()
    LOG.info("Elapsed time: %s" % str(end - start))
    LOG.info("Done.")
    sys.exit(0)
    
def deploy_extras():
    DEPLOY_LOCATION = r'C:\Ringling\HPC'
    extras = resource_filename(Requirement.parse("ringling-render-tools"),"rrt/extras")
    if os.path.exists(DEPLOY_LOCATION): shutil.rmtree(DEPLOY_LOCATION)
    shutil.copytree(extras,DEPLOY_LOCATION)
    print "Done."
    sys.exit(0)