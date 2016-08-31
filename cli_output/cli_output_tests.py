import os
import unittest
import cli_output
from jbosscli import Deployment


class CliOutputTests(unittest.TestCase):

    def test_prepare_deploy_statement_warfile(self):
        path = os.path.join("/tmp", "deploy") + os.path.sep + "archive.war"
        deployment = Deployment("archive-notag", "archive.war", path=path)

        actual_statement = cli_output.prepare_deploy_statement(deployment)
        expected_statement = 'deploy ' + path + \
            ' --runtime-name=archive.war --name=archive-notag'

        self.assertEqual(actual_statement, expected_statement)

    def test_prepare_deploy_statement_jarfile(self):
        path = os.path.join("/tmp", "deploy") + os.path.sep + "archive.jar"
        deployment = Deployment("archive-notag", "archive.jar", path=path)

        actual_statement = cli_output.prepare_deploy_statement(deployment)
        expected_statement = 'deploy ' + path + \
            ' --runtime-name=archive.jar --name=archive-notag'

        self.assertEqual(actual_statement, expected_statement)

    def test_prepare_undeploy_statement_warfile(self):
        deployment = Deployment("archive-tag", "archive.war")
        self.assertEqual(cli_output.prepare_undeploy_statement(deployment),
                         "undeploy archive-tag --keep-content")

    def test_prepare_undeploy_statement_warfile_withUndeployTag(self):
        deployment = Deployment("archive-tag", "archive.war")

        self.assertEqual(
            cli_output.prepare_undeploy_statement(deployment, "undeploy_tag"),
            "undeploy archive-undeploy_tag --keep-content"
        )

    def test_prepare_undeploy_statement_jarfile_withUndeployTag(self):
        deployment = Deployment("archive-tag", "archive.jar")
        self.assertEqual(
            cli_output.prepare_undeploy_statement(deployment, "undeploy_tag"),
            "undeploy archive-undeploy_tag --keep-content"
        )

    def test_prepare_undeploy_statement_jarfile(self):
        deployment = Deployment("archive-tag", "archive.jar")
        self.assertEqual(
            cli_output.prepare_undeploy_statement(deployment),
            "undeploy archive-tag --keep-content"
        )

if __name__ == "__main__":
    unittest.main()
