from mock import MagicMock
import unittest
import rollback

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

  def test_persist_rollback_info_NullDeploymentList_shouldNotWriteFile(self):
      deployments = None
      rollback.write_to_file = MagicMock()

      rollback.persist_rollback_info(deployments)

      rollback.write_to_file.assert_not_called()

if __name__ == '__main__':
    unittest.main()
