#!/usr/bin/python
import os

import unittest
import deploy
from jbosscli import Deployment

from mock import MagicMock
from mock import patch
from mock import ANY

current_dir = os.path.dirname(os.path.abspath(__file__))


class TestDeploy(unittest.TestCase):

    def test_generate_deploy_script_emptyParams_shouldReturnEmptyString(self):
        expected_script = ""
        args = MagicMock()

        script = deploy.generate_undeploy_script(args)

        self.assertEqual(script, expected_script)

    def test_generate_deploy_script_skipUndeployTrue_ReturnEmptyString(self):
        expected_script = ""
        args = MagicMock()
        args.skip_undeploy = True

        script = deploy.generate_undeploy_script(args)

        self.assertEqual(script, expected_script)

    def test_generate_deploy_script_undeployPattern_ReturnUndeployString(self):
        expected_script = "undeploy --name=system-* --keep-content"
        args = MagicMock()
        args.undeploy_pattern = "system-*"
        args.skip_undeploy = False

        script = deploy.generate_undeploy_script(args)

        self.assertEqual(script, expected_script)

    def test_generate_deploy_script_withArchives_ReturnUndeployString(self):
        expected_script = "\nundeploy system-v1.2.3 --keep-content"
        args = MagicMock()
        args.skip_undeploy = False
        args.undeploy_pattern = None
        args.undeploy_tag = None

        archives = [Deployment("system-v1.2.3", "system.war")]

        script = deploy.generate_undeploy_script(args, archives)

        self.assertEqual(script, expected_script)

    @patch("deploy.common.write_to_file", MagicMock())
    def test_persist_rollback_info_emptyDeploymentList_DoNotWriteFile(self):
        deployments = []

        deploy.persist_rollback_info(deployments)

        deploy.common.write_to_file.assert_not_called()

    @patch("deploy.common.write_to_file", MagicMock())
    def test_persist_rollback_info_NullDeploymentList_shouldNotWriteFile(self):
        deployments = None

        deploy.persist_rollback_info(deployments)

        deploy.common.write_to_file.assert_not_called()

    @patch("deploy.common.write_to_file", MagicMock())
    def test_persist_rollback_info_oneDeployment_shouldWriteFile(self):
        deployments = [Deployment("abc", "abc.war", server_group="group")]

        deploy.persist_rollback_info(deployments)

        deploy.common.write_to_file.assert_called_with(
            ANY,
            "abc abc.war group\n"
        )

    @patch("deploy.common.write_to_file", MagicMock())
    def test_persist_rollback_info_twoDeployments_shouldWriteFile(self):
        deployments = [
            Deployment("abc", "abc.war", server_group="group"),
            Deployment("cba-v5.2.0", "cba.war", server_group="pourg")
        ]

        deploy.persist_rollback_info(deployments)

        deploy.common.write_to_file.assert_called_with(
            ANY,
            "abc abc.war group\ncba-v5.2.0 cba.war pourg\n"
        )

    @patch("deploy.os.path.isfile", MagicMock(return_value=True))
    @patch("deploy.common.read_from_file", MagicMock(return_value=["abc.war=group"]))
    def test_read_server_group_mapping_OneMapping_ShouldReturnValidMap(self):
        expected_mapping = {
            "abc.war": "group"
        }

        mapping = deploy.read_server_group_mapping("dummy_file")
        self.assertEqual(mapping, expected_mapping)

    @patch("deploy.os.path.isfile", MagicMock(return_value=True))
    @patch("deploy.common.read_from_file", MagicMock(return_value=["abc.war=group\n"]))
    def test_read_server_group_mapping_OneMappingWithoutStrip_ShouldReturnValidMap(self):
        expected_mapping = {
            "abc.war": "group"
        }

        mapping = deploy.read_server_group_mapping("dummy_file")
        self.assertEqual(mapping, expected_mapping)

    @patch("deploy.os.path.isfile", MagicMock(return_value=True))
    @patch("deploy.common.read_from_file", MagicMock(return_value=["abc.war=group", "cba.war=other"]))
    def test_read_server_group_mapping_TwoMappings_ShouldReturnValidMap(self):
        expected_mapping = {
            "abc.war": "group",
            "cba.war": "other"
        }

        mapping = deploy.read_server_group_mapping("dummy_file")
        self.assertEqual(mapping, expected_mapping)

    @patch("deploy.os.path.isfile", MagicMock(return_value=True))
    @patch("deploy.common.read_from_file", MagicMock(return_value=["abc.war=group", ""]))
    def test_read_server_group_mapping_TrailingLine_ShouldReturnValidMap(self):
        expected_mapping = {
            "abc.war": "group"
        }

        mapping = deploy.read_server_group_mapping("dummy_file")
        self.assertEqual(mapping, expected_mapping)

    @patch("deploy.os.path.isfile", MagicMock(return_value=True))
    @patch("deploy.common.read_from_file", MagicMock(return_value=["abc.war=group", "", "", "cba.war=other", ""]))
    def test_read_server_group_mapping_BlankLines_ShouldReturnValidMap(self):
        expected_mapping = {
            "abc.war": "group",
            "cba.war": "other"
        }

        mapping = deploy.read_server_group_mapping("dummy_file")
        self.assertEqual(mapping, expected_mapping)

# -- "Acceptance" Tests:

    @patch("deploy.common.fetch_enabled_deployments", MagicMock(return_value=[Deployment("abc-v1.0.0", "abc.war", server_group="group")]))
    @patch("deploy.common.read_from_file", MagicMock(return_value=["abc.war=group"]))
    @patch("os.path.isfile", MagicMock(return_value=True))
    @patch("__main__.deploy.persist_rollback_info", MagicMock(return_value=current_dir + os.sep + "rollback-info_test"))
    @patch("deploy.common.read_archive_files", MagicMock(return_value=[Deployment("abc-v1.2.3", "abc.war", path=current_dir + os.sep + "v1.2.3" + os.sep + "abc.war")]))
    def test_generate_deploy_script_receiving_data_from_controller(self):
        expected_script = """\
# Rollback information saved in {0}rollback-info_test

undeploy abc-v1.0.0 --keep-content --all-relevant-server-groups

deploy {1} --runtime-name=abc.war --name=abc-v1.2.3 --server-groups=group\
""".format(current_dir + os.sep,
           current_dir + os.sep + "v1.2.3" + os.sep + "abc.war")

        args = MagicMock()
        args.path = current_dir + os.sep + "v1.2.3"
        args.undeploy_pattern = None
        args.undeploy_tag = None
        args.restart = False

        mock_controller = MagicMock()
        mock_controller.domain = True
        deploy.common.initialize_controller = MagicMock(
            return_value=mock_controller
        )

        script = deploy.generate_deploy_script(args)

        self.assertEqual(script, expected_script)

    @patch("deploy.common.fetch_enabled_deployments", MagicMock(return_value=[Deployment("abc-v1.0.0", "abc.war", server_group="group")]))
    @patch("deploy.common.read_from_file", MagicMock(return_value=["abc.war=group"]))
    @patch("os.path.isfile", MagicMock(return_value=True))
    @patch("__main__.deploy.persist_rollback_info", MagicMock(return_value=current_dir + os.sep + "rollback-info_test"))
    @patch("deploy.common.read_archive_files", MagicMock(return_value=[Deployment("abc-v1.2.3", "abc.war", path=current_dir + os.sep + "v1.2.3" + os.sep + "abc.war")]))
    def test_generate_deploy_script_withRestartOption_ShouldPrintStopStart(self):
        expected_script = """\
# Rollback information saved in {0}rollback-info_test
:stop-servers()

undeploy abc-v1.0.0 --keep-content --all-relevant-server-groups

deploy {1} --runtime-name=abc.war --name=abc-v1.2.3 --server-groups=group
:start-servers()\
""".format(current_dir + os.sep,
           current_dir + os.sep + "v1.2.3" + os.sep + "abc.war")

        args = MagicMock()
        args.path = current_dir + os.sep + "v1.2.3"
        args.undeploy_pattern = None
        args.undeploy_tag = None
        args.restart = True

        mock_controller = MagicMock()
        mock_controller.domain = True
        deploy.common.initialize_controller = MagicMock(
            return_value=mock_controller
        )

        script = deploy.generate_deploy_script(args)

        self.assertEqual(script, expected_script)


    @patch("deploy.common.fetch_enabled_deployments",
           MagicMock(return_value=[]))
    @patch("deploy.common.read_from_file",
           MagicMock(return_value=["abc.war=group"]))
    @patch("os.path.isfile", MagicMock(return_value=True))
    @patch("deploy.common.read_archive_files",
           MagicMock(return_value=[
            Deployment("abc-v1.2.3",
                       "abc.war",
                       path=current_dir + os.sep +
                       "v1.2.3" + os.sep + "abc.war")
                       ]))
    def test_generate_deploy_script_noEnabledDeployments_DoNotPrintRollbackHeader(self):
        expected_script = """


deploy {1} --runtime-name=abc.war --name=abc-v1.2.3 --server-groups=group\
""".format(current_dir + os.sep,
           current_dir + os.sep + "v1.2.3" + os.sep + "abc.war")
        args = MagicMock()
        args.path = current_dir + os.sep + "v1.2.3"
        args.undeploy_pattern = None
        args.undeploy_tag = None
        args.restart = False

        mock_controller = MagicMock()
        mock_controller.domain = True
        deploy.common.initialize_controller = MagicMock(
            return_value=mock_controller
        )

        script = deploy.generate_deploy_script(args)

        self.assertEqual(script, expected_script)

    @patch("deploy.common.read_archive_files",
           MagicMock(return_value=[
            Deployment("system-v1.2.3",
                       "system.war",
                       path=current_dir + os.sep + "v1.2.3" + os.sep +
                       "system.war")
                    ]))
    def test_generate_deploy_script_skip_local_undeploy(self):
        expected_script = """

undeploy system-sometag --keep-content

deploy {0}system.war --runtime-name=system.war --name=system-v1.2.3\
""".format(current_dir + os.sep + "v1.2.3" + os.sep)

        args = MagicMock()
        args.skip_undeploy = False
        args.path = current_dir + os.sep + "v1.2.3"
        args.undeploy_pattern = None
        args.undeploy_tag = "sometag"
        args.restart = False

        deploy.common.initialize_controller = MagicMock(return_value=None)

        script = deploy.generate_deploy_script(args)

        self.assertEqual(script, expected_script)

if __name__ == '__main__':
    unittest.main()
