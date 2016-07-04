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

    $./josie.py -c mycontroller:9990 --auth user:password deploy /path/to/5.2.0/

    # Rollback information saved in /path/to/rollback-info_1466105982374
    undeploy app-5.1.0 --keep-content
    undeploy app-ext-5.1.1 --keep-content
    deploy /path/to/5.2.0/new-app.war --runtime-name=new-app.war --name=new-app-5.2.0
    deploy /path/to/5.2.0/app-ext.jar --runtime-name=app-ext.jar --name=app-ext-5.2.0
    deploy /path/to/5.2.0/app.war --runtime-name=app.war --name=app-5.2.0

The script will scan the /path/to/5.2.0/ directory for deployments and generates the deploy commands. If the controller reports deployments with the same runtime-name as the new deployments, undeploy commands are generated as well.

Just pipe the output to the jbosscli script:

    $./josie.py --controller mycontroller:9990 --auth user:password deploy /path/to/5.2.0/ | /opt/jboss/bin/jboss-cli --connect controller=mycontroller:9999

And voilá!

A file named rollback-info_&lt;timestamp&gt; will be created containing information for rollback. That is deployment information about the enabled deployments prior to the script run.

Command-line options
--------------------

For a short list, do:

    $josie.py [deploy|rollback|cleanup] --help

    usage: josie.py [-h] [-c CONTROLLER] [-a AUTH] {deploy,rollback,cleanup} ...

    Generates [un]deploy commands which you can pipe through jboss-cli script.

    optional arguments:
      -h, --help            show this help message and exit
      -c CONTROLLER, --controller CONTROLLER
                        The controller to interact with.
      -a AUTH, --auth AUTH  The credentials to authenticate on the controller

      subcomands:
      {deploy,rollback,cleanup}
                              choose an action to take
