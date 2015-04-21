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
    proc = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        close_fds=True)
    stdout, stderr = proc.communicate()

    test.assertEqual('', stderr)
    if output:
        test.assertIn(output, stdout)
    test.assertEqual(proc.returncode, exit_code)


class Checker:
    def __init__(self, test, config_file):
        self.test = test
        self.config_file = config_file

    def age_status(self, output=None):
        '''Age the status of the system by running checks.'''
        check_command(self.test, [
            'python', self.test.nanomon_path, '--config', self.config_file],
            output=output)

    def check_status(self, up=False):
        output_str = ', UP' if up is True else ', DOWN'
        check_command(self.test, [
            'python', self.test.nanomon_path, '--config',
            self.config_file, 'status'], output=output_str, exit_code=1)


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
        file_list = ['test_checker', 'status_1', 'status_2', 'nanomon.status']
        for filename in file_list:
            try:
                os.remove(filename)
            except OSError:
                pass

    def test_Basic(self):
        config_file = 'basic_config'
        checker = Checker(self, config_file)

        #  make checker fail
        with open('test_checker', 'w') as fp:
            fp.write('#!/bin/bash\n\nfalse\n')
        os.chmod('test_checker', 0755)

        check_command(
            self, ['python', self.nanomon_path, '--help'],
            'Usage: nanomon')
        check_command(self, [
            'python', self.nanomon_path, '--config', config_file,
            '--help'], 'Usage: nanomon')

        check_command(self, [
            'python', self.nanomon_path, '--config', config_file,
            'reset'])

        for i in xrange(15):
            checker.age_status()
            checker.check_status(up=True)

        #  Check e-mail subject
        checker.age_status(
            output='Subject: DOWN: Service OUTAGE: test_checker')
        check_command(self, [
            'python', self.nanomon_path, '--config', config_file,
            'status'], output=', DOWN', exit_code=1)

        for i in xrange(15):
            checker.age_status()
            checker.check_status(up=False)

        #  make checker succeed
        with open('test_checker', 'w') as fp:
            fp.write('#!/bin/bash\n\ntrue\n')
        os.chmod('test_checker', 0755)

        #  Check e-mail subject
        checker.age_status(
            output='Subject: UP: Service restored: test_checker')
        check_command(self, [
            'python', self.nanomon_path, '--config', config_file,
            'status'], output='OK', exit_code=0)

    def test_SwapFailure(self):
        config_file = 'swapfailure_config'
        checker = Checker(self, config_file)

        def set_status(status_1, status_2):
            with open('status_1', 'w') as fp:
                fp.write('%s' % status_1)
            with open('status_2', 'w') as fp:
                fp.write('%s' % status_2)

        with open('test_checker', 'w') as fp:
            fp.write('#!/bin/bash\n\nexit `cat $1`\n')
        os.chmod('test_checker', 0755)

        set_status(0, 0)

        check_command(self, [
            'python', self.nanomon_path, '--config', config_file,
            'reset'])

        for i in xrange(10):
            check_command(self, [
                'python', self.nanomon_path, '--config', config_file])
            check_command(self, [
                'python', self.nanomon_path, '--config', config_file,
                'status'], output='OK', exit_code=0)

        set_status(1, 0)

        for i in xrange(5):
            checker.age_status()
            checker.check_status(up=True)

        #  Check e-mail subject
        checker.age_status(
            output='Subject: DOWN: Service OUTAGE: test_checker')
        check_command(self, [
            'python', self.nanomon_path, '--config', config_file,
            'status'], output=', DOWN', exit_code=1)

        set_status(0, 1)

        #  should receive an up from the first test
        #@@@ This currently is failing due to an enhancement request
        checker.age_status(
            output='Subject: UP: Service restored: test_checker')
        check_command(self, [
            'python', self.nanomon_path, '--config', config_file,
            'status'], output='OK', exit_code=0)

        for i in xrange(5):
            checker.age_status()
            checker.check_status(up=True)

        #  now should fail for the second one
        checker.age_status(
            output='Subject: DOWN: Service OUTAGE: test_checker')
        check_command(self, [
            'python', self.nanomon_path, '--config', config_file,
            'status'], output=', DOWN', exit_code=1)

        for i in xrange(5):
            checker.age_status()
            checker.check_status(up=False)

        #  make checker succeed
        set_status(0, 0)

        #  Check e-mail subject
        checker.age_status(
            output='Subject: UP: Service restored: test_checker')
        check_command(self, [
            'python', self.nanomon_path, '--config', config_file,
            'status'], output='OK', exit_code=0)


unittest.main()
