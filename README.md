JBoss Wildfly cli deploy automation
===================================

Generate jboss-cli deployment script commands from a command

Features
--------

* Direcotry oriented
* Customizable names
* Automatically undeploy previous deployments
* Cleanup
* Deployment rollback
* Supports standalone and domain modes
* Server group mapping

Usage
-----
Suppose you want to deploy version 5.2.0 of your app.

    $deploy.py --controller mycontroller:9990 --auth user:password /path/to/5.2.0/

    # Rollback information saved in /path/to/rollback-info_1466105982374
    undeploy app-5.1.0 --keep-content
    undeploy app-ext-5.1.1 --keep-content
    deploy /path/to/5.2.0/new-app.war --runtime-name=new-app.war --name=new-app-5.2.0
    deploy /path/to/5.2.0/app-ext.jar --runtime-name=app-ext.jar --name=app-ext-5.2.0
    deploy /path/to/5.2.0/app.war --runtime-name=app.war --name=app-5.2.0

The script will scan the /path/to/5.2.0/ directory for deployments and generates the deploy commands. If the controller reports deployments with the same runtime-name as the new deployments, undeploy commands are generated as well.

Just pipe the output to the jbosscli script:

    $deploy.py --controller mycontroller:9990 --auth user:password /path/to/5.2.0/ | /opt/jboss/bin/jboss-cli --connect controller=mycontroller:9999

And voilá!

A file named rollback-info_&lt;timestamp&gt; will be created containing information for rollback. That is deployment information about the enabled deployments prior to the script run.

Command-line options
--------------------

For a short list, do:

    $deploy.py --help

    usage: deploy.py [-h] [--skip-undeploy] [--undeploy-pattern UNDEPLOY_PATTERN]
                 [--undeploy-tag UNDEPLOY_TAG] [--controller CONTROLLER]
                 [--auth AUTH]
                 [--server-group-mapping-file SERVER_GROUP_MAPPING_FILE]
                 [--rollback]
                 path

    Generates [un]deploy commands which you can pipe through jboss-cli script.

    positional arguments:
      path                  the path where the archive (.war, .jar) packages are stored

    optional arguments:
      -h, --help            show this help message and exit
      --skip-undeploy       do not generate undeploy commands
      --undeploy-pattern UNDEPLOY_PATTERN
                            specify a regex pattern for the undeploy cammand. This implies --skip-undeploy.
      --undeploy-tag UNDEPLOY_TAG
                        specify a tag to append for the undeploy cammand.
      --controller CONTROLLER The controller to deploy to.
      --auth AUTH             The credentials to authenticate on the controller
      --server-group-mapping-file SERVER_GROUP_MAPPING_FILE
                        A file containing a runtime-name=server-group mapping.
                        Defaults to /tmp/server-group-mapping.properties
      --rollback        Rollback to a previous deployment. This depends on
                        having a deployment-info file.
