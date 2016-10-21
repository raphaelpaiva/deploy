#!/usr/bin/python

import os
import time
import cli_output
import jbosscli
import common


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
    """Given the archives and a server group mapping dict,
    update the archive's server_group property.
    """
    for archive in archives:
        if archive.server_group is None and archive.runtime_name in mapping:
            archive.server_group = jbosscli.ServerGroup(
                mapping[archive.runtime_name],
                None
            )


def generate_deploy_script(args, rollback_file_dir=None):
    path = os.path.abspath(args.path) + os.sep
    files_filter = args.files
    undeploy_pattern = args.undeploy_pattern
    skip_undeploy = True if undeploy_pattern else args.skip_undeploy
    undeploy_tag = args.undeploy_tag
    mapping_file = args.server_group_mapping_file

    tag = common.extract_tag(path)

    controller = common.initialize_controller(args)
    archives = common.read_archive_files(path, tag, files_filter)

    header = ""
    undeploy_script = ""

    domain_mode = controller and controller.domain

    if controller:
        enabled_deployments = common.fetch_enabled_deployments(
            controller,
            archives
        )

        rollback_filename_template = \
            common.generate_rollback_filename_template(
                args.rollback_info_file_suffix
            )
        rollback_info_file = persist_rollback_info(
            enabled_deployments,
            rollback_filename_template,
            rollback_file_dir
        )
        header = "# Rollback information saved in " \
            + rollback_info_file if rollback_info_file else ""

        undeploy_script = cli_output.generate_undeploy_script(
            enabled_deployments
        )

        if domain_mode:
            map_deployments_server_groups(archives, mapping_file)
            if args.restart:
                header += "\n:stop-servers()"
    else:
        undeploy_script = generate_undeploy_script(args, archives)

    deploy_script = cli_output.generate_deploy_script(archives)

    if args.restart:
        deploy_script += "\n:start-servers()"

    return "{0}\n{1}\n{2}".format(header, undeploy_script, deploy_script)


def persist_rollback_info(deployments,
                          rollback_filename_template="rollback-info_",
                          rollback_file_dir=None):
    """Write name, runtime_name and server group of all enabled
    deployments to be replaced to a file named rollback-info_<timestamp>.
    """
    if not deployments:
        return

    directory = rollback_file_dir if rollback_file_dir else \
        os.path.dirname(os.path.abspath(__file__))

    rollback_info_file = directory + os.path.sep + \
        rollback_filename_template + str(int(round(time.time() * 1000)))
    deployment_line_template = "{0} {1} {2}\n"
    rollback_info = ""

    for deployment in deployments:
        line = deployment_line_template.format(
            deployment.name,
            deployment.runtime_name,
            deployment.server_group
        )
        rollback_info += line

    common.write_to_file(rollback_info_file, rollback_info)

    return rollback_info_file


def generate_undeploy_script(args, archives=[]):
    if args.skip_undeploy:
        return ""
    if args.undeploy_pattern:
        return cli_output.generate_undeploy_pattern(args.undeploy_pattern)
    else:
        return cli_output.generate_undeploy_script(archives, args.undeploy_tag)


def map_deployments_server_groups(archives, mapping_file):
    mapping = read_server_group_mapping(mapping_file)
    map_server_groups(archives, mapping)
