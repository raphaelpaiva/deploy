#!/usr/bin/python

import jbosscli.jbosscli as jbosscli
import argparse

def main():
    args = parse_args()
    cleanup(args.controller, args.auth, args.deployments_to_keep)

def parse_args():
    parser = argparse.ArgumentParser(description="Generates jboss-cli commands to remove disabled deployments based on lexicographical order of their names.")

    parser.add_argument("--controller",
                        help="The controller to deploy to.",
                        default="localhost:9990")

    parser.add_argument("--auth",
                        help="The credentials to authenticate on the controller.",
                        default="jboss:jboss@123")

    parser.add_argument("--deployments-to-keep", "-k",
                        help="The minimum number of disabled deployments to keep. Defaults to 2.",
                        type=int,
                        default=2)

    return parser.parse_args()

def cleanup(controller, auth, num_deployments_to_keep):
    cli = jbosscli.Jbosscli(controller, auth)

    all_deployments = cli.get_deployments()

    not_enabled = [x for x in all_deployments if not x.enabled]

    deployments_by_runtime_name = {}

    for d in not_enabled:
        if d.runtime_name not in deployments_by_runtime_name:
            deployments_by_runtime_name[d.runtime_name] = []

        deployments_by_runtime_name[d.runtime_name].append(d)

    for item in deployments_by_runtime_name.values():
        if len(item) > num_deployments_to_keep:
            sorted_deployments = sorted(item, key=lambda x: x.name)
            for d in sorted_deployments[0:len(item) - num_deployments_to_keep]:
                print "undeploy {0}{1}".format(d.name, " --all-relevant-server-groups" if cli.domain else "")

if __name__ == "__main__": main()
