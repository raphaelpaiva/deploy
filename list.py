import common

def generate_list(args):
    controller = common.initialize_controller(args)
    if controller is None:
        return "# Cannot reach controller {0}.".format(args.controller)

    enabled_deployments = common.fetch_enabled_deployments(controller)

    list = ""

    enabled_deployments.sort(key=lambda x: x.server_group, reverse=True)

    for deployment in enabled_deployments:
        name = deployment.name
        runtime_name = deployment.runtime_name
        server_group = " - " + deployment.server_group if deployment.server_group is not None else " "

        list += "{0} - {1}{2}\n".format(name, runtime_name, server_group)

    return list
