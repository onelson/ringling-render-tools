import ntpath, re
from subprocess import Popen, PIPE
from rrt import RinglingException, get_log
LOG = get_log()
def get_share(path):
    """
    Maps windows drive letters to unc paths.
    """
    drive_letter = ntpath.splitdrive(path)[0]
    try:
        p = Popen(['net use', drive_letter], stdin=PIPE, stdout=PIPE, 
                  stderr=PIPE, shell=True)
        p.stdin.close()
        (out, err) = p.communicate()
        if p.returncode != 0:
            LOG.error(err)
            raise RinglingException("Can't find network share for drive %s" % drive_letter)
        unc = out.splitlines()[1].split()[2].strip().lower()
        
        """
        TODO: decide if we want to hold off on these transformations until we're 
        in hpc-spool-script...
        """
        # on the cluster vlan, our file-server hosts have a 1 appended to their names        
        return re.sub("(hamming|minsky|perlis|shannon|wilkes|wilkinson)", '\g<1>1', unc, 1)
    except Exception, e:
        raise e
