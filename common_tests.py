import unittest
from mock import MagicMock
from mock import patch
from StringIO import StringIO

import common
from jbosscli import Deployment

class CommonTests(unittest.TestCase):
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

if __name__ == "__main__":
    unittest.main()
