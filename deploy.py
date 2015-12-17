#!/usr/bin/python
import os
import sys
def read_war_files(path):
    wars = []
    for file in os.listdir(path):
        if is_war(file):
            wars.append(path + file)

    return wars

def is_war(file):
    return file.endswith('.war')

def prepare_deploy_statement(war_file):
    tag = "tag"
    archive_name = war_file.split('/')[-1]
    deployment_name = archive_name.replace(".war", "") + "-" + tag

    return "deploy " + war_file + " --runtime-name=" + archive_name + " --name=" + deployment_name

def main():
    if len(sys.argv) <= 1:
        print "Please provide the full path where the war files are located"
        print "Example:"
        print "  $ python deploy.py /path/to/deployment/"
        exit(1)

    path = sys.argv[1]
    wars = read_war_files(path)

    batch = len(wars)

    if  batch > 1:
        print "batch"

    for war in wars:
        print prepare_deploy_statement(war)

    if batch > 1:
        print "run-batch"

if __name__ == "__main__": main()
