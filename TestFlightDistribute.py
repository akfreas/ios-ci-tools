#!/usr/bin/env python

import biplist
import os
import requests
import tempfile
import sys
import git

testflight_api_url = "http://testflightapp.com/api/builds.json"

def upload_app_to_testflight(archive_path, testflight_api_token, testflight_team_token, testflight_distro_lists=[], notify=True):

    print archive_path
    plist_path = "%s/Info.plist" % archive_path
    archive_plist = biplist.readPlist(plist_path)

    app_path = archive_plist['ApplicationProperties']['ApplicationPath']
    app_name = archive_plist['Name']
    full_app_path = "%s/Products/%s" % (archive_path, app_path)
    dsym_path = "%s/dSYMs/%s.app.dSYM" % (archive_path, app_name)

    app_package = package_app('iphoneos', full_app_path, app_name)
    app_dsym_zip = zip_dsym(dsym_path)
    print app_dsym_zip
    notes = compile_note_from_git_head()
    distro_list = ",".join(testflight_distro_lists)

    file_upload_params = {'file' : app_package, 'dsym' : app_dsym_zip}
    meta_params = {
            'api_token'          : testflight_api_token,
            'team_token'         : testflight_team_token,
            'notes'              : notes,
            'notify'             : notify,
            'distribution_lists' : distro_list
            }
    print meta_params
    upload_response = requests.post(testflight_api_url, meta_params, files=file_upload_params)

    app_package.close()
    app_dsym_zip.close()

    print upload_response.text

    if upload_response.status_code == 200:
        return True
    else:
        return False


def package_app(sdk, app_path, app_name):

    temp_dir = tempfile.mkdtemp()
    ipa_path = "%s/%s.ipa" % (temp_dir, app_name)
    xc_run_command = "xcrun -sdk %s PackageApplication '%s' -o %s" % (sdk, app_path, ipa_path)
    print xc_run_command
    command = os.system(xc_run_command)
    app_package = open(ipa_path)
    return app_package
 
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


def compile_note_from_git_head():
    repo = git.Repo(os.getcwd())
    head_message = repo.head.commit.message
    head_short_sha = repo.head.commit.hexsha[:8]

    note = "%s %s" % (head_short_sha, head_message)
    return note

def main():
    archive_path = os.popen("find ~/Library/Developer/Xcode/Archives -type d -Btime -60m -name '*.xcarchive' | head -1").read().strip()
    print archive_path
    api_token = os.getenv("TESTFLIGHT_API_TOKEN")
    team_token = os.getenv("TESTFLIGHT_TEAM_TOKEN")

    upload_app_to_testflight(archive_path, api_token, team_token)

if __name__ == "__main__":
    main()
