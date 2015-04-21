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
		for filename in ['test_checker', 'status_1', 'status_2', 'nanomon.status']:
			try:
				os.remove(filename)
			except OSError:
				pass

	def test_Basic(self):
		#  make checker fail
		with open('test_checker', 'w') as fp:
			fp.write('#!/bin/bash\n\nfalse\n')
		os.chmod('test_checker', 0755)

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

		#  Check e-mail subject
		check_command(self, ['python', self.nanomon_path,
				'--config', 'basic_config'],
				output='Subject: DOWN: Service OUTAGE: test_checker')
		check_command(self, ['python', self.nanomon_path,
				'--config', 'basic_config', 'status'],
				output=', DOWN', exit_code=1)

		for i in xrange(15):
			check_command(self, ['python', self.nanomon_path,
					'--config', 'basic_config'])
			check_command(self, ['python', self.nanomon_path,
					'--config', 'basic_config', 'status'],
					output=', DOWN', exit_code=1)

		#  make checker succeed
		with open('test_checker', 'w') as fp:
			fp.write('#!/bin/bash\n\ntrue\n')
		os.chmod('test_checker', 0755)

		#  Check e-mail subject
		check_command(self, ['python', self.nanomon_path,
				'--config', 'basic_config'],
				output='Subject: UP: Service restored: test_checker')
		check_command(self, ['python', self.nanomon_path,
				'--config', 'basic_config', 'status'],
				output='OK', exit_code=0)


	def test_SwapFailure(self):
		#  make checker fail
		with open('test_checker', 'w') as fp:
			fp.write('#!/bin/bash\n\nexit `cat $1`\n')
		os.chmod('test_checker', 0755)

		with open('status_1', 'w') as fp:
			fp.write('0')
		with open('status_2', 'w') as fp:
			fp.write('0')

		check_command(self, ['python', self.nanomon_path,
				'--config', 'swapfailure_config', 'reset'])

		for i in xrange(10):
			check_command(self, ['python', self.nanomon_path,
					'--config', 'swapfailure_config'])
			check_command(self, ['python', self.nanomon_path,
					'--config', 'swapfailure_config', 'status'],
					output='OK', exit_code=0)

        #  make first one fail
		with open('status_1', 'w') as fp:
			fp.write('1')
		with open('status_2', 'w') as fp:
			fp.write('0')

		for i in xrange(5):
			check_command(self, ['python', self.nanomon_path,
					'--config', 'swapfailure_config'])
			check_command(self, ['python', self.nanomon_path,
					'--config', 'swapfailure_config', 'status'],
					output=', UP', exit_code=1)

		#  Check e-mail subject
		check_command(self, ['python', self.nanomon_path,
				'--config', 'swapfailure_config'],
				output='Subject: DOWN: Service OUTAGE: test_checker')
		check_command(self, ['python', self.nanomon_path,
				'--config', 'swapfailure_config', 'status'],
				output=', DOWN', exit_code=1)

        #  make only second one fail
		with open('status_1', 'w') as fp:
			fp.write('0')
		with open('status_2', 'w') as fp:
			fp.write('1')

        #  should receive an up from the first test
		check_command(self, ['python', self.nanomon_path,
				'--config', 'swapfailure_config'],
				output='Subject: UP: Service restored: test_checker')
		check_command(self, ['python', self.nanomon_path,
				'--config', 'swapfailure_config', 'status'],
				output='OK', exit_code=0)

		for i in xrange(5):
			check_command(self, ['python', self.nanomon_path,
					'--config', 'swapfailure_config'])
			check_command(self, ['python', self.nanomon_path,
					'--config', 'swapfailure_config', 'status'],
					output=', UP', exit_code=1)

        #  now should fail for the second one
		check_command(self, ['python', self.nanomon_path,
				'--config', 'swapfailure_config'],
				output='Subject: DOWN: Service OUTAGE: test_checker')
		check_command(self, ['python', self.nanomon_path,
				'--config', 'swapfailure_config', 'status'],
				output=', DOWN', exit_code=1)

		for i in xrange(5):
			check_command(self, ['python', self.nanomon_path,
					'--config', 'swapfailure_config'])
			check_command(self, ['python', self.nanomon_path,
					'--config', 'swapfailure_config', 'status'],
					output=', DOWN', exit_code=1)

		#  make checker succeed
		with open('status_1', 'w') as fp:
			fp.write('0')
		with open('status_2', 'w') as fp:
			fp.write('0')

		#  Check e-mail subject
		check_command(self, ['python', self.nanomon_path,
				'--config', 'swapfailure_config'],
				output='Subject: UP: Service restored: test_checker')
		check_command(self, ['python', self.nanomon_path,
				'--config', 'swapfailure_config', 'status'],
				output='OK', exit_code=0)


unittest.main()
