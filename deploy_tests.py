#!/usr/bin/python
import os

import unittest
import cli_output
import deploy
import jbosscli.jbosscli as jbosscli
from jbosscli.jbosscli import Deployment

from mock import MagicMock
from mock import patch

current_dir = os.path.dirname(os.path.abspath(__file__))

class TestDeploy(unittest.TestCase):

  def test_is_archive__warfile_shouldReturnTrue(self):
      self.assertTrue(deploy.is_archive('aaa.war'))
  def test_is_archive__notWarFle_shouldReturnFalse(self):
      self.assertFalse(deploy.is_archive('aaa'))

  def test_is_archive_file_jarFile_shouldReturnTrue(self):
      self.assertTrue(deploy.is_archive('aaa.jar'))

  def test_extract_tag_fullPath_shouldReturnLastDir(self):
      path = os.path.join("/tmp", "deploy", "5.0.0-alfa-24")
      expected_tag="5.0.0-alfa-24"
      self.assertEqual(deploy.extract_tag(path), expected_tag)
  def test_extract_tag_fullPathTrailingSlash_shouldReturnLastDir(self):
      path = os.path.join("/tmp", "deploy", "5.0.0-alfa-24") + os.path.sep
      expected_tag="5.0.0-alfa-24"
      self.assertEqual(deploy.extract_tag(path), expected_tag)
  def test_extract_tag_onlyDirName_shouldReturnDirName(self):
      path = "5.0.0-alfa-24"
      expected_tag="5.0.0-alfa-24"
      self.assertEqual(deploy.extract_tag(path), expected_tag)
  def test_extract_tag_onlyDirNameWithTrailingSlash_shouldReturnDirName(self):
      path = "5.0.0-alfa-24" + os.path.sep
      expected_tag="5.0.0-alfa-24"
      self.assertEqual(deploy.extract_tag(path), expected_tag)

  def test_read_archive_files(self):
      files = ["aaa.war", "bbb.war", "ccc.txt", "ddd.jar"]
      tag = "5.0.0.1"
      path = "/tmp/deploy/" + tag
      os.listdir = MagicMock(return_value=files)

      deployments = deploy.read_archive_files(path, tag)

      self.assertEqual(len(deployments), 3)
      self.assertEqual(deployments[0].name, "aaa-5.0.0.1")
      self.assertEqual(deployments[0].runtime_name, "aaa.war")

      self.assertEqual(deployments[1].name, "bbb-5.0.0.1")
      self.assertEqual(deployments[1].runtime_name, "bbb.war")

      self.assertEqual(deployments[2].name, "ddd-5.0.0.1")
      self.assertEqual(deployments[2].runtime_name, "ddd.jar")

  def test_generate_deploy_script_emptyParams_shouldReturnEmptyString(self):
      expected_script = ""
      args = MagicMock()

      script = deploy.generate_undeploy_script(args)

      self.assertEqual(script, expected_script)

  def test_generate_deploy_script_skipUndeployTrue_shouldReturnEmptyString(self):
      expected_script = ""
      args = MagicMock()
      args.skip_undeploy = True

      script = deploy.generate_undeploy_script(args)

      self.assertEqual(script, expected_script)

  def test_generate_deploy_script_undeployPattern_shouldReturnUndeployString(self):
      expected_script = "undeploy --name=system-* --keep-content"
      args = MagicMock()
      args.undeploy_pattern = "system-*"
      args.skip_undeploy = False

      script = deploy.generate_undeploy_script(args)

      self.assertEqual(script, expected_script)

  def test_generate_deploy_script_withArchives_shouldReturnUndeployString(self):
      expected_script = "\nundeploy system-v1.2.3 --keep-content"
      args = MagicMock()
      args.skip_undeploy = False
      args.undeploy_pattern = None
      args.undeploy_tag = None

      archives = [Deployment("system-v1.2.3", "system.war")]

      script = deploy.generate_undeploy_script(args, archives)

      self.assertEqual(script, expected_script)

# -- "Acceptance" Tests:

  @patch("deploy.common.fetch_enabled_deployments", MagicMock(return_value=[Deployment("abc-v1.0.0", "abc.war", server_group="group")]))
  @patch("deploy.common.read_from_file", MagicMock(return_value=["abc.war=group"]))
  @patch("os.path.isfile", MagicMock(return_value=True))
  @patch("deploy.rollback.persist_rollback_info", MagicMock(return_value=current_dir + os.sep + "rollback-info_test"))
  @patch("deploy.read_archive_files", MagicMock(return_value=[Deployment("abc-v1.2.3", "abc.war", path=current_dir + os.sep + "v1.2.3" + os.sep + "abc.war")]))
  def test_generate_deploy_script_receiving_data_from_controller(self):
      expected_script="""\
# Rollback information saved in {0}rollback-info_test

undeploy abc-v1.0.0 --keep-content --all-relevant-server-groups

deploy {1} --runtime-name=abc.war --name=abc-v1.2.3 --server-groups=group\
""".format(current_dir + os.sep,
           current_dir + os.sep + "v1.2.3" + os.sep + "abc.war")
      args = MagicMock()
      args.path = current_dir + os.sep + "v1.2.3"
      args.undeploy_pattern = None
      args.undeploy_tag = None

      mock_controller = MagicMock()
      mock_controller.domain = True
      deploy.common.initialize_controller = MagicMock(return_value=mock_controller)

      script = deploy.generate_deploy_script(args)

      self.assertEqual(script, expected_script)

  @patch("deploy.read_archive_files", MagicMock(return_value=[Deployment("system-v1.2.3", "system.war", path=current_dir + os.sep + "v1.2.3" + os.sep + "system.war")]))
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

      deploy.common.initialize_controller = MagicMock(return_value=None)

      script = deploy.generate_deploy_script(args)

      self.assertEqual(script, expected_script)

if __name__ == '__main__':
    unittest.main()
