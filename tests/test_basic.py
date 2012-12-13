#!/usr/bin/env python
#
#  Basic tests of nanomon
#
#===============
#  This is based on a skeleton test file, more information at:
#
#     https://github.com/linsomniac/python-unittest-skeleton

import unittest
import os
import subprocess


def check_command(test, command, output=None, exit_code=0):
	proc = subprocess.Popen(command, stdout=subprocess.PIPE,
			stderr=subprocess.PIPE, close_fds=True)
	stdout, stderr = proc.communicate()

	test.assertEqual('', stderr)
	if output:
		test.assertIn(output, stdout)
	test.assertEqual(proc.returncode, exit_code)


class test_Basic(unittest.TestCase):
	@classmethod
	def setUp(self):
		if os.path.exists('nanomon'):
			self.nanomon_path = './nanomon'
		elif os.path.exists('../nanomon'):
			self.nanomon_path = '../nanomon'
		else:
			raise ValueError('Unable to find nanomon executable')

		try:
			os.remove('nanomon.status')
		except OSError:
			pass

	def tearDown(self):
		try:
			os.remove('nanomon.status')
		except OSError:
			pass

	def test_Basic(self):
		check_command(self, ['python', self.nanomon_path, '--help'],
				'Usage: nanomon')
		check_command(self, ['python', self.nanomon_path,
				'--config', 'basic_config', '--help'], 'Usage: nanomon')

		check_command(self, ['python', self.nanomon_path,
				'--config', 'basic_config', 'reset'])

		for i in xrange(15):
			check_command(self, ['python', self.nanomon_path,
					'--config', 'basic_config'])
			check_command(self, ['python', self.nanomon_path,
					'--config', 'basic_config', 'status'],
					output=', UP', exit_code=1)

		for i in xrange(15):
			check_command(self, ['python', self.nanomon_path,
					'--config', 'basic_config'])
			check_command(self, ['python', self.nanomon_path,
					'--config', 'basic_config', 'status'],
					output=', DOWN', exit_code=1)

unittest.main()
