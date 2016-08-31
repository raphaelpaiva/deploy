import unittest

from mock import MagicMock
from mock import patch

from jbosscli import Deployment

import verify_deployments

deployment_app = Deployment("app-1.2.3", "app.war", enabled=True)
deployment_ppa = Deployment("ppa-1.3.2", "ppa.war", enabled=True)


class VerifyDeploymentsTests(unittest.TestCase):
    @patch("verify_deployments.common.read_archive_files",
           MagicMock(return_value=[]))
    @patch("verify_deployments.common.fetch_enabled_deployments",
           MagicMock(return_value=[deployment_app, deployment_ppa]))
    @patch("verify_deployments.common.initialize_controller", MagicMock())
    @patch("verify_deployments.os.path.abspath",
           MagicMock(return_value="/tmp/deployment"))
    def test_verify_emptyFolder_shouldReturn2AndHaveErrorMessage(self):
        args = MagicMock()
        result = verify_deployments.verify(args)
        output = result[0]
        return_code = result[1]

        self.assertEquals(return_code, 2)
        self.assertEquals(output, "Deployment directory is empty!")

    @patch("verify_deployments.common.read_archive_files",
           MagicMock(return_value=[deployment_app, deployment_ppa]))
    @patch("verify_deployments.common.fetch_enabled_deployments",
           MagicMock(return_value=[deployment_app]))
    @patch("verify_deployments.common.initialize_controller", MagicMock())
    @patch("verify_deployments.os.path.abspath",
           MagicMock(return_value="/tmp/deployment"))
    def test_verify_MissingDeploymentInServer_Return1AndHaveErrorMessage(self):
        args = MagicMock()
        result = verify_deployments.verify(args)
        output = result[0]
        return_code = result[1]
        stderr = result[2]

        self.assertEquals(return_code, 1)
        self.assertEquals(output, "ERROR: some modules were not deployed:\n")
        self.assertEquals(stderr, "ppa-1.3.2")

    @patch("verify_deployments.common.read_archive_files",
           MagicMock(return_value=[deployment_app]))
    @patch("verify_deployments.common.fetch_enabled_deployments",
           MagicMock(return_value=[deployment_app, deployment_ppa]))
    @patch("verify_deployments.common.initialize_controller", MagicMock())
    @patch("verify_deployments.os.path.abspath",
           MagicMock(return_value="/tmp/deployment"))
    def test_verify_emptyFolder_shouldReturn0AndHaveOKMessage(self):
        args = MagicMock()
        result = verify_deployments.verify(args)
        output = result[0]
        return_code = result[1]

        self.assertEquals(return_code, 0)
        self.assertEquals(output, "OK!")

if __name__ == "__main__":
    unittest.main()
