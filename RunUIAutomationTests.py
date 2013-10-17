#!/usr/bin/env python

import argparse
import sys
import Utils as utils
import os
import re
import subprocess
import tempfile
import shutil
import shlex


def main():


#    imat_project_dir, target, configuration, test_script, preprocessor_definitions, template_path = command_line_controller()

#    automation = iOSUIAutomation(imat_project_dir, target, configuration, test_script, template_path)
    args = command_line_controller()
    automation = iOSUIAutomation(**args)
    automation.test()


def build_imat_command(project_dir, app_path, suite_path, template_path):

    imat_command = os.environ['IMAT_HOME'] + "/imat"
    imat_command += " -project_dir %s" % project_dir
    imat_command += " run-tests"
    imat_command += " -app %s" % app_path
    imat_command += " -suite %s" % suite_path
    imat_command += " -template %s" % template_path

    return imat_command

class iOSUIAutomation(object):


    def __init__(self, imat_project_path, target, configuration, test_script, template_path, preprocessor_definitions=None):
        self.imat_project_path = imat_project_path
        self.target = target
        self.configuration = configuration
        self.test_script = test_script
        self.template_path = template_path
        if preprocessor_definitions != None and preprocessor_definitions != "":
            self.preprocessor_defs = {k : v for [k, v] in [x.split("=") for x in preprocessor_definitions.split(" ")]}
        else:
            self.preprocessor_defs = None
        self.app_path = None

    def test(self):

        os.system("killall iPhone\ Simulator")
        self.clean()
        self.build_for_automation()
        self.symlink_bootstrap()
        self.run_ui_automation()

    def symlink_bootstrap(self):
        env_dir = "%s/env" % self.imat_project_path
        os.mkdir(env_dir)
        
        js_file = open("%s/env.js" % env_dir, "w")
        js_file.writelines(["#import \"%s/js/bootstrap.js\"" % os.environ['IMAT_HOME']])
        js_file.close()


    def clean(self):
        os.system("git reset --hard")
        os.system("git clean -dfx")
        shutil.rmtree('%s/Library/Application Support/iPhone Simulator/', os.environ['HOME']) 

    def build_for_automation(self):

        arg_dict = {'target' : self.target,
                'configuration' : self.configuration,
                'sdk' : 'iphonesimulator',
                }


        build_command = utils.create_build_command(['build'], self.preprocessor_defs, **arg_dict)

        print build_command
        
        ret_val = os.system(build_command)

        os.environ['IMAT'] = os.environ['IMAT_HOME'] + "/imat"

        if ret_val == 0:

            regx = re.compile(".*xcodeproj$")
            projfolder = filter(regx.match, os.listdir("."))

            if len(projfolder) == 1:
                pbxfile = "/".join([projfolder[0], "project.pbxproj"])
            else:
                raise Exception("No pbx file found in %s" % projfolder)

            conf_dict = utils.build_settings_dict(pbxfile, self.target, self.configuration)
            test_bundle_path = "%s/build/%s-%s/%s.%s" % (os.getcwd(), arg_dict['configuration'], arg_dict['sdk'], arg_dict['target'], conf_dict['WRAPPER_EXTENSION'])


        self.app_path = test_bundle_path

    def run_ui_automation(self):

        imat_command = build_imat_command(self.imat_project_path, self.app_path, self.test_script, self.template_path)
        print imat_command
        os.system(imat_command)





def command_line_controller():
 
    parser = argparse.ArgumentParser(description="Runs a unit test target in an XCode Project")

    parser.add_argument("--configuration", '-c', required=True, dest="configuration", help="The configuration to build the target with.")
    parser.add_argument("--target", '-t',  required=True, dest="target", help="The target to build the project for.")
    parser.add_argument("--preprocessor-definitions", '-d', dest="preprocessor_definitions", help="GCC Preprocessor definitions to build app with.")
    parser.add_argument("--test-script", '-s', required=True, dest="test_script", help="UI automation script path to run against app.")
    parser.add_argument("--template-path", '-p', required=True, dest="template_path", help="Test template path.")
    parser.add_argument("--project-path", '-j', required=True, dest="imat_project_path", help="IMAT Project path.")


    arguments = parser.parse_args()
    packed_args = {k : v for (k, v) in arguments._get_kwargs()}

    print packed_args
    #import pdb; pdb.set_trace()

#    return arguments.target, arguments.configuration, arguments.test_script, arguments.preprocessor_definitions, arguments.template_path
    return packed_args

if __name__ == '__main__':
    main()

