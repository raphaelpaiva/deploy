import unittest
from mock import MagicMock
from mock import patch

import cleanup
from jbosscli import Deployment

mock_deployments = [
    Deployment({"name": "dep-v1.2.3", "runtime-name": "dep.war", "enabled": True}, None),
    Deployment({"name": "dep-v1.2.2", "runtime-name": "dep.war", "enabled": False}, None),
    Deployment({"name": "dep-v1.2.1", "runtime-name": "dep.war", "enabled": False}, None),
    Deployment({"name": "sys-v1.0.0", "runtime-name": "sys.war", "enabled": True}, None)
]


class CleanupTests(unittest.TestCase):

    @patch("cleanup.common.get_assigned_deployments", MagicMock(return_value=mock_deployments))
    def test_fetch_not_enabled_deployments(self):
        cli_mock = MagicMock()

        not_enabled = cleanup.fetch_not_enabled_deployments(cli_mock)

        self.assertEqual(len(not_enabled), 2)

        names = [x.name for x in not_enabled]
        self.assertTrue("dep-v1.2.2" in names,
                        msg="Expected dep-v1.2.2 not to be enabled")

        self.assertTrue("dep-v1.2.1" in names,
                        msg="Expected dep-v1.2.1 not to be enabled")

    def test_map_deployments_by_runtime_name(self):
        deployments = [
            Deployment({"name": "dep-v1.2.2", "runtime-name": "dep.war", "enabled": True}, None),
            Deployment({"name": "dep-v1.2.1", "runtime-name": "dep.war", "enabled": True}, None),
            Deployment({"name": "app-v1.0.1", "runtime-name": "app.war", "enabled": True}, None)
        ]

        mapped = cleanup.map_deployments_by_runtime_name(deployments)

        self.assertTrue("dep.war" in mapped,
                        msg="Expected dep.war to be mapped")
        self.assertTrue("app.war" in mapped,
                        msg="Expected app.war to be mapped")

        self.assertEqual(len(mapped["dep.war"]), 2)
        self.assertEqual(len(mapped["app.war"]), 1)

        self.assertEqual(mapped["app.war"][0].name, "app-v1.0.1")

        names = [x.name for x in mapped["dep.war"]]
        self.assertTrue("dep-v1.2.2" in names,
                        msg="Expected dep-v1.2.2 to be mapped to dep.war")
        self.assertTrue("dep-v1.2.1" in names,
                        msg="Expected dep-v1.2.1 to be mapped to dep.war")

    @patch("cleanup.common.initialize_controller")
    @patch("cleanup.common.get_assigned_deployments", MagicMock(return_value=mock_deployments))
    def test_generate_cleanup_script_notDomain_shouldNotPrintAllRelevantServerGroups(self, init_mock):
        cli_mock = MagicMock()
        cli_mock.domain = False

        init_mock.return_value = cli_mock
        args = MagicMock()
        args.controller = "host:port"
        args.auth = "user:passw"
        args.deployments_to_keep = 1

        expected_script = """
undeploy dep-v1.2.1\
"""

        script = cleanup.generate_cleanup_script(args)

        init_mock.assert_called_with(args)
        self.assertEqual(script, expected_script)

    @patch("cleanup.common.initialize_controller")
    @patch("cleanup.common.get_assigned_deployments", MagicMock(return_value=mock_deployments))
    def test_generate_cleanup_script_Domain_shouldPrintAllRelevantServerGroups(self, init_mock):
        cli_mock = MagicMock()
        cli_mock.domain = True

        init_mock.return_value = cli_mock
        args = MagicMock()
        args.controller = "host:port"
        args.auth = "user:passw"
        args.deployments_to_keep = 1

        expected_script = """
undeploy dep-v1.2.1 --all-relevant-server-groups\
"""

        script = cleanup.generate_cleanup_script(args)

        init_mock.assert_called_with(args)
        self.assertEqual(script, expected_script)

    @patch("cleanup.common.initialize_controller")
    @patch("cleanup.common.get_assigned_deployments", MagicMock(return_value=mock_deployments))
    def test_generate_cleanup_script_numDeploymentsToKeepGreaterThanDeployments_shouldNotPrintScript(self, init_mock):
        cli_mock = MagicMock()
        cli_mock.domain = True

        init_mock.return_value = cli_mock
        args = MagicMock()
        args.controller = "host:port"
        args.auth = "user:passw"
        args.deployments_to_keep = 2

        expected_script = ""

        script = cleanup.generate_cleanup_script(args)

        init_mock.assert_called_with(args)
        self.assertEqual(script, expected_script)

    @patch("cleanup.common.initialize_controller",
           MagicMock(return_value=None))
    def test_generate_cleanup_script_NullController_shouldPrintErrorMessage(self):
        args = MagicMock()
        args.controller = "host:port"
        args.auth = "user:passw"

        expected_script = """\
# Could not initialize controller host:port. Cleanup will not occour.\
"""

        script = cleanup.generate_cleanup_script(args)

        cleanup.common.initialize_controller.assert_called_with(args)
        self.assertEqual(script, expected_script)

if __name__ == "__main__":
    unittest.main()
