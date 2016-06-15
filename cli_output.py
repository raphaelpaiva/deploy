#!/usr/bin/python
import os

def prepare_deploy_statement(deployment):
    deployment_statement = "deploy {0} --runtime-name={1} --name={2}{3}"
    server_group_statement = "" if not deployment.server_group else " --server-groups={0}".format(deployment.server_group)

    deployment_path = deployment.path if deployment.path else ""

    return deployment_statement.format(deployment_path, deployment.runtime_name, deployment.name, server_group_statement)

def print_deploy_script(archives):
    for archive in archives:
        print prepare_deploy_statement(archive)

def prepare_undeploy_statement(deployment, undeploy_tag=None):
    undeploy_statement = "undeploy {0} --keep-content{1}"
    server_group_statement = " --all-relevant-server-groups" if deployment.server_group else ""

    name = deployment.name if not undeploy_tag else deployment.runtime_name.replace(".war", "").replace(".jar", "") + "-" + undeploy_tag

    return undeploy_statement.format(name, server_group_statement)

def print_undeploy_pattern(undeploy_pattern):
    print "undeploy --name=" + undeploy_pattern + " --keep-content"

def print_undeploy_script(archives, undeploy_tag=None):
    for archive in archives:
        print prepare_undeploy_statement(archive, undeploy_tag)
