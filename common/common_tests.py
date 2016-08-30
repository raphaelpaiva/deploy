import unittest
from mock import MagicMock
from mock import patch
from StringIO import StringIO

import os

import common
from jbosscli import Deployment

class CommonTests(unittest.TestCase):

    def test_is_archive__warfile_shouldReturnTrue(self):
        self.assertTrue(common.is_archive('aaa.war'))
    def test_is_archive__notWarFle_shouldReturnFalse(self):
        self.assertFalse(common.is_archive('aaa'))
    def test_is_archive_file_jarFile_shouldReturnTrue(self):
        self.assertTrue(common.is_archive('aaa.jar'))

    def test_extract_tag_fullPath_shouldReturnLastDir(self):
        path = os.path.join("/tmp", "deploy", "5.0.0-alfa-24")
        expected_tag="5.0.0-alfa-24"
        self.assertEqual(common.extract_tag(path), expected_tag)
    def test_extract_tag_fullPathTrailingSlash_shouldReturnLastDir(self):
        path = os.path.join("/tmp", "deploy", "5.0.0-alfa-24") + os.path.sep
        expected_tag="5.0.0-alfa-24"
        self.assertEqual(common.extract_tag(path), expected_tag)
    def test_extract_tag_onlyDirName_shouldReturnDirName(self):
        path = "5.0.0-alfa-24"
        expected_tag="5.0.0-alfa-24"
        self.assertEqual(common.extract_tag(path), expected_tag)
    def test_extract_tag_onlyDirNameWithTrailingSlash_shouldReturnDirName(self):
        path = "5.0.0-alfa-24" + os.path.sep
        expected_tag="5.0.0-alfa-24"
        self.assertEqual(common.extract_tag(path), expected_tag)

    @patch("sys.stdout", new_callable=StringIO)
    def test_initialize_controller(self, mock_stdout):
        args = MagicMock()
        args.controller = "host:port"
        args.auth = "user:passw"

        value = common.initialize_controller(args)

        self.assertIsNone(value)
        self.assertEquals(mock_stdout.getvalue(), "Failed to parse: host:port\n")

    def test_fetch_enabled_deployments_emptyArchives_shouldReturnEnabledDeployments(self):
        controller = MagicMock()
        archives = []
        controller_deployments = [Deployment("name", "runtime_name", server_group="server_group", enabled=True), Deployment("uname", "uruntime_name", server_group="server_group", enabled=False)]
        controller.get_assigned_deployments = MagicMock(return_value=controller_deployments)

        enabled_deployments = common.fetch_enabled_deployments(controller, archives)

        self.assertEquals(len(enabled_deployments), 1)
        self.assertEquals(enabled_deployments[0].name, "name")

    def test_fetch_enabled_deployments_archivesContainsEnabledDeployment_shouldUpdateArchives(self):
        controller = MagicMock()
        archives = [Deployment("name", "runtime_name", server_group="server_group")]
        controller_deployments = [Deployment("name", "runtime_name", server_group="server_group", enabled=True), Deployment("uname", "uruntime_name", server_group="server_group", enabled=False)]
        controller.get_assigned_deployments = MagicMock(return_value=controller_deployments)

        enabled_deployments = common.fetch_enabled_deployments(controller, archives)

        self.assertEquals(len(enabled_deployments), 1)
        self.assertEquals(enabled_deployments[0].name, "name")
        self.assertEquals(enabled_deployments[0].enabled, True)

    @patch("os.listdir", MagicMock(return_value=["aaa.war", "bbb.war", "ccc.txt", "ddd.jar"]))
    def test_read_archive_files(self):
        tag = "5.0.0.1"
        path = "/tmp/deploy/" + tag

        deployments = common.read_archive_files(path, tag)

        self.assertEqual(len(deployments), 3)
        self.assertEqual(deployments[0].name, "aaa-5.0.0.1")
        self.assertEqual(deployments[0].runtime_name, "aaa.war")

        self.assertEqual(deployments[1].name, "bbb-5.0.0.1")
        self.assertEqual(deployments[1].runtime_name, "bbb.war")

        self.assertEqual(deployments[2].name, "ddd-5.0.0.1")
        self.assertEqual(deployments[2].runtime_name, "ddd.jar")

    @patch("os.listdir", MagicMock(return_value=["aaa.war", "bbb.war", "ccc.txt", "ddd.jar"]))
    def test_read_archive_files_filesSpecified_shouldReturnOnlySpecifiedFiles(self):
        tag = "5.0.0.1"
        path = "/tmp/deploy/" + tag
        files = ['aaa.war', 'bbb.war']

        deployments = common.read_archive_files(path, tag, files)

        self.assertEqual(len(deployments), 2)
        self.assertEqual(deployments[0].name, "aaa-5.0.0.1")
        self.assertEqual(deployments[0].runtime_name, "aaa.war")

        self.assertEqual(deployments[1].name, "bbb-5.0.0.1")
        self.assertEqual(deployments[1].runtime_name, "bbb.war")

if __name__ == "__main__":
    unittest.main()
