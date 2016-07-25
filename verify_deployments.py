import os

import common
import deploy

INITIALIZE_ERROR_RET_CODE = 2
OK_RETURN_CODE            = 0

def verify(args):
    path = os.path.abspath(args.path) + os.sep
    tag = deploy.extract_tag(path)

    controller = common.initialize_controller(args)
    if controller is None:
        return ("# Cannot reach controller {0}.".format(args.controller), INITIALIZE_ERROR_RET_CODE)

    output = ""

    enabled_deployments = common.fetch_enabled_deployments(controller)

    to_be_deployed = deploy.read_archive_files(path, tag)

    deployed_names = {x.name for x in enabled_deployments}
    to_be_deployed_names = {x.name for x in to_be_deployed}

    everything_deployed = verify_deployments(to_be_deployed_names, deployed_names)

    if everything_deployed:
        output += "OK!"
    else:
        not_deployed = to_be_deployed_names - deployed_names
        output += "ERROR: some modules were not deployed:\n"
        output += "\n".join(not_deployed)

    return (output, OK_RETURN_CODE)

def verify_deployments(to_be, deployed):
    return to_be.issubset(deployed)
