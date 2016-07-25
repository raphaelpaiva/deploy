import os

import common
import deploy

OK_RET_CODE         = 0
ERROR_RET_CODE      = 1
INIT_ERROR_RET_CODE = 2

def verify(args):
    path = os.path.abspath(args.path) + os.sep
    tag = deploy.extract_tag(path)

    controller = common.initialize_controller(args)
    if controller is None:
        return ("# Cannot reach controller {0}.".format(args.controller), INIT_ERROR_RET_CODE)

    output = ""

    enabled_deployments = common.fetch_enabled_deployments(controller)

    to_be_deployed = deploy.read_archive_files(path, tag)

    if not to_be_deployed:
        return ("Deployment directory is empty!", INIT_ERROR_RET_CODE)

    deployed_names = {x.name for x in enabled_deployments}
    to_be_deployed_names = {x.name for x in to_be_deployed}

    everything_deployed = verify_deployments(to_be_deployed_names, deployed_names)

    return_code = None

    if everything_deployed:
        output += "OK!"
        return_code = OK_RET_CODE
    else:
        not_deployed = to_be_deployed_names - deployed_names
        output += "ERROR: some modules were not deployed:\n"
        output += "\n".join(not_deployed)
        return_code = ERROR_RET_CODE

    return (output, return_code)

def verify_deployments(to_be, deployed):
    return to_be.issubset(deployed)
