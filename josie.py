"""josie.py

This module is the entry-point (main) module for the josie scripts.
It's role is to parse arguments and call each specific module according to the
command-line arugments passed.

"""

from __future__ import print_function

import os
import argparse
import tempfile
import sys

import rollback
import deploy
import cleanup
import verify_deployments
import http_test

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    """Parse arguments and call the requested command."""

    args = parse_args()
    args.func(args)


def parse_args():
    """Configure the parser for each module and parse the arguments."""

    parser = argparse.ArgumentParser(
        description="Generates [un]deploy commands which you can " +
        "pipe through jboss-cli script."
    )

    parser.add_argument(
        "-c", "--controller",
        help="The controller to interact with.",
        default="localhost:9990"
    )

    parser.add_argument(
        "-a", "--auth",
        help="The credentials to authenticate on the controller",
        default="jboss:jboss@123"
    )

    subparsers = parser.add_subparsers(
        title="subcomands",
        help="choose an action to take"
    )

    configure_deploy_parser(subparsers)
    configure_rollback_parser(subparsers)
    configure_cleanup_parser(subparsers)
    configure_list_parser(subparsers)
    configure_http_test_parser(subparsers)

    return parser.parse_args()


def configure_deploy_parser(subparsers):
    """Configure the argument parser for the deploy module."""

    default_sv_group_mapping_file = tempfile.gettempdir() + os.sep + \
        "server-group-mapping.properties"

    deploy_parser = subparsers.add_parser(
        "deploy",
        description="Generates [un]deloy commands for the packages inside " +
        "PATH. The deployment name is appended with de name of the leaf " +
        "directory in PATH."
    )

    deploy_parser.set_defaults(func=do_deploy)

    deploy_parser.add_argument(
        "path",
        help="the path where the archive (.ear, .war, .jar) packages are " +
        " stored"
    )

    deploy_parser.add_argument(
        "--skip-undeploy",
        help="do not generate undeploy commands",
        action="store_true"
    )

    deploy_parser.add_argument(
        "--undeploy-pattern",
        help="specify a regex pattern for the undeploy cammands. " +
        "This implies --skip-undeploy."
    )

    deploy_parser.add_argument(
        "--undeploy-tag",
        help="specify a tag to append for the undeploy cammand."
    )

    deploy_parser.add_argument(
        "--server-group-mapping-file",
        help="A file containing a runtime-name=server-group mapping. " +
        "Defaults to /tmp/server-group-mapping.properties",
        default=default_sv_group_mapping_file
    )

    deploy_parser.add_argument(
        "--rollback-info-file-suffix",
        help="Will write rollback-info-<suffix>_<timestamp> files for " +
        "rollback.",
        default=""
    )

    deploy_parser.add_argument(
        "-f", "--file",
        action="append",
        dest="files",
        help="Specify packages to deploy. This doesn't need to be a path, " +
        "but file names.",
        default=[]
    )

    deploy_parser.add_argument(
        "--restart",
        action="store_true",
        help="Stop servers prior to the deploy process and start them after."
    )


def configure_rollback_parser(subparsers):
    """Configure the argument parser for the rollback module."""

    rollback_parser = subparsers.add_parser(
        "rollback",
        description="Rollbacks the last deploy made in a controller."
    )

    rollback_parser.add_argument(
        "--rollback-info-file-suffix",
        help="Will look for rollback-info-<suffix>_<timestamp> files " +
        "for rollback.",
        default=""
    )

    rollback_parser.set_defaults(func=do_rollback)


def configure_cleanup_parser(subparsers):
    """Configure the argument parser for the cleanup module."""

    cleanup_parser = subparsers.add_parser(
        "cleanup",
        description="Generates jboss-cli commands to remove disabled " +
        "deployments based on lexicographical order of their names."
    )

    cleanup_parser.add_argument(
        "--deployments-to-keep", "-k",
        help="The minimum number of disabled deployments to keep. " +
        "Defaults to 2.",
        type=int,
        default=2
    )

    cleanup_parser.set_defaults(func=do_cleanup)


def configure_list_parser(subparsers):
    """Configure the argument parser for the verify_deployments module."""

    list_parser = subparsers.add_parser(
        "verify-deployments",
        description="verifies deployments"
    )

    list_parser.add_argument(
        "path",
        help="the path where the archive (.ear, .war, .jar) " +
        "packages are stored"
    )

    list_parser.set_defaults(func=do_verify_deployments)


def configure_http_test_parser(subparsers):
    """Configure the argument parser for the http_test module."""

    http_test_parser = subparsers.add_parser(
        "http-test",
        description="Teste the context root of deployed modules for http " +
        "responses that are not 5xx or 4xx."
    )

    http_test_parser.add_argument(
        "--base-url",
        help="The base url to test the context roots. If your app is " +
        "http://company.com/app, then base-url is company.com.",
        default=""
    )

    http_test_parser.set_defaults(func=do_http_test)


def do_deploy(args):
    print(deploy.generate_deploy_script(args, CURRENT_DIR))


def do_rollback(args):
    print(rollback.generate_rollback_script(args, CURRENT_DIR))


def do_cleanup(args):
    print(cleanup.generate_cleanup_script(args))


def do_verify_deployments(args):
    run(verify_deployments.verify, args)


def do_http_test(args):
    run(http_test.generate_test_list, args)


def run(func, args):
    """Run `func` with `args` as arguments and parse the result.

    This expects that `func` returns a tulpe containing
    (output, ret_code, err), where:
        * output is the text to be printed to stdout.
        * ret_code is the exit code to be returned by josie.py.
        * err is the text to be printed to stderr.
    """

    result = func(args)

    output = result[0]
    ret_code = result[1]
    err = result[2]

    print(output)
    print(err, file=sys.stderr)
    sys.exit(ret_code)

if __name__ == "__main__":
    main()
