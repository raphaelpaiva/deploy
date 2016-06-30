#!/usr/bin/python

import jbosscli.jbosscli as jbosscli

def generate_cleanup_script(args):
    controller = args.controller
    auth = args.auth
    num_deployments_to_keep = args.deployments_to_keep

    # TODO use common.initialize_controller()
    cli = jbosscli.Jbosscli(controller, auth)

    # TODO fail if cannot initialize controller

    # TODO extract these logics below

    all_deployments = cli.get_deployments()

    not_enabled = [x for x in all_deployments if not x.enabled]

    deployments_by_runtime_name = {}

    for d in not_enabled:
        if d.runtime_name not in deployments_by_runtime_name:
            deployments_by_runtime_name[d.runtime_name] = []

        deployments_by_runtime_name[d.runtime_name].append(d)

    script = ""

    for item in deployments_by_runtime_name.values():
        if len(item) > num_deployments_to_keep:
            sorted_deployments = sorted(item, key=lambda x: x.name)
            for d in sorted_deployments[0:len(item) - num_deployments_to_keep]:
                script += "\nundeploy {0}{1}".format(d.name, " --all-relevant-server-groups" if cli.domain else "")

    return script

if __name__ == "__main__":
    main()
