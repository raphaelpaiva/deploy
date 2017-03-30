import os
import unittest
import cli_output
from jbosscli import Deployment

deploy_dir = os.path.join("/tmp", "deploy")

class CliOutputTests(unittest.TestCase):

    def test_prepare_deploy_statement_warfile(self):
        path = deploy_dir + os.path.sep + "archive.war"
        deployment = Deployment(
            {"name": "archive-notag", "runtime-name": "archive.war", "enabled": False},
            None
        )

        actual_statement = cli_output.prepare_deploy_statement(deployment, deploy_dir)
        expected_statement = 'deploy ' + path + \
            ' --runtime-name=archive.war --name=archive-notag'

        self.assertEqual(actual_statement, expected_statement)

    def test_prepare_deploy_statement_jarfile(self):
        path = deploy_dir + os.path.sep + "archive.jar"
        deployment = Deployment(
            {"name": "archive-notag", "runtime-name": "archive.jar", "enabled": False},
            None
        )

        actual_statement = cli_output.prepare_deploy_statement(deployment, deploy_dir)
        expected_statement = 'deploy ' + path + \
            ' --runtime-name=archive.jar --name=archive-notag'

        self.assertEqual(actual_statement, expected_statement)

    def test_prepare_undeploy_statement_warfile(self):
        deployment = Deployment(
            {"name": "archive-tag", "runtime-name": "archive.war", "enabled": True},
            None
        )
        self.assertEqual(cli_output.prepare_undeploy_statement(deployment),
                         "undeploy archive-tag --keep-content")

    def test_prepare_undeploy_statement_warfile_withUndeployTag(self):
        deployment = Deployment(
            {"name": "archive-tag", "runtime-name": "archive.war", "enabled": True},
            None
        )

        self.assertEqual(
            cli_output.prepare_undeploy_statement(deployment, "undeploy_tag"),
            "undeploy archive-undeploy_tag --keep-content"
        )

    def test_prepare_undeploy_statement_jarfile_withUndeployTag(self):
        deployment = Deployment(
            {"name": "archive-tag", "runtime-name": "archive.jar", "enabled": True},
            None
        )
        self.assertEqual(
            cli_output.prepare_undeploy_statement(deployment, "undeploy_tag"),
            "undeploy archive-undeploy_tag --keep-content"
        )

    def test_prepare_undeploy_statement_jarfile(self):
        deployment = Deployment(
            {"name": "archive-tag", "runtime-name": "archive.jar", "enabled": True},
            None
        )
        self.assertEqual(
            cli_output.prepare_undeploy_statement(deployment),
            "undeploy archive-tag --keep-content"
        )

if __name__ == "__main__":
    unittest.main()
