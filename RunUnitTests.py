#!/usr/bin/env python

import argparse
import sys
import Utils as utils
import os
import re
import subprocess
import tempfile
import shlex


def main():
    target, configuration = command_line_controller()
    run_unit_tests(target, configuration)

def run_unit_tests(target, configuration):

    os.system("killall \"iPhone Simulator\"")

    launcher_path = "/usr/local/bin/ios-sim"
    arg_dict = {'target' : target,
            'configuration' : configuration,
            'sdk' : 'iphonesimulator' }
    build_command = utils.create_build_command(['clean', 'build'], **arg_dict)

    ret_val = os.system(build_command)

    if ret_val == 0:

        regx = re.compile(".*xcodeproj$")
        projfolder = filter(regx.match, os.listdir("."))

        if len(projfolder) == 1:
            pbxfile = "/".join([projfolder[0], "project.pbxproj"])
        else:
            raise Exception("No pbx file found in %s" % projfolder)

        conf_dict = utils.build_settings_dict(pbxfile, target, configuration)

        e = conf_dict

        test_bundle_path = "%s/build/%s-%s/%s.%s" % (os.getcwd(), arg_dict['configuration'], arg_dict['sdk'], arg_dict['target'], e['WRAPPER_EXTENSION'])

        r = {}
        r['DYLD_INSERT_LIBRARIES'] = "/../../Library/PrivateFrameworks/IDEBundleInjection.framework/IDEBundleInjection"
        r['XCInjectBundle'] = test_bundle_path
        r['XCInjectBundleInto'] = e['TEST_HOST']

        env_args = "".join(["--setenv %s=\"%s\" " % (x, r[x]) for x in r.keys()])
        app_test_host = os.path.dirname(e['TEST_HOST'])
        test_command = "%s launch \"%s\" %s --args -SenTest All %s" % (launcher_path, app_test_host, env_args, test_bundle_path)
        output_descriptor, temp_output_path = tempfile.mkstemp()


        split_command = shlex.split(str(test_command))
        temp_file = open(temp_output_path, "w") 
        test_results = subprocess.Popen(split_command, stdout=temp_file, stderr=subprocess.STDOUT)
        test_results.wait()
        test_results_text = open(temp_output_path, "r")
        subprocess.check_output("%s/ocunit2junit.rb" % os.environ['COMMON_SCRIPTS_HOME'], stdin=test_results_text)

def command_line_controller():
 
    parser = argparse.ArgumentParser(description="Runs a unit test target in an XCode Project")

    parser.add_argument("--configuration", '-c', dest="configuration", help="The configuration to build the target with.")
    parser.add_argument("--target", '-t', dest="target", help="The target to build the project for.")

    arguments = parser.parse_args()

    return arguments.target, arguments.configuration

if __name__ == '__main__':
    main()

