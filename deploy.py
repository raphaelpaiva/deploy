#!/usr/bin/python

import os
import tempfile
import argparse
import cli_output
import jbosscli.jbosscli as jbosscli
import rollback
import common

def initialize_controller(args):
    """Try to instantiate and return the controller object. In case of errors, print it and return None."""
    try:
        return jbosscli.Jbosscli(args.controller, args.auth)
    except Exception as e:
        print e
        return None

def read_archive_files(path, tag):
    """Scan path looking for archive files. Return a list of archives with tag applied to their names. runtime_name remains as the filename."""
    archives = []
    for file in os.listdir(path):
        if is_archive(file):
            runtime_name = file.split(os.sep)[-1]
            name = runtime_name.replace(".ear", "").replace(".war", "").replace(".jar", "") + "-" + tag
            enabled = False
            deployment = jbosscli.Deployment(name, runtime_name, enabled, path=path + file)
            archives.append(deployment)

    return archives

def is_archive(file):
    """Return true if file name ends with .ear, .war or .jar"""
    return file.endswith('.ear') or file.endswith('.war') or file.endswith('.jar')

def extract_tag(path):
    """Extract the name of the directory where the deployments are placed.

    Arguments:
    path -- the path to extract the name from.

    This simply reads the leaf dir in a path.
    "/path/to/deployment" returns "deployment"
    "../relative/path/" returns "path"
    "abc" returns "abc"
    """
    if path.endswith(os.sep):
        path = path[:-1]

    return path.split(os.sep)[-1]

def read_server_group_mapping(mapping_file):
    """Given a mapping file path, read it and return a dict with its contents.

    Arguments:
    mapping_file -- the path to the mapping file (e.g. /tmp/mapping.properties)

    The mapping file name is not relevant.
    The content of the file should be in the format runtime_name=server_group.
    One per line, just like a java properties file.
    E.g.:
    app1=cluster_group
    app2=web_group
    """
    mapping = {}
    if os.path.isfile(mapping_file):
        lines = common.read_from_file(mapping_file)
        for line in lines:
            (runtime_name, server_group) = line.strip().split("=")
            mapping[runtime_name] = server_group

    return mapping

def map_server_groups(archives, mapping):
    """Given the archives and a server group mapping dict, update the archive's server_group property."""
    for archive in archives:
        if archive.server_group is None and archive.runtime_name in mapping:
            archive.server_group = jbosscli.ServerGroup(mapping[archive.runtime_name], None)

def generate_deploy_script(args):
    path = os.path.abspath(args.path) + os.sep
    undeploy_pattern = args.undeploy_pattern
    skip_undeploy = True if undeploy_pattern else args.skip_undeploy
    undeploy_tag = args.undeploy_tag
    mapping_file = args.server_group_mapping_file

    tag = extract_tag(path)

    controller = common.initialize_controller(args)
    archives = read_archive_files(path, tag)

    header = ""
    undeploy_script = ""

    if controller:
        enabled_deployments = common.fetch_enabled_deployments(controller, archives)
        rollback_info_file = rollback.persist_rollback_info(enabled_deployments)
        header = "# Rollback information saved in " + rollback_info_file

        undeploy_script = cli_output.generate_undeploy_script(enabled_deployments)

        if controller.domain:
             map_deployments_server_groups(archives, mapping_file)
    else:
        undeploy_script = generate_undeploy_script()

    deploy_script = cli_output.generate_deploy_script(archives)

    return "{0}\n{1}\n{2}".format(header, undeploy_script, deploy_script)

def generate_undeploy_script():
    if not skip_undeploy:
        cli_output.generate_undeploy_script(archives, undeploy_tag)

    if undeploy_pattern:
        cli_output.print_undeploy_pattern(undeploy_pattern)

def map_deployments_server_groups(archives, mapping_file):
    mapping = read_server_group_mapping(mapping_file)
    map_server_groups(archives, mapping)

if __name__ == "__main__": main()
