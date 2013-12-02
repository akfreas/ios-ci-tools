#!/usr/bin/env python

import os
import shutil
from zipfile import ZipFile
from boto.s3.connection import S3Connection
from tempfile import mkdtemp


aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_KEY")
key_password = os.getenv("KEY_PASSWORD")
s3_bucket_name = os.getenv("S3_CERT_BUCKET")
certs_key_name = os.getenv("S3_CERT_KEY")
home_dir = os.getenv("HOME")



conn = S3Connection(aws_access_key_id, aws_secret_access_key)

bucket = conn.get_bucket(s3_bucket_name)

key = bucket.get_key(certs_key_name)

assets_path = "%s/assets" % home_dir
os.mkdir(assets_path)
zip_path = "%s/%s" % (assets_path, key.name)
key.get_contents_to_filename(zip_path)

cert_zip = ZipFile(zip_path)
cert_zip.extractall(assets_path)



provisioning_profile_dir = "%s/Library/MobileDevice/Provisioning Profiles" % home_dir 
os.makedirs(provisioning_profile_dir)
os.system("security create-keychain -p travis ios-build.keychain")
os.chdir(assets_path)
for asset_file in os.listdir(assets_path):
    file_ext = os.path.splitext(asset_file)[1]
    abs_path = os.path.abspath(asset_file)
    if file_ext == ".p12":
        os.system("security import '%s' -k ~/Library/Keychains/ios-build.keychain -P %s -T /usr/bin/codesign" % (abs_path, key_password))
    elif file_ext == ".cer":
        os.system("security import '%s' -k ~/Library/Keychains/ios-build.keychain -T /usr/bin/codesign" % abs_path)
    elif file_ext == ".mobileprovision":
        shutil.copy(abs_path, provisioning_profile_dir) 

