#!/usr/bin/env python

import os
import requests
import json
import re
import tempfile
import sys
import git

def list_app_names(build_dir):
    app_regex = re.compile("(.*)\.app$")

    build_dir_contents = os.listdir(build_dir)
    app_names = [app_regex.findall(app) for app in build_dir_contents if app_regex.match(app)]

    return app_names

def app_information_list(build_dir):

    app_regex = re.compile("(.*)\.app$")
    build_dir_contents = os.listdir(build_dir)

    app_info = [{'path' : os.path.abspath("%s/%s" %(build_dir, app)), 'name' : app_regex.findall(app)[0]} for app in build_dir_contents if app_regex.match(app)]

    return app_info


def package_app(sdk, app_path, app_name):

    temp_dir = tempfile.mkdtemp()
    ipa_path = "%s/%s.ipa" % (temp_dir, app_name)
    xc_run_command = "xcrun -sdk %s PackageApplication -v %s -o %s" % (sdk, app_path, ipa_path)
    print xc_run_command
    command = os.system(xc_run_command)
    app_package = open(ipa_path)
    return app_package
    
def create_app(product_name, note, spout_url, tags="") :

    app_create_url = "%s/app/create" % spout_url

    create_dict = {'note' : note,
            'device_type' : 'IOS',
            'product' : product_name,
            'tags' : ",".join(tags),}


    app_response = requests.post(app_create_url, create_dict)

    retval = None
    if app_response.status_code == 200:
        response_json = app_response.json()
        retval = response_json['new_app_id']
    return retval

    
def upload_asset_for_app(app_id, asset_path_or_file, spout_url, is_primary=False):
    
    if type(asset_path_or_file) == file:
        asset_file = asset_path_or_file
    else:
        asset_file = open(asset_path)
    upload_dict = {'asset_file' : asset_file}
    meta_dict = {'primary' : is_primary}

    upload_response = requests.post("%s/app/%s/asset/add" % (spout_url, app_id), meta_dict, files=upload_dict)

    print upload_response.text
    if upload_response.status_code == 200:
        return True
    else:
        return False

def compile_note_from_git_head():
    repo = git.Repo(os.getcwd())
    head_message = repo.head.commit.message
    head_short_sha = repo.head.commit.hexsha[:8]

    note = "%s %s" % (head_short_sha, head_message)
    return note

def zip_dsym(dsym_path):

    from zipfile import ZipFile
    temp_dir = tempfile.mkdtemp()
    temp_dsym_path = "%s/%s" % (temp_dir, os.path.basename(dsym_path))
    dsym_zip = ZipFile(temp_dsym_path, "w")
    zipdir(dsym_path, dsym_zip)
    dsym_zip.close()
    dsym_zip = open(temp_dsym_path, "r")
    return dsym_zip
    

def zipdir(path, zip):
    for root, dirs, files in os.walk(path):
        for file in files:
            zip.write(os.path.join(root, file))

def main():
    apps = app_information_list("build/Release-iphoneos/")
    product_name = os.getenv("DIST_PRODUCT")
    spout_url = os.getenv("UPLOAD_URL")
    note = compile_note_from_git_head()
    for app in apps:

        app_id = create_app(product_name, note, spout_url)
        app_package = package_app("iphoneos", app['path'], app['name'])
        upload_asset_for_app(app_id, app_package, spout_url, is_primary=True)
        print app_id

        dsym_path = "%s.dSYM" % app['path']
        dsym_zip = zip_dsym(dsym_path)
        upload_asset_for_app(app_id, dsym_zip, spout_url)
        

if __name__ == "__main__":
    main()

    
    

    
