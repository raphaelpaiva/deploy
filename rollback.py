import os
import glob
import time

from jbosscli import Deployment
import common
import cli_output

current_dir = os.path.dirname(os.path.abspath(__file__))

def persist_rollback_info(deployments, rollback_filename_template="rollback-info_"):
    """Write name, runtime_name and server group of all enabled deployments to be replaced to a file named rollback-info_<timestamp>."""
    if not deployments:
        return

    rollback_info_file = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + rollback_filename_template + str(int(round(time.time() * 1000)))
    deployment_line_template = "{0} {1} {2}\n"
    rollback_info = ""

    for deployment in deployments:
        line = deployment_line_template.format(deployment.name, deployment.runtime_name, deployment.server_group)
        rollback_info += line

    common.write_to_file(rollback_info_file, rollback_info)

    return rollback_info_file

def get_latest_rollback_file(files, rollback_filename_template="rollback-info_"):
    """Given a list of rollback file names, return the latest file name based on the name's timestamp."""
    if not files:
        return None
    timestamps = sorted([int(x.split("_")[1]) for x in files], reverse=True)
    latest = timestamps[0]
    return rollback_filename_template + str(latest)

def get_rollback_file(directory=current_dir, rollback_filename_template="rollback-info_"):
    files = list_rollback_files(directory, rollback_filename_template)

    rollback_filename = get_latest_rollback_file(files, rollback_filename_template)

    if not rollback_filename:
        return None

    rollback_file_path = directory + os.sep + rollback_filename

    return rollback_file_path

def read_rollback_info(rollback_file_path):
    """Search the current directory for the latest rollback-info_* file. Return the content as a deployment list."""
    archives = []
    lines = common.read_from_file(rollback_file_path)
    for line in lines:
        (name, runtime_name, server_group) = line.split()
        archives.append(Deployment(name, runtime_name, server_group=server_group))

    return archives

def list_rollback_files(directory, rollback_filename_template="rollback-info_"):
    """List files in the directory whose name starts with rollback-info_. Return a list with the filenames.

    Arguments:
    directory -- the directory to search the files
    """
    rollback_files_pattern = directory + os.sep + rollback_filename_template + "*"

    return glob.glob(rollback_files_pattern)

def generate_rollback_filename_template(rollback_info_file_suffix):
    if not rollback_info_file_suffix:
        return "rollback-info_"
    else:
        return "rollback-info-{0}_".format(rollback_info_file_suffix)

def generate_rollback_script(args):
    controller = common.initialize_controller(args)

    if not controller:
        return "# Cannot initialize the controller {0}. Rollback will not occour.".format(args.controller)

    rollback_filename_template = generate_rollback_filename_template(args.rollback_info_file_suffix)

    rollback_file = get_rollback_file(rollback_filename_template=rollback_filename_template)

    if not rollback_file:
        return "# Cannot find rollback-info file in {0}. Rollback will not occour.".format(current_dir)

    archives = read_rollback_info(rollback_file)
    enabled_deployments = common.fetch_enabled_deployments(controller, archives)

    header = "# Using rollback information from " + rollback_file
    undeploy_script = cli_output.generate_undeploy_script(enabled_deployments)
    deploy_script = cli_output.generate_deploy_script(archives)

    script = "{0}\n{1}\n{2}".format(header, undeploy_script, deploy_script)

    return script
