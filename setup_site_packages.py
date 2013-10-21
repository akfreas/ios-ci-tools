#!/usr/bin/env python

from boto.s3.connection import S3Connection
from zipfile import ZipFile
from tempfile import mktemp
import os

bucket_name = "travis-assets"

access_key = os.getenv("AWS_ACCESS_KEY_ID")
secret_key = os.getenv("AWS_SECRET_KEY")

conn = S3Connection(access_key, secret_key)

bucket = conn.get_bucket(bucket_name)

site_packages_key = bucket.get_key("site-packages.zip")

temp_zip_path = mktemp()

temp_zip_file = open(temp_zip_path, "w")

site_packages_key.get_contents_to_file(temp_zip_file)

temp_zip_file.close()

zip_file = ZipFile(temp_zip_path)

common_scripts = os.getenv("COMMON_SCRIPTS_HOME")
import pdb;pdb.set_trace()
zip_file.extractall("%s/lib/python2.7/site-packages" % common_scripts)
zip_file.close()


