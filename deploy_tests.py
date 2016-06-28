#!/usr/bin/python
import os

import unittest
import cli_output
import deploy
import jbosscli.jbosscli as jbosscli

from mock import MagicMock

class TestDeploy(unittest.TestCase):

  def test_is_archive__warfile_shouldReturnTrue(self):
      self.assertTrue(deploy.is_archive('aaa.war'))
  def test_is_archive__notWarFle_shouldReturnFalse(self):
      self.assertFalse(deploy.is_archive('aaa'))

  def test_is_archive_file_jarFile_shouldReturnTrue(self):
      self.assertTrue(deploy.is_archive('aaa.jar'))

  def test_prepare_deploy_statement_warfile(self):
      path = os.path.join("/tmp", "deploy") + os.path.sep + "archive.war"
      deployment = jbosscli.Deployment("archive-notag", "archive.war", path=path)

      actual_statement = cli_output.prepare_deploy_statement(deployment)
      expected_statement = 'deploy ' + path + ' --runtime-name=archive.war --name=archive-notag'

      self.assertEqual(actual_statement, expected_statement)

  def test_prepare_deploy_statement_jarfile(self):
      path = os.path.join("/tmp", "deploy") + os.path.sep + "archive.jar"
      deployment = jbosscli.Deployment("archive-notag", "archive.jar", path=path)

      actual_statement = cli_output.prepare_deploy_statement(deployment)
      expected_statement = 'deploy ' + path + ' --runtime-name=archive.jar --name=archive-notag'

      self.assertEqual(actual_statement, expected_statement)


  def test_prepare_undeploy_statement_warfile(self):
      deployment = jbosscli.Deployment("archive-tag", "archive.war")
      self.assertEqual(cli_output.prepare_undeploy_statement(deployment), "undeploy archive-tag --keep-content")

  def test_prepare_undeploy_statement_warfile_withUndeployTag(self):
      deployment = jbosscli.Deployment("archive-tag", "archive.war")
      self.assertEqual(cli_output.prepare_undeploy_statement(deployment, "undeploy_tag"), "undeploy archive-undeploy_tag --keep-content")

  def test_prepare_undeploy_statement_jarfile_withUndeployTag(self):
      deployment = jbosscli.Deployment("archive-tag", "archive.jar")
      self.assertEqual(cli_output.prepare_undeploy_statement(deployment, "undeploy_tag"), "undeploy archive-undeploy_tag --keep-content")


  def test_prepare_undeploy_statement_jarfile(self):
      deployment = jbosscli.Deployment("archive-tag", "archive.jar")
      self.assertEqual(cli_output.prepare_undeploy_statement(deployment), "undeploy archive-tag --keep-content")

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

if __name__ == '__main__':
    unittest.main()
