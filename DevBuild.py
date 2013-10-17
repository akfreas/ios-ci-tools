#!/usr/bin/env python

import argparse
import sys
import Utils as utils
import os
import re


def main():

    target, config = command_line_args()

    arg_dict = {
            'configuration' : config,
            'target' : target,
            'sdk' : 'iphonesimulator'
            }

    build_command = utils.create_build_command(['clean', 'build'], **arg_dict)
    print build_command

    ret_val = os.system(build_command)

    if ret_val != 0:
        sys.exit(ret_val)


def command_line_args():
 
    parser = argparse.ArgumentParser(description="Builds a target in an XCode Project")

    parser.add_argument("--configuration", '-c', dest="configuration", help="The configuration to build the target with.")
    parser.add_argument("--target", '-t', dest="target", help="The target to build the project for.")

    arguments = parser.parse_args()

    return arguments.target, arguments.configuration

if __name__ == '__main__':
    main()

