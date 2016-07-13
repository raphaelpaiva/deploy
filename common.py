from jbosscli import Jbosscli

def initialize_controller(args):
    """Try to instantiate and return the controller object. In case of errors, print it and return None."""
    try:
        return Jbosscli(args.controller, args.auth)
    except Exception as e:
        print e
        return None

def fetch_enabled_deployments(controller, archives=[]):
    """Fetch a list of enabled deployments with the same runtime name as the archives to deploy.

    Arguments:
    controller -- the controller to fetch the deployments from
    archives   -- the archives to be deployed

    This function updates the archives with fresh information from the controller,
    such as the server group and if it is enabled or not.

    It is mainly used to provide information to the undeploy script generation.
    """
    deployments = controller.get_assigned_deployments()

    if not archives:
        return [x for x in deployments if x.enabled]

    runtime_names = {}
    for archive in archives:
        runtime_names[archive.runtime_name] = archive

    enabled_deployments = []
    for deployment in deployments:
        if deployment.runtime_name in runtime_names and deployment.enabled:
            enabled_deployments.append(deployment)
            runtime_names[deployment.runtime_name].enabled = True
            runtime_names[deployment.runtime_name].server_group = deployment.server_group

    return enabled_deployments


def write_to_file(file, content): #pragma: no cover
    """Write content to file."""
    with open(file, "w") as f:
        f.write(content)

def read_from_file(path): #pragma: no cover
    lines = []
    with open(path) as f:
        lines = f.readlines()

    return lines
