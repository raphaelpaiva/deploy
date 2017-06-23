#!/usr/bin/python
"""Perform cleanup of existing disabled deployments.

Scan the disabled deployments, sorting by lexicographical order,
undeploying the all disabled deployments, but the last n, defined by
`deployments_to_keep` argument, which defaults to 2.

This module depends upon a connection with the controller.
If it is not available, the script will return an error message in the
form of a jboss-cli script comment line.
"""

import common


def generate_cleanup_script(args):
    """Generate and return the jboss-cli script to undeploy disabled
    deployments.
    """

    controller = args.controller
    deployments_to_keep = args.deployments_to_keep

    cli = common.initialize_controller(args)

    if not cli:
        return "# Could not initialize controller {0}. \
Cleanup will not occour.".format(controller)

    not_enabled_deployments = fetch_not_enabled_deployments(cli)

    deployments_by_runtime_name = map_deployments_by_runtime_name(
        not_enabled_deployments
    )

    script = ""

    for item in deployments_by_runtime_name.values():
        if len(item) > deployments_to_keep:
            sorted_deployments = sorted(item, key=lambda x: x.name)
            for dep in sorted_deployments[0:len(item) - deployments_to_keep]:
                script += "\nundeploy {0}{1}".format(
                    dep.name,
                    " --all-relevant-server-groups" if cli.domain else ""
                )

    return script


def map_deployments_by_runtime_name(deployments):
    """Aggregate deployments by their runtime name."""
    deployments_by_runtime_name = {}

    for dep in deployments:
        if dep.runtime_name not in deployments_by_runtime_name:
            deployments_by_runtime_name[dep.runtime_name] = []

        deployments_by_runtime_name[dep.runtime_name].append(dep)

    return deployments_by_runtime_name


def fetch_not_enabled_deployments(cli):
    """Filter deployments that are not enabled from all deployments in
    the controller.
    """
    all_deployments = set(cli.deployments)

    if cli.domain:
        assigned_deployments = set(common.get_assigned_deployments(cli))
        enabled_deployments = frozenset([d for d in assigned_deployments if d.enabled])

        return all_deployments - enabled_deployments
    else:
        return filter(lambda d: not d.enabled, all_deployments)

