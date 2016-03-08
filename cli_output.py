#!/usr/bin/python
import os

def prepare_deploy_statement(deployment):
    return "deploy " + deployment.path + " --runtime-name=" + deployment.runtime_name + " --name=" + deployment.name

def print_deploy_script(wars):
    batch = len(wars)

    if  batch > 1:
        print "batch"

    for war in wars:
        print prepare_deploy_statement(war)

    if batch > 1:
        print "run-batch"

def prepare_undeploy_statement(deployment, undeploy_tag=""):
    return "undeploy " + deployment.runtime_name + " --keep-content"

def print_undeploy_pattern(undeploy_pattern):
    print "undeploy --name=" + undeploy_pattern + " --keep-content"

def print_undeploy_script(wars, undeploy_tag):
    for war in wars:
        print prepare_undeploy_statement(war, undeploy_tag)
