import os

import common
import deploy

def generate_list(args):
    path = os.path.abspath(args.path) + os.sep
    tag = deploy.extract_tag(path)

    controller = common.initialize_controller(args)
    if controller is None:
        return "# Cannot reach controller {0}.".format(args.controller)

    output = "Testing deployments in {0} against {1}\n".format(args.controller, path)

    enabled_deployments = common.fetch_enabled_deployments(controller)

    to_be_deployed = deploy.read_archive_files(path, tag)

    deployed_names = {x.name for x in enabled_deployments}
    to_be_deployed_names = {x.name for x in to_be_deployed}

    everything_deployed = to_be_deployed_names.issubset(deployed_names)

    #output += str(deployed_names)
    #output += "\n\n" + str(to_be_deployed_names)

    if everything_deployed:
        output += "OK!"
    else:
        not_deployed = to_be_deployed_names - deployed_names
        output += "ERROR: some modules were not deployed:\n"
        output += "\n".join(not_deployed)

    return output
