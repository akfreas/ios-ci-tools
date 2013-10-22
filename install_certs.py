#!/usr/bin/env python

import os
import shutil
from zipfile import ZipFile
from boto.s3.connection import S3Connection
from tempfile import mkdtemp


aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_KEY")
key_password = os.getenv("KEY_PASSWORD")
s3_bucket_name = "travis-assets"
certs_key_name = "certs.zip"
home_dir = os.getenv("HOME")



conn = S3Connection(aws_access_key_id, aws_secret_access_key)

bucket = conn.get_bucket(s3_bucket_name)

key = bucket.get_key(certs_key_name)

temp_path = mkdtemp()
cert_zip_path = "%s/%s" % (temp_path, key.name)
key.get_contents_to_filename(cert_zip_path)

cert_zip = ZipFile(cert_zip_path)
cert_zip.extractall(temp_path)
assets_dir = "~/assets"

print os.listdir("%s/certs" % temp_path)


provisioning_profile_dir = "%s/Library/MobileDevice/Provisioning Profiles" % home_dir 
os.system("security create-keychain -p travis ios-build.keychain")
os.system("security import %s/certs/apple.cer ~/Library/Keychains/ios-build.keychain -T /usr/bin/codesign" % temp_path)
os.system("security import %s/certs/iPhone-distribution.cer -k ~/Library/Keychains/ios-build.keychain -T /usr/bin/codesign" % temp_path)
os.system("security import %s/certs/iPhone-distribution.p12 -k ~/Library/Keychains/ios-build.keychain -P %s -T /usr/bin/codesign" % (temp_path, key_password))
os.makedirs(provisioning_profile_dir)
shutil.copy("%s/certs/DriverMagic.mobileprovision" % temp_path, provisioning_profile_dir) 
os.makedirs(assets_dir)

shutil.copy("%s/certs/DM-Config.xcconfig" % temp_path, assets_dir)
print os.listdir(assets_dir)
