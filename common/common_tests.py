import unittest
from mock import MagicMock
from mock import patch
from StringIO import StringIO

import os

import common
from jbosscli import Deployment
from jbosscli import ServerGroup
from jbosscli import Host

GROUP1_DATA = {
    "name": "server_group1",
    "profile": "profile",
    "socket-binding-group": "bgroup",
    "socket-binding-port-offset": 100,
    "deployment": {
        "deployment1-v2.41": {
            "name": "deployment1-v2.41",
            "runtime-name": "deployment1.war",
            "enabled": True
        },
        "otherdeployment2-v3.21": {
            "name": "otherdeployment2-v3.21",
            "runtime-name": "otherdeployment2.war",
            "enabled": False
        }
    }
}

GROUP2_DATA = {
    "name": "server_group2",
    "profile": "profile",
    "socket-binding-group": "bgroup",
    "socket-binding-port-offset": 100,
    "deployment": {
        "omg1-v2.41": {
            "name": "omg1-v2.41",
            "runtime-name": "omg1.war",
            "enabled": True
        },
        "gmo2-v3.21": {
            "name": "gmo2-v3.21",
            "runtime-name": "gmo2.war",
            "enabled": False
        }
    }
}


class CommonTests(unittest.TestCase):

    def test_is_archive__warfile_shouldReturnTrue(self):
        self.assertTrue(common.is_archive('aaa.war'))

    def test_is_archive__notWarFle_shouldReturnFalse(self):
        self.assertFalse(common.is_archive('aaa'))

    def test_is_archive_file_jarFile_shouldReturnTrue(self):
        self.assertTrue(common.is_archive('aaa.jar'))

    def test_extract_tag_fullPath_shouldReturnLastDir(self):
        path = os.path.join("/tmp", "deploy", "5.0.0-alfa-24")
        expected_tag = "5.0.0-alfa-24"

        self.assertEqual(common.extract_tag(path), expected_tag)

    def test_extract_tag_fullPathTrailingSlash_shouldReturnLastDir(self):
        path = os.path.join("/tmp", "deploy", "5.0.0-alfa-24") + os.path.sep
        expected_tag = "5.0.0-alfa-24"

        self.assertEqual(common.extract_tag(path), expected_tag)

    def test_extract_tag_onlyDirName_shouldReturnDirName(self):
        path = "5.0.0-alfa-24"
        expected_tag = "5.0.0-alfa-24"

        self.assertEqual(common.extract_tag(path), expected_tag)

    def test_extract_tag_DirNameWithTrailingSlash_shouldReturnDirName(self):
        path = "5.0.0-alfa-24" + os.path.sep
        expected_tag = "5.0.0-alfa-24"

        self.assertEqual(common.extract_tag(path), expected_tag)

    @patch("sys.stdout", new_callable=StringIO)
    def test_initialize_controller(self, mock_stdout):
        args = MagicMock()
        args.controller = "host:port"
        args.auth = "user:passw"

        value = common.initialize_controller(args)

        self.assertIsNone(value)
        self.assertEquals(
            mock_stdout.getvalue(),
            "'Error requesting: Failed to parse: host:port code'\n"
        )

    def test_get_assigned_deployments_domain_shouldReturnAllDeploymentsFromServerGroups(self):
        controller = MagicMock(
            domain=True,
            server_groups=[]
        )

        controller.server_groups = [
            ServerGroup(GROUP1_DATA, controller=controller),
            ServerGroup(GROUP2_DATA, controller=controller)
        ]

        actual_deployments = common.get_assigned_deployments(controller)
        self.assertEqual(len(actual_deployments), 4)

    def test_get_assigned_deployments_standalone_shouldReturnDeploymentsFromHost(self):
        controller = MagicMock(
            domain=False,
        )

        host_data = {
            "name": "host",
            "product-name": "",
            "product-version": "",
            "release-codename": "",
            "release-version": "",
            "master": True,
            "deployment": {
                "omg1-v2.41": {
                    "name": "omg1-v2.41",
                    "runtime-name": "omg1.war",
                    "enabled": True
                },
                "gmo2-v3.21": {
                    "name": "gmo2-v3.21",
                    "runtime-name": "gmo2.war",
                    "enabled": False
                }
            }
        }

        controller.hosts = [Host(host_data, controller=controller)]

        actual_deployments = common.get_assigned_deployments(controller)
        self.assertEqual(len(actual_deployments), 2)

    def test_fetch_enabled_deployments_emptyArchives_ReturnEnabledDeployments(self):
        archives = []
        controller = MagicMock(
            domain=True,
            server_groups=[]
        )

        controller.server_groups = [
            ServerGroup(GROUP1_DATA, controller=controller)
        ]

        enabled_deployments = common.fetch_enabled_deployments(
            controller, archives
        )

        self.assertEquals(len(enabled_deployments), 1)
        self.assertEquals(enabled_deployments[0].name, "deployment1-v2.41")

    def test_fetch_enabled_deployments_archivesContainsEnabledDeployment_UpdateArchives(self):
        controller = MagicMock(
            domain=True,
            server_groups=[]
        )

        controller.server_groups = [
            ServerGroup(GROUP2_DATA, controller=controller)
        ]

        archives = [
            Deployment({"name": "omg1-v2.41", "runtime-name": "omg1.war", "enabled": False}, None)
        ]

        enabled_deployments = common.fetch_enabled_deployments(
            controller, archives
        )

        self.assertEquals(len(enabled_deployments), 1)
        self.assertEquals(enabled_deployments[0].name, "omg1-v2.41")
        self.assertEquals(enabled_deployments[0].enabled, True)

    @patch("os.listdir",
           MagicMock(return_value=[
            "aaa.war", "bbb.war", "ccc.txt", "ddd.jar"
           ]))
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

    @patch("os.listdir",
           MagicMock(return_value=[
            "aaa.war", "bbb.war", "ccc.txt", "ddd.jar"
           ]))
    def test_read_archive_files_filesSpecified_ReturnOnlySpecifiedFiles(self):
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
