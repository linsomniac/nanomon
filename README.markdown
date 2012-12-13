nanomon: Extremely Lightweight Monitoring System
================================================

Overview
--------

nanomon is an extremely small and simple monitoring system meant largely
for reporting on a few systems such as reporting failures on RAID arrays,
ZFS volums, or file-systems don't fill up.  It's meant to be similar to
a simple "check" script that one may write, but with the additional
features:

   - Checks several times, so a transient failure does not result in an alert.
   - Remembers state so that a failure doesn't generate mail with every check.
   - Can check multiple issues from a single instance.

It's meant to be a *much* simpler system than things like OpsView (which we
use at work), Zenoss, or Zabbix, without the learning-curve of nagios
(which most of the others listed above use under the hood).  nanomon was
written after I had spent nearly a week trying to get the other solutions
working on an only slightly unusual environment (CentOS 6, they still only
really support CentOS 5).

nanomon uses "cron" for the scheduling, and is a single program executable.
nanomon runs external programs (as specified in the config file), which can
be simple commands or shell scripts and determines success or failure by
either exit code, string match, or Python function (including regular
expression match).

Examples
--------

Simple example which calls Nagios NRPE scripts (a good source of scripts to
perform various checks, see "yum search nrpe" or "apt-cache search nrpe"
for a list of available packages).

    statusfile('/var/lib/nanomon.status')
    mailto('user@example.com')

    #  this check has a description, otherwise the basename of the
    #  check command is used ("check_zfs.sh" in this example).
    command('/usr/lib/nagios/plugins/check_zfs.sh -p data',
         success = re.compile(r'^OK:').match,
         description = 'ZFS')

    command('/usr/lib/nagios/plugins/check_mdstat.sh',
          success = re.compile(r'^OK:').match)
    command('/usr/lib/nagios/plugins/check_disk -c 10% -p /',
          success = re.compile(r'^DISK OK ').match)
    command('/usr/lib/nagios/plugins/check_disk -c 10% -p /boot',
          success = re.compile(r'^DISK OK ').match)

    #  uncomment the following line to simulate a failure.
    #  this takes 15 runs of nanomon before an alert is sent.
    #command('/bin/false', success = 0)

Installation
------------

The following steps will install nanomon:

   - Copy "nanomon" to some location on the system, such as /usr/local/sbin
   - Create a "/usr/local/etc/nanomon.conf" file.  (This location can be
     changed by editing the top of "nanomon")
   - Add "nanomon" to cron, for example with: `echo '* * * * * root
     /usr/local/sbin/nanomon' >/etc/cron.d/nanomon`

If you would like nanomon to re-alert periodically if a failure persists,
you can set up a cron job to run "nanomon reset", which acts like the
service has recovered (without sending an alert).  So if it is still down,
this would cause another alert to be sent.  However, if the service
recovers within 15 (default) minutes of the reset, no recovery will be
sent.

Running "nanomon --help" will display the help message:

   Usage: nanomon [options] [status|reset]

   A small service checking program, which can run an series of commands,
   check their results, and report when they repeatedly fail, and when
   they recover.

   Options:
     -h, --help            show this help message and exit
     -c FILE, --config=FILE
                           Override the configuration file path

   If called with the "reset" command, the status of all services is
   reset to to the default state.  If called with the "status" command,
   the state file is loaded and either "OK" is printed and nanomon exits
   with 0, or information on the failed services is printed and nanomon
   exits with 1.  If called with no command-line commands, a check of
   all services is run.  Typically this is how it is called from cron.

License
-------

nanomon is licensed under the GPL v3 or later.
