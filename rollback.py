import os
import glob
import time
import jbosscli.jbosscli as jbosscli
import common
import cli_output

current_dir = os.path.dirname(os.path.abspath(__file__))

def persist_rollback_info(deployments):
    """Write name, runtime_name and server group of all enabled deployments to be replaced to a file named rollback-info_<timestamp>."""
    if not deployments:
        return

    rollback_info_file = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + "rollback-info_" + str(int(round(time.time() * 1000)))
    deployment_line_template = "{0} {1} {2}\n"
    rollback_info = ""

    for deployment in deployments:
        line = deployment_line_template.format(deployment.name, deployment.runtime_name, deployment.server_group)
        rollback_info += line

    common.write_to_file(rollback_info_file, rollback_info)

    return rollback_info_file

def get_latest_rollback_file(files):
    """Given a list of rollback file names, return the latest file name based on the name's timestamp."""
    if not files:
        return None
    timestamps = sorted([int(x.split("_")[1]) for x in files], reverse=True)
    latest = timestamps[0]
    return "rollback-info_" + str(latest)

def get_rollback_file(directory=current_dir):
    files = list_rollback_files(directory)

    rollback_filename = get_latest_rollback_file(files)

    if not rollback_filename:
        return None

    rollback_file_path = current_dir + os.sep + rollback_filename

    return rollback_file_path

def read_rollback_info(rollback_file_path):
    """Search the current directory for the latest rollback-info_* file. Return the content as a deployment list."""
    archives = []
    lines = common.read_from_file(rollback_file_path)
    for line in lines:
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

def generate_rollback_script(args):
    controller = common.initialize_controller(args)

    if not controller:
        return "# Cannot initialize the controller " + args.controller

    rollback_file = get_rollback_file()
    #TODO Caso o arquivo seja None, retornar o texto de erro.

    archives = read_rollback_info(rollback_file)
    enabled_deployments = common.fetch_enabled_deployments(controller, archives)

    header = "# Using rollback information from " + rollback_file
    undeploy_script = cli_output.generate_undeploy_script(enabled_deployments)
    deploy_script = cli_output.generate_deploy_script(archives)

    script = "{0}\n{1}\n{2}".format(header, undeploy_script, deploy_script)

    return script
