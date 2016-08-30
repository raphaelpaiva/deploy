#!/usr/bin/python

import common

def generate_cleanup_script(args):
    controller = args.controller
    auth = args.auth
    num_deployments_to_keep = args.deployments_to_keep

    cli = common.initialize_controller(args)

    if not cli:
        return "# Could not initialize controller {0}. Cleanup will not occour.".format(controller)

    not_enabled_deployments = fetch_not_enabled_deployments(cli)

    deployments_by_runtime_name = map_deployments_by_runtime_name(not_enabled_deployments)

    script = ""

    for item in deployments_by_runtime_name.values():
        if len(item) > num_deployments_to_keep:
            sorted_deployments = sorted(item, key=lambda x: x.name)
            for d in sorted_deployments[0:len(item) - num_deployments_to_keep]:
                script += "\nundeploy {0}{1}".format(d.name, " --all-relevant-server-groups" if cli.domain else "")

    return script

def map_deployments_by_runtime_name(deployments):
    """Aggregate deployments by their runtime name."""
    deployments_by_runtime_name = {}

    for d in deployments:
        if d.runtime_name not in deployments_by_runtime_name:
            deployments_by_runtime_name[d.runtime_name] = []

        deployments_by_runtime_name[d.runtime_name].append(d)

    return deployments_by_runtime_name

def fetch_not_enabled_deployments(controller):
    """Filter deployments that are not enabled from all deployments in the controller."""
    all_deployments = controller.get_deployments()

    not_enabled = [x for x in all_deployments if not x.enabled]

    return not_enabled
