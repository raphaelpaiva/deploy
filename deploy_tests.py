#!/usr/bin/python
import unittest
import deploy

class TestDeploy(unittest.TestCase):

  def test_is_war__warfile_shouldReturnTrue(self):
      self.assertTrue(deploy.is_war('aaa.war'))
  def test_is_war__notWarFle_shouldReturnFalse(self):
      self.assertFalse(deploy.is_war('aaa'))
  def test_prepare_deploy_statement(self):
      actual_statement = deploy.prepare_deploy_statement('/tmp/deploy/archive.war')
      expected_statement = 'deploy /tmp/deploy/archive.war --runtime-name=archive.war --name=archive-tag'
      self.assertEqual(actual_statement, expected_statement)

if __name__ == '__main__':
    unittest.main()
