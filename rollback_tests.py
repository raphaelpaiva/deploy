import os
import tempfile
from mock import MagicMock
from mock import ANY
from mock import mock_open
from mock import patch
import unittest
import rollback
from jbosscli import Deployment

class TestRollback(unittest.TestCase):
  def test_get_latest_rollback_file_validFileList_shouldReturnLatestTimeStamp(self):
      files = "rollback-info_1465588121140 rollback-info_1465588289292 rollback-info_1465588416224 rollback-info_1465590073564".split()

      expected_latest = "rollback-info_1465590073564"
      actual_latest = rollback.get_latest_rollback_file(files)

      self.assertEqual(actual_latest, expected_latest)

  def test_get_latest_rollback_file_validFileList_rollbackfilesuffix_shouldReturnLatestTimeStamp(self):
      files = "rollback-info-suffix_1465588121140 rollback-info-suffix_1465588289292 rollback-info-suffix_1465588416224".split()

      expected_latest = "rollback-info-suffix_1465588416224"
      actual_latest = rollback.get_latest_rollback_file(files, "rollback-info-suffix_")

      self.assertEqual(actual_latest, expected_latest)

  def test_get_latest_rollback_file_emptyFileList_shouldReturnNone(self):
      files = []

      expected_latest = None
      actual_latest = rollback.get_latest_rollback_file(files)

      self.assertEqual(actual_latest, expected_latest)

  def test_get_latest_rollback_file_NullFileList_shouldReturnNone(self):
      files = None

      expected_latest = None
      actual_latest = rollback.get_latest_rollback_file(files)

      self.assertEqual(actual_latest, expected_latest)

  @patch("rollback.glob.glob", MagicMock(return_value="rollback-info-suffix_1465588121140 rollback-info-suffix_1465588289292 rollback-info-suffix_1465588416224".split()))
  def test_get_rollback_file_rollbackFileSuffix_shouldReturnLatestFile(self):
      dir = tempfile.gettempdir()
      rollback_filename_template = "rollback-info-suffix_"
      expected_rollback_filename = dir + os.sep + "rollback-info-suffix_1465588416224"

      rollback_file = rollback.get_rollback_file(dir, rollback_filename_template)

      rollback.glob.glob.assert_called_with(dir + os.sep + rollback_filename_template + "*")
      self.assertEqual(rollback_file, expected_rollback_filename)

  @patch("rollback.common.write_to_file", MagicMock())
  def test_persist_rollback_info_emptyDeploymentList_shouldNotWriteFile(self):
      deployments = []

      rollback.persist_rollback_info(deployments)

      rollback.common.write_to_file.assert_not_called()

  @patch("rollback.common.write_to_file", MagicMock())
  def test_persist_rollback_info_NullDeploymentList_shouldNotWriteFile(self):
      deployments = None

      rollback.persist_rollback_info(deployments)

      rollback.common.write_to_file.assert_not_called()

  @patch("rollback.common.write_to_file", MagicMock())
  def test_persist_rollback_info_oneDeployment_shouldWriteFile(self):
      deployments = [Deployment("abc", "abc.war", server_group="group")]

      rollback.persist_rollback_info(deployments)

      rollback.common.write_to_file.assert_called_with(ANY, "abc abc.war group\n")

  @patch("rollback.common.write_to_file", MagicMock())
  def test_persist_rollback_info_twoDeployments_shouldWriteFile(self):
      deployments = [Deployment("abc", "abc.war", server_group="group"), Deployment("cba-v5.2.0", "cba.war", server_group="pourg")]

      rollback.persist_rollback_info(deployments)

      rollback.common.write_to_file.assert_called_with(ANY, "abc abc.war group\ncba-v5.2.0 cba.war pourg\n")

  @patch("rollback.glob.glob", MagicMock())
  def test_list_rollback_files_valid_directory_shouldCallGlob(self):

      rollback.list_rollback_files("/home/directory")

      rollback.glob.glob.assert_called_with("/home/directory" + os.sep + "rollback-info_*")

  @patch("rollback.glob.glob", MagicMock())
  def test_list_rollback_files_valid_directory_specifiedRollbackSuffix_shouldCallGlobWithSuffix(self):

      rollback.list_rollback_files("/home/directory", "rollback-info-suffix_")

      rollback.glob.glob.assert_called_with("/home/directory" + os.sep + "rollback-info-suffix_*")

  @patch("rollback.common.read_from_file", MagicMock(return_value=["abc abc.war group"]))
  def test_read_rollback_info(self):
      rollback_file_path = os.path.dirname(os.path.abspath(__file__)) + os.sep + "rollback-info_test"
      archives = []
      archives = rollback.read_rollback_info(rollback_file_path)

      rollback.common.read_from_file.assert_called_with(rollback_file_path)
      self.assertEqual(len(archives), 1)

      archive = archives[0]
      self.assertEqual(archive.name, "abc")
      self.assertEqual(archive.runtime_name, "abc.war")
      self.assertEqual(archive.server_group, "group")

  @patch("rollback.common.read_from_file", MagicMock(return_value=["abc-v1.2.3 abc.war group"]))
  @patch("rollback.get_latest_rollback_file", MagicMock(return_value="rollback-info_test"))
  @patch("rollback.common.fetch_enabled_deployments", MagicMock(return_value=[Deployment("abc-v1.0.0", "abc.war", server_group="group")]))
  @patch("rollback.common.initialize_controller", MagicMock())
  def test_generate_rollback_script(self):
      expected_script="""\
# Using rollback information from {0}rollback-info_test

undeploy abc-v1.0.0 --keep-content --all-relevant-server-groups

deploy  --runtime-name=abc.war --name=abc-v1.2.3 --server-groups=group\
""".format(os.path.dirname(os.path.abspath(__file__)) + os.sep)

      args = MagicMock()
      args.args.rollback_info_file_suffix = ""

      script = rollback.generate_rollback_script(args)
      self.assertEqual(script, expected_script)

  def test_get_rollback_file_emptyDirectory_shouldReturnNone(self):
      rollback_file = rollback.get_rollback_file(tempfile.gettempdir())
      self.assertIsNone(rollback_file)

  @patch("rollback.common.read_from_file", MagicMock(return_value=["abc-v1.2.3 abc.war group"]))
  @patch("rollback.common.fetch_enabled_deployments", MagicMock(return_value=[Deployment("abc-v1.0.0", "abc.war", server_group="group")]))
  @patch("rollback.common.initialize_controller", MagicMock())
  @patch("rollback.glob.glob", MagicMock(return_value="rollback-info-suffix_1465588121140 rollback-info-suffix_1465588289292 rollback-info-suffix_1465588416224".split()))
  def test_generate_rollback_script_rollbackfile_suffix(self):
      expected_script="""\
# Using rollback information from {0}rollback-info-suffix_1465588416224

undeploy abc-v1.0.0 --keep-content --all-relevant-server-groups

deploy  --runtime-name=abc.war --name=abc-v1.2.3 --server-groups=group\
""".format(os.path.dirname(os.path.abspath(__file__)) + os.sep)

      args = MagicMock()
      args.rollback_info_file_suffix = "suffix"

      script = rollback.generate_rollback_script(args)

      rollback.glob.glob.assert_called_with(os.path.dirname(os.path.abspath(__file__)) + os.sep + "rollback-info-suffix_*")
      self.assertEqual(script, expected_script)

  def test_get_rollback_file_emptyDirectory_shouldReturnNone(self):
      rollback_file = rollback.get_rollback_file(tempfile.gettempdir())
      self.assertIsNone(rollback_file)


  @patch("rollback.common.initialize_controller", MagicMock(return_value=None))
  def test_generate_rollback_script_NoneController_shouldReturnErrorMessage(self):
    args = MagicMock()
    args.controller = "controller:port"
    expected_script = "# Cannot initialize the controller controller:port. Rollback will not occour."

    script = rollback.generate_rollback_script(args)

    self.assertEqual(script, expected_script)

  @patch("rollback.common.initialize_controller", MagicMock())
  @patch("rollback.get_rollback_file", MagicMock(return_value=None))
  def test_generate_rollback_script_NoRollbackFile_shouldReturnErrorMessage(self):
      current_dir = os.path.dirname(os.path.abspath(__file__))

      args = MagicMock()
      args.controller = "controller:port"
      expected_script = "# Cannot find rollback-info file in {0}. Rollback will not occour.".format(current_dir)

      script = rollback.generate_rollback_script(args)

      self.assertEqual(script, expected_script)

  def test_generate_rollback_filename_template_emptySuffix_shouldReturnDefaultTemplate(self):
      expected_rollback_filename_template = "rollback-info_"
      rollback_filename_template = rollback.generate_rollback_filename_template("")

      self.assertEqual(rollback_filename_template, expected_rollback_filename_template)

  def test_generate_rollback_filename_template_providedSuffix_shouldReturnSuffixedTemplate(self):
      expected_rollback_filename_template = "rollback-info-suffix-ix_"
      rollback_filename_template = rollback.generate_rollback_filename_template("suffix-ix")

      self.assertEqual(rollback_filename_template, expected_rollback_filename_template)

if __name__ == '__main__':
    unittest.main()
