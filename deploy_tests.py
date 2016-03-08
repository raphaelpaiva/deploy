#!/usr/bin/python
import os

import unittest
import cli_output
import deploy


class TestDeploy(unittest.TestCase):

  def test_is_war__warfile_shouldReturnTrue(self):
      self.assertTrue(deploy.is_war('aaa.war'))
  def test_is_war__notWarFle_shouldReturnFalse(self):
      self.assertFalse(deploy.is_war('aaa'))

  def test_prepare_deploy_statement(self):
      path = os.path.join("/tmp", "deploy") + os.path.sep + "archive.war"
      actual_statement = cli_output.prepare_deploy_statement(path)
      expected_statement = 'deploy ' + path + ' --runtime-name=archive.war --name=archive-notag'
      self.assertEqual(actual_statement, expected_statement)

  def test_extract_tag_fullPath_shouldReturnLastDir(self):
      path = os.path.join("/tmp", "deploy", "5.0.0-alfa-24")
      expected_tag="5.0.0-alfa-24"
      self.assertEqual(deploy.extract_tag(path), expected_tag)
  def test_extract_tag_fullPathTrailingSlash_shouldReturnLastDir(self   ):
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

if __name__ == '__main__':
    unittest.main()
