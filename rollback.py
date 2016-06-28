import os
import glob
import time
import jbosscli.jbosscli as jbosscli

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
