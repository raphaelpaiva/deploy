import os
import argparse
import tempfile
import rollback
import deploy

def main():
    args = parse_args()
    args.func(args)

def parse_args():
    default_server_group_mapping_file = tempfile.gettempdir() + os.sep + "server-group-mapping.properties"

    parser = argparse.ArgumentParser(description="Generates [un]deploy commands which you can pipe through jboss-cli script.")

    parser.add_argument("-c", "--controller",
                        help="The controller to interact with.",
                        default="localhost:9990")

    parser.add_argument("-a", "--auth",
                        help="The credentials to authenticate on the controller",
                        default="jboss:jboss@123")

    subparsers = parser.add_subparsers(title="subcomands", help="choose an action to take")

    deploy_parser = subparsers.add_parser("deploy", description="Generates [un]deloy commands for the packages inside PATH. The deployment name is appended with de name of the leaf directory in PATH.")
    deploy_parser.set_defaults(func=do_deploy)

    deploy_parser.add_argument("path", help="the path where the archive (.ear, .war, .jar) packages are stored")

    deploy_parser.add_argument("--skip-undeploy",
                        help="do not generate undeploy commands",
                        action="store_true")

    deploy_parser.add_argument("--undeploy-pattern",
                        help="specify a regex pattern for the undeploy cammands. This implies --skip-undeploy.")

    deploy_parser.add_argument("--undeploy-tag",
                        help="specify a tag to append for the undeploy cammand.")

    deploy_parser.add_argument("--server-group-mapping-file",
                        help="A file containing a runtime-name=server-group mapping. Defaults to /tmp/server-group-mapping.properties",
                        default=default_server_group_mapping_file)

    rollback_parser = subparsers.add_parser("rollback", description="Generates [un]deploy commands which you can pipe through jboss-cli script.")
    rollback_parser.set_defaults(func=do_rollback)

    return parser.parse_args()

def do_deploy(args):
    print deploy.generate_deploy_script(args)

def do_rollback(args):
    print rollback.generate_rollback_script(args)

if __name__ == "__main__":
    main()
