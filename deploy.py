#!/usr/bin/python
import os
import glob
import tempfile
import argparse
import cli_output
import jbosscli.jbosscli as jbosscli
import time

def main():
    args = parse_args()
    path = os.path.abspath(args.path) + os.sep
    undeploy_pattern = args.undeploy_pattern
    skip_undeploy = True if undeploy_pattern else args.skip_undeploy
    undeploy_tag = args.undeploy_tag
    mapping_file = args.server_group_mapping_file

    controller = initialize_controller(args)

    if not controller and args.rollback:
        print "# Cannot communicate with the specified controller\n# Rollback will not occour"
        exit(1)

    tag = extract_tag(path)

    archives = []
    if not args.rollback:
        archives = read_archive_files(path, tag)
    else:
        archives = read_rollback_info()

    enabled_deployments = []

    if controller:
        enabled_deployments = fetch_enabled_deployments(controller, archives)
        if not args.rollback:
            persist_rollback_info(enabled_deployments)
        cli_output.print_undeploy_script(enabled_deployments)
    else:
        if not skip_undeploy:
            cli_output.print_undeploy_script(archives, undeploy_tag)

        if undeploy_pattern:
            cli_output.print_undeploy_pattern(undeploy_pattern)

    if controller and controller.domain:
        mapping = read_server_group_mapping(mapping_file)
        map_server_groups(archives, mapping)

    cli_output.print_deploy_script(archives)

def parse_args():
    default_server_group_mapping_file = tempfile.gettempdir() + os.sep + "server-group-mapping.properties"

    parser = argparse.ArgumentParser(description="Generates [un]deploy commands which you can pipe through jboss-cli script.")

    parser.add_argument("path", help="the path where the archive (.ear, .war, .jar) packages are stored")

    parser.add_argument("--skip-undeploy",
                        help="do not generate undeploy commands",
                        action="store_true")

    parser.add_argument("--undeploy-pattern",
                        help="specify a regex pattern for the undeploy cammand. This implies --skip-undeploy.")

    parser.add_argument("--undeploy-tag",
                        help="specify a tag to append for the undeploy cammand.")

    parser.add_argument("--controller",
                        help="The controller to deploy to.",
                        default="localhost:9990")

    parser.add_argument("--auth",
                        help="The credentials to authenticate on the controller",
                        default="jboss:jboss@123")

    parser.add_argument("--server-group-mapping-file",
                        help="A file containing a runtime-name=server-group mapping. Defaults to /tmp/server-group-mapping.properties",
                        default=default_server_group_mapping_file)

    parser.add_argument("--rollback",
                        help="Rollback to a previous deployment. This depends on having a deployment-info file.",
                        action="store_true")

    return parser.parse_args()

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
        with open(mapping_file) as f:
            for line in f:
                (runtime_name, server_group) = line.strip().split("=")
                mapping[runtime_name] = server_group
    return mapping

def map_server_groups(archives, mapping):
    """Given the archives and a server group mapping dict, update the archive's server_group property."""
    for archive in archives:
        if archive.server_group is None and archive.runtime_name in mapping:
            archive.server_group = jbosscli.ServerGroup(mapping[archive.runtime_name], None)

def fetch_enabled_deployments(controller, archives):
    """Fetch a list of enabled deployments with the same runtime name as the archives to deploy.

    Arguments:
    controller -- the controller to fetch the deployments from
    archives   -- the archives to be deployed

    This function updates the archives with fresh information from the controller,
    such as the server group and if it is enabled or not.

    It is mainly used to provide information to the undeploy script generation.
    """
    deployments = controller.get_assigned_deployments()

    runtime_names = {}
    for archive in archives:
        runtime_names[archive.runtime_name] = archive

    enabled_deployments = []
    for deployment in deployments:
        if deployment.runtime_name in runtime_names and deployment.enabled:
            enabled_deployments.append(deployment)
            runtime_names[deployment.runtime_name].enabled = True
            runtime_names[deployment.runtime_name].server_group = deployment.server_group

    return enabled_deployments

def persist_rollback_info(deployments):
    """Write name, runtime_name and server group of all enabled deployments to be replaced to a file named rollback-info_<timestamp>."""
    if not deployments:
        return

    rollback_info_file = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + "rollback-info_" + str(int(round(time.time() * 1000)))
    deployment_line_template = "{0} {1} {2}\n"
    rollback_info = ""

    print "# Rollback information saved in " + rollback_info_file

    for deployment in deployments:
        line = deployment_line_template.format(deployment.name, deployment.runtime_name, deployment.server_group)
        rollback_info += line

    write_to_file(rollback_info_file, rollback_info)

def write_to_file(file, content):
    """Write content to file."""
    with open(file, "w") as f:
        f.write(content)

def get_latest_rollback_file(files):
    """Given a list of rollback file names, return the latest file name based on the name's timestamp."""
    if not files:
        return None
    timestamps = sorted([int(x.split("_")[1]) for x in files], reverse=True)
    latest = timestamps[0]
    return "rollback-info_" + str(latest)

def read_rollback_info():
    """Search the current directory for the latest rollback-info_* file. Return the content as a deployment list."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    files = list_rollback_files(current_dir)

    rollback_filename = get_latest_rollback_file(files)

    if not rollback_filename:
        print "# Could not find any rollback information on directory " + current_dir
        exit(2)

    rollback_file_path = current_dir + os.sep + rollback_filename
    print "# Using rollback information from " + rollback_file_path

    archives = []
    with open(rollback_file_path) as f:
        for line in f:
            (name, runtime_name, server_group) = line.split()
            archives.append(jbosscli.Deployment(name, runtime_name, server_group=server_group))

    return archives

def list_rollback_files(directory):
    """List files in the directory whose name starts with rollback-info_. Return a list with the filenames.

    Arguments:
    directory -- the directory to search the files
    """
    rollback_files_pattern = directory + os.sep + "rollback-info_*"

    return glob.glob(rollback_files_pattern)

if __name__ == "__main__": main()
