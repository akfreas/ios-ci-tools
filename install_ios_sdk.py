#!/usr/bin/env python

import os
import sys
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from zipfile import ZipFile
from tarfile import TarFile
import tarfile
from tempfile import mktemp, mkdtemp
import argparse

aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_KEY")
s3_bucket_name = "travis-assets"

iphone_sdk_dir = "/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/SDKs"

def is_sdk_installed(sdk_string):

    formatted_sdk = "%s.sdk" % sdk_string
    sdk_list = os.listdir(iphone_sdk_dir)

    format_sdk = lambda x: x.replace(".sdk", "").lower()

    formatted_sdk_list = map(format_sdk, sdk_list)

    if sdk_string not in formatted_sdk_list:
        return False
    else:
        return True
        
def install_sdk(sdk_string):

    conn = S3Connection(aws_access_key_id, aws_secret_access_key)
    bucket = conn.get_bucket(s3_bucket_name)

    formatted_sdk_key = "%s.tar" % sdk_string


    sdk_key = bucket.get_key(formatted_sdk_key)

    temp_filename = mktemp()
    temp_file = open(temp_filename, "w")

    sdk_key.get_contents_to_file(temp_file)#, cb=print_progress, num_cb=10)

    print temp_filename

    temp_file.close()

    zipfile = tarfile.open(temp_filename, mode="r:gz")

    temp_iphone_sdk_dir = mkdtemp()


    zipfile.extractall(iphone_sdk_dir)
    zipfile.close()
    os.unlink(temp_filename)
    

def print_progress(progress, size):
    sys.stdout.write("Downloading.  Progress: %.2f%%   \r" % (progress/size) )
    sys.stdout.flush()

def command_line_controller():

    parser = argparse.ArgumentParser(description="Downloads and installs a version of the iOS SDK.")

    parser.add_argument("--sdk", dest="sdk_string")

    arguments = parser.parse_args()

    return arguments.sdk_string

def main():

    sdk = command_line_controller()
    if is_sdk_installed(sdk) == False:
        install_sdk(sdk)

if __name__ == '__main__':
    main()

