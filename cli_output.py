#!/usr/bin/python
import os

def prepare_deploy_statement(deployment):
    deployment_statement = "deploy {0} --runtime-name={1} --name={2}{3}"
    server_group_statement = "" if not deployment.server_group else " --server-groups={0}".format(deployment.server_group)

    return deployment_statement.format(deployment.path, deployment.runtime_name, deployment.name, server_group_statement)

def print_deploy_script(wars):

    for war in wars:
        print prepare_deploy_statement(war)

def prepare_undeploy_statement(deployment, undeploy_tag=""):
    undeploy_statement = "undeploy {0} --keep-content{1}"
    server_group_statement = " --all-relevant-server-groups" if deployment.server_group else ""

    return undeploy_statement.format(deployment.name, server_group_statement)

def print_undeploy_pattern(undeploy_pattern):
    print "undeploy --name=" + undeploy_pattern + " --keep-content"

def print_undeploy_script(wars, undeploy_tag):
    for war in wars:
        print prepare_undeploy_statement(war, undeploy_tag)
