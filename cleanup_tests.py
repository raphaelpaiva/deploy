import unittest
from mock import MagicMock
from mock import patch

import cleanup
from jbosscli import Deployment

mock_deployments = [Deployment("dep-v1.2.3", "dep.war", enabled=True),
                    Deployment("dep-v1.2.2", "dep.war", enabled=False),
                    Deployment("dep-v1.2.1", "dep.war", enabled=False),
                    Deployment("sys-v1.0.0", "sys.war", enabled=True)
]

class CleanupTests(unittest.TestCase):

    def test_fetch_not_enabled_deployments(self):
        cli_mock = MagicMock()

        cli_mock.get_deployments = MagicMock(return_value=mock_deployments)

        not_enabled = cleanup.fetch_not_enabled_deployments(cli_mock)

        self.assertEqual(len(not_enabled), 2)

        names = [x.name for x in not_enabled]
        self.assertTrue("dep-v1.2.2" in names, msg="Expected dep-v1.2.2 not to be enabled")
        self.assertTrue("dep-v1.2.1" in names, msg="Expected dep-v1.2.1 not to be enabled")

    def test_map_deployments_by_runtime_name(self):
        deployments = [Deployment("dep-v1.2.2", "dep.war"),
                       Deployment("dep-v1.2.1", "dep.war"),
                       Deployment("app-v1.0.1", "app.war")
        ]


        mapped = cleanup.map_deployments_by_runtime_name(deployments)

        self.assertTrue("dep.war" in mapped, msg="Expected dep.war to be mapped")
        self.assertTrue("app.war" in mapped, msg="Expected app.war to be mapped")

        self.assertEqual(len(mapped["dep.war"]), 2)
        self.assertEqual(len(mapped["app.war"]), 1)

        self.assertEqual(mapped["app.war"][0].name, "app-v1.0.1")

        names = [x.name for x in mapped["dep.war"]]
        self.assertTrue("dep-v1.2.2" in names, msg="Expected dep-v1.2.2 to be mapped to dep.war")
        self.assertTrue("dep-v1.2.1" in names, msg="Expected dep-v1.2.1 to be mapped to dep.war")

    @patch("cleanup.common.initialize_controller")
    def test_generate_cleanup_script_notDomain_shouldNotPrintAllRelevantServerGroups(self, init_mock):
        cli_mock = MagicMock()
        cli_mock.domain = False

        cli_mock.get_deployments = MagicMock(return_value=mock_deployments)

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
    def test_generate_cleanup_script_Domain_shouldPrintAllRelevantServerGroups(self, init_mock):
        cli_mock = MagicMock()
        cli_mock.domain = True

        cli_mock.get_deployments = MagicMock(return_value=mock_deployments)

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
    def test_generate_cleanup_script_numDeploymentsToKeepGreaterThanDeployments_shouldNotPrintScript(self, init_mock):
        cli_mock = MagicMock()
        cli_mock.domain = True

        cli_mock.get_deployments = MagicMock(return_value=mock_deployments)

        init_mock.return_value = cli_mock
        args = MagicMock()
        args.controller = "host:port"
        args.auth = "user:passw"
        args.deployments_to_keep = 2

        expected_script = ""

        script = cleanup.generate_cleanup_script(args)

        init_mock.assert_called_with(args)
        self.assertEqual(script, expected_script)

    @patch("cleanup.common.initialize_controller", MagicMock(return_value=None))
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
