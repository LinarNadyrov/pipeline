# -*- coding: utf-8 -*-
#!/usr/bin/python

import jenkins
import argparse

parser = argparse.ArgumentParser(description='command line options')
parser.add_argument("-lu", "--ldap_user", default=None, type=str, help="LDAP User")
parser.add_argument("-lp", "--ldap_password", default=None, type=str, help="LDAP PW")
parser.add_argument("-jl", "--jenkinslist", default='default-jenkins', type=str)
args = parser.parse_args()

jenkins_name_list = [str(item) for item in args.jenkinslist.split(',')]

JENKINS_URL = 'http'
JENKINS_DOMAIN = 'jenkins'

JENKINS_LDAP_USER = args.ldap_user
JENKINS_LDAP_PW = args.ldap_password

for data in jenkins_name_list: 
	JENKINS_NAME = data
	JENKINS_ADDR = JENKINS_URL + '://' + JENKINS_DOMAIN + '/' + JENKINS_NAME + '/'
	try:
		server = jenkins.Jenkins(JENKINS_ADDR, username=JENKINS_LDAP_USER, password=JENKINS_LDAP_PW)
		user = server.get_whoami()
		version = server.get_version()
		print(' Jenkins =',JENKINS_ADDR, '- works', '\n', 'Jenkins version =', version, '\n', 'Connected using this user =', user['fullName'], '\n')
	except jenkins.NotFoundException:
		print(' There is no such Jenkins. Requested -', JENKINS_ADDR, '\n')
	except jenkins.BadHTTPException: 
		print(' Jenkins exists but does not work. His address -', JENKINS_ADDR, '\n')
	except jenkins.JenkinsException: 
		print(' Jenkins exists, work. His address -', JENKINS_ADDR, '\n', 'Failed to connect to Jenkins with user -', JENKINS_LDAP_USER, '\n')
