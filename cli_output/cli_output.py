#!/usr/bin/python

import os


def prepare_deploy_statement(deployment, path=None):
    deployment_statement = "deploy {0} --runtime-name={1} --name={2}{3}"
    server_group_statement = "" if not deployment.server_group else \
        " --server-groups={0}".format(deployment.server_group.name)

    deployment_path = path + os.sep + deployment.runtime_name if path else ""

    return deployment_statement.format(
        deployment_path, deployment.runtime_name,
        deployment.name, server_group_statement
    )


def prepare_undeploy_statement(deployment, undeploy_tag=None):
    undeploy_statement = "undeploy {0} --keep-content{1}"
    server_group_statement = " --all-relevant-server-groups" \
        if deployment.server_group else ""

    name = deployment.name if not undeploy_tag else \
        deployment.runtime_name.replace(".war", "").replace(".jar", "") + \
        "-" + undeploy_tag

    return undeploy_statement.format(name, server_group_statement)


def generate_undeploy_pattern(undeploy_pattern):
    return "undeploy --name=" + undeploy_pattern + " --keep-content"


def generate_undeploy_script(archives, undeploy_tag=None):
    script = ""
    for archive in archives:
        script = script + "\n" + \
            prepare_undeploy_statement(archive, undeploy_tag)

    return script


def generate_deploy_script(archives, path=None):
    script = ""
    for archive in archives:
        script = script + "\n" + prepare_deploy_statement(archive, path)

    return script
