#!/usr/bin/python
import os
import sys
import argparse
import cli_output
import jbosscli.jbosscli as jbosscli

def main():
    args = parse_args()
    path = os.path.abspath(args.path) + os.sep
    undeploy_pattern = args.undeploy_pattern
    skip_undeploy = True if undeploy_pattern else args.skip_undeploy
    undeploy_tag = args.undeploy_tag if args.undeploy_tag else ".war"

    controller = initialize_controller(args)

    tag = extract_tag(path)
    wars = read_war_files(path, tag)

    enabled_deployments = []

    if controller:
        enabled_deployments = fetch_enabled_deployments(controller, wars)
        cli_output.print_undeploy_script(enabled_deployments, "")
    else:
        if not skip_undeploy:
            cli_output.print_undeploy_script(wars, undeploy_tag)

        if undeploy_pattern:
            cli_output.print_undeploy_pattern(undeploy_pattern)

    cli_output.print_deploy_script(wars)

def parse_args():
    parser = argparse.ArgumentParser(description="Generates [un]deploy commands which you can pipe through jboss-cli script.")

    parser.add_argument("path", help="the path where the .war packages are stored")

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

    return parser.parse_args()

def initialize_controller(args):
    try:
        return jbosscli.Jbosscli(args.controller, args.auth)
    except Exception as e:
        print e
        return None

def read_war_files(path, tag):
    wars = []
    for file in os.listdir(path):
        if is_war(file):
            runtime_name = file.split(os.sep)[-1]
            name = runtime_name.replace(".war", "") + "-" + tag
            enabled = False
            deployment = jbosscli.Deployment(name, runtime_name, enabled, path=path + file)
            wars.append(deployment)

    return wars

def is_war(file):
    return file.endswith('.war')

def extract_tag(path):
    if path.endswith(os.sep):
        path = path[:-1]

    return path.split(os.sep)[-1]

def fetch_enabled_deployments(controller, wars):
    deployments = controller.get_deployments()

    runtime_names = {}
    for war in wars:
        runtime_names[war.runtime_name] = war

    enabled_deployments = []
    for deployment in deployments:
        if deployment.runtime_name in runtime_names and deployment.enabled:
            enabled_deployments.append(deployment)
            runtime_names[deployment.runtime_name].enabled = True
            runtime_names[deployment.runtime_name].server_group = deployment.server_group

    return enabled_deployments

if __name__ == "__main__": main()
