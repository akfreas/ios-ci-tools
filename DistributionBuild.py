#!/usr/bin/python

from datetime import datetime, timedelta
from tempfile import mkstemp
from random import randrange
import argparse
import os, sys
import re
import Utils as utils
import PlistUtility as plutil
import biplist

def main():
    arg_dict = command_line_controller()

    print os.system("xcodebuild -showsdks")
    print os.system("whereis xcodebuild")
    print os.listdir("/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/SDKs")


    if arg_dict['scheme'] == None or arg_dict['configuration'] == None:
        raise Exception("You must specify at least a scheme and a configuration to build through the command line or by setting the DIST_SCHEME and DIST_CONFIGURATION environment variables")

    if arg_dict['sdk'] == None:
        sdk = "iphoneos6.0"

    regx = re.compile(".*xcodeproj$")

    projfolder = filter(regx.match, os.listdir("."))

    if len(projfolder) == 1:
        pbxfile = "/".join([projfolder[0], "project.pbxproj"])
        info_plist_path = utils.get_plist_path_from_pbxfile(pbxfile, arg_dict['scheme'], arg_dict['configuration'])

        plist_dict = biplist.readPlist(info_plist_path)
        resource_root = os.path.dirname(os.path.abspath(info_plist_path))

        print "xxxxXXXXxxx"
        print plist_dict
        print resource_root


        if arg_dict['version'] != None and arg_dict['version'] != "":
            version = plutil.increment_development_version(info_plist_path, arg_dict['version'])
            version = plutil.increment_release_version(info_plist_path, arg_dict['version'])
        if arg_dict['bundle_id'] != None and arg_dict['version'] != "":
            plutil.change_bundle_id(info_plist_path, arg_dict['bundle_id'])
        del(arg_dict['bundle_id'])

        def brand_icons(icon_list):
            try:
                for icon in icon_list:
                    icon_path = "%s/%s" % (resource_root, icon)
                    print icon_path
                    utils.brand_icon(icon_path, version, os.getenv("GIT_BRANCH"))
            except:
                pass


        if "CFBundleIconFiles" in plist_dict.keys():
            brand_icons(plist_dict['CFBundleIconFiles'])

        if "CFBundleIcons" in plist_dict.keys():
            primary_icons = plist_dict['CFBundleIcons']['CFBundlePrimaryIcon']['CFBundleIconFiles']
            brand_icons(primary_icons)



    if (arg_dict['xcconfig']):

        current_date = datetime.now() 
        expiry_date = current_date + timedelta(30)

        template_vars = {'kill_day' : expiry_date.month, 'kill_year' : expiry_date.year, 'kill_month' : expiry_date.month }
        temp_config_path = utils.format_file_with_vars(arg_dict['xcconfig'], template_vars)
        arg_dict['xcconfig'] = temp_config_path

    if "version" in arg_dict.keys():
        del(arg_dict['version'])

    command_append_string = ""

    if arg_dict['additional_vars'] != None and arg_dict['additional_vars'] != "":
        command_append_string = arg_dict['additional_vars']

    if "additional_vars" in arg_dict.keys():
        del(arg_dict['additional_vars'])
        



    build_command = utils.create_build_command(['clean', 'build'], **arg_dict)
    build_command += " " + command_append_string
    print build_command
      
    retval = os.system(build_command)
    if retval != 0:
        sys.exit(-1)


def command_line_controller():

    parser = argparse.ArgumentParser(description="Builds the release version of an Xcode project for distribution.")

    parser.add_argument("--version", '-v', dest="version", help="The version number of this release version (bundle version).")
    parser.add_argument("--bundle_id", '-b', dest="bundle_id", help="Desired bundle id of this version.")
    parser.add_argument("--configuration", '-c', dest="configuration", help="The configuration to build the target with.")
    parser.add_argument("--scheme", '-t', dest="scheme", help="The scheme to use to build the project.")
    parser.add_argument("--sdk", '-s', dest="sdk", help="SDK to build the target with.")
    parser.add_argument("--xcconfig", '-x', dest="xcconfig", help="xcconfig file to use for building target.")
    parser.add_argument("--additional-build-vars", '-a', dest="additional_vars", help="Additional variables to build project with.", required=False)

    arguments = parser.parse_args()

    arg_dict = {}

    if(arguments.version == None):
        arg_dict['version'] = os.getenv("DIST_VERSION")
    else:
        arg_dict['version'] = arguments.version

    arg_dict['additional_vars'] = arguments.additional_vars or os.getenv("ADDITIONAL_VARS")

    arg_dict['bundle_id'] = arguments.bundle_id or os.getenv("DIST_BUNDLE_ID")
    arg_dict['scheme'] = arguments.scheme or os.getenv("DIST_SCHEME")
    arg_dict['configuration'] = arguments.configuration or os.getenv("DIST_CONFIGURATION")
    arg_dict['sdk'] = arguments.sdk or os.getenv("DIST_SDK")
    arg_dict['xcconfig'] = arguments.xcconfig or os.getenv("DIST_XCCONFIG")

    return arg_dict

if __name__ == '__main__':
    main()
