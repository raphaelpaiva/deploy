#!/usr/bin/python
import os
import sys
import argparse
import cli_output

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="the path where the .war packages are stored")
    parser.add_argument("--domain",
                        help="prepare statements for domain mode, instead of standalone",
                        action="store_true")
    args = parser.parse_args()

    path = os.path.abspath(args.path) + "/"
    wars = read_war_files(path)
    tag = extract_tag(path)

    cli_output.print_undeploy_script(wars)
    cli_output.print_deploy_script(wars, tag)

def usage():
    print "Please provide the full path where the war files are located"
    print "Example:"
    print "  $ " + sys.argv[0] + " /path/to/deployment/"
    exit(1)

def error(message=None, code=1):
    if message != None:
        print "[ERROR]: " + message

    usage()
    exit(code)

def read_war_files(path):
    wars = []
    for file in os.listdir(path):
        if is_war(file):
            wars.append(path + file)

    return wars

def is_war(file):
    return file.endswith('.war')

def extract_tag(path):
    if path.endswith("/"):
        path = path[:-1]

    return path.split("/")[-1]

if __name__ == "__main__": main()
