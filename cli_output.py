#!/usr/bin/python
import os

def prepare_deploy_statement(war_file, tag=None):
    if tag == None:
        tag = "notag"

    archive_name = war_file.split('/')[-1]
    deployment_name = archive_name.replace(".war", "") + "-" + tag

    return "deploy " + war_file + " --runtime-name=" + archive_name + " --name=" + deployment_name

def print_deploy_script(wars, tag):
    batch = len(wars)

    if  batch > 1:
        print "batch"

    for war in wars:
        print prepare_deploy_statement(war, tag)

    if batch > 1:
        print "run-batch"

def prepare_undeploy_statement(war_file, undeploy_tag):
    war = war_file.split("/")[-1]
    deployment_name = war.replace(".war", "") + "-" + undeploy_tag
    return "undeploy " + deployment_name + " --keep-content"

def print_undeploy_pattern(undeploy_pattern):
    print "undeploy --name=" + undeploy_pattern + " --keep-content"

def print_undeploy_script(wars, undeploy_tag):
    for war in wars:
        print prepare_undeploy_statement(war, undeploy_tag)
