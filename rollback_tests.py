from mock import MagicMock
from mock import ANY
from mock import mock_open
import unittest
import rollback
import os
from jbosscli.jbosscli import Deployment

class TestRollback(unittest.TestCase):
  def test_get_latest_rollback_file_validFileList_shouldReturnLatestTimeStamp(self):
      files = "rollback-info_1465588121140 rollback-info_1465588289292 rollback-info_1465588416224 rollback-info_1465590073564".split()

      expected_latest = "rollback-info_1465590073564"
      actual_latest = rollback.get_latest_rollback_file(files)

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

  def test_persist_rollback_info_emptyDeploymentList_shouldNotWriteFile(self):
      deployments = []
      rollback.write_to_file = MagicMock()

      rollback.persist_rollback_info(deployments)

      rollback.write_to_file.assert_not_called()

  def test_persist_rollback_info_NullDeploymentList_shouldNotWriteFile(self):
      deployments = None
      rollback.write_to_file = MagicMock()

      rollback.persist_rollback_info(deployments)

      rollback.write_to_file.assert_not_called()

  def test_persist_rollback_info_oneDeployment_shouldWriteFile(self):
      deployments = [Deployment("abc", "abc.war", server_group="group")]
      rollback.write_to_file = MagicMock()

      rollback.persist_rollback_info(deployments)

      rollback.write_to_file.assert_called_with(ANY, "abc abc.war group\n")

  def test_persist_rollback_info_twoDeployments_shouldWriteFile(self):
      deployments = [Deployment("abc", "abc.war", server_group="group"), Deployment("cba-v5.2.0", "cba.war", server_group="pourg")]
      rollback.write_to_file = MagicMock()

      rollback.persist_rollback_info(deployments)

      rollback.write_to_file.assert_called_with(ANY, "abc abc.war group\ncba-v5.2.0 cba.war pourg\n")

  def test_list_rollback_files_valid_directory_shouldCallGlob(self):
      rollback.glob.glob = MagicMock()

      rollback.list_rollback_files("/home/directory")

      rollback.glob.glob.assert_called_with("/home/directory" + os.sep + "rollback-info_*")

  def test_read_rollback_info(self):
      rollback.read_from_file = MagicMock(return_value=["abc abc.war group"])
      rollback.get_latest_rollback_file = MagicMock(return_value="rollback-info_test")

      archives = []
      archives = rollback.read_rollback_info()

      rollback.read_from_file.assert_called_with( os.path.dirname(os.path.abspath(__file__)) + os.sep + "rollback-info_test")
      self.assertEqual(len(archives), 1)

      archive = archives[0]
      self.assertEqual(archive.name, "abc")
      self.assertEqual(archive.runtime_name, "abc.war")
      self.assertEqual(archive.server_group, "group")

if __name__ == '__main__':
    unittest.main()
