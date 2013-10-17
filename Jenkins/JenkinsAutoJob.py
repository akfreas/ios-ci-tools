#!/usr/bin/python

from git import *
from argparse import ArgumentParser
import urllib
import requests
import shutil
from elementtree.ElementTree import Element, parse


import os

class JenkinsAutoJob:


    def __init__(self, repo_path, prefix, root_job_dir, config_template, jenkins_url):
        self.repo_path = repo_path
        self.prefix = prefix
        self.config_xml = "config.xml"
        self.config_template = config_template
        self.root_job_dir=  root_job_dir
        self.verbose = False
        print "The cwd is: " + os.getcwd()
        self.repo = Repo.init()
        self.jenkins_url = jenkins_url

        if len(self.repo.remotes) < 1:
            self.start()

    def start(self):

        remote = self.repo.create_remote("origin", self.repo_path)

    def poll_and_create_job(self):

        self.check_remote_branches(self.new_branch_callback, self.branch_removal_callback) 

    def check_remote_branches(self, additional_branch_callback, branch_removal_callback):

        try: 
            if self.verbose: old_refs = self.repo.remote().refs
            print "Old refs in repo: %s" % old_refs
        except AssertionError:
            print "No old refs in repo, assuming new repo."
            old_refs = []
        self.repo.remote().update()
        updated_refs = [ref for ref in self.repo.remote().refs if ref not in self.repo.remote().stale_refs]

        if self.verbose: print "Updated refs: %s" % updated_refs

        new_refs = [ref for ref in updated_refs if ref not in old_refs]
        deleted_refs = [ref for ref in old_refs if ref not in updated_refs]
        print new_refs, deleted_refs
        if len(new_refs) > 0:
            additional_branch_callback(new_refs)
            self.reload_jenkins()
        if len(deleted_refs) > 0:
            branch_removal_callback(deleted_refs)
            self.reload_jenkins()

    def reload_jenkins(self):
        requests.post(self.jenkins_url + "/reload")

    def branch_removal_callback(self, ref_list):

        for ref in ref_list:

            branch_name = ref.name
            self.delete_job(branch_name)

    def new_branch_callback(self, ref_list):
        
        for ref in ref_list:

            #branch_name = ref.name.split("/")[-1]
            #branch_name = ref.name.replace("origin/", "") #HAXHAXHAX
            branch_name = ref.name
            print "Creating job for %s branch." % branch_name
            self.create_job(branch_name)

    def delete_job(self, branch_name):


        cleaned_branch_name = branch_name.replace("origin/", "").replace("/", "_")
        job_name = "%s-%s" % (self.prefix, cleaned_branch_name)
        full_job_path = "%s/%s" % (self.root_job_dir, job_name)
        try:
            shutil.rmtree(full_job_path)
        except OSError:
            print "No such job for branch %s in %s!" % (branch_name, full_job_path)

    def create_job(self, branch_name): 

        cleaned_branch_name = branch_name.replace("origin/", "").replace("/", "_")
        job_name = "%s-%s" % (self.prefix, cleaned_branch_name)
        full_job_path = "%s/%s" % (self.root_job_dir, job_name)
        try:
            os.mkdir(full_job_path)
        except OSError:
            print "Job already exists! Not creating."
            return
        template = open(self.config_template, "r")

        parser = parse(self.config_template)
        top_element = parser.getroot()

        branch_element = top_element.getiterator("hudson.plugins.git.BranchSpec")[0]
        [branch_element.remove(element) for element in branch_element.getchildren()]
        new_name_element = Element("name")
        new_name_element.text = branch_name
        branch_element.append(new_name_element)

        parser.write("%s/%s" % (full_job_path, self.config_xml))

def command_line_controller():

    parser = ArgumentParser(description="Polls repos for new branches and creates jenkins jobs if new branches are found.") 

    parser.add_argument("task", nargs=1)
    parser.add_argument("--job_root", "-j", dest="job_root", help="The path for jobs to be created.") 
    parser.add_argument("--repo", "-r", dest="repo", help="The path to the repo you want to pull.")
    parser.add_argument("--prefix", "-p", dest="prefix", help="Prefix for the job to be created.")
    parser.add_argument("--config-template-job", "-c", dest="config_template", help="Configuration template for jenkins job.")
    parser.add_argument("--verbose", "-v", action="store_true",  dest="verbose")
    parser.add_argument("--jenkins_url", "-u", default=os.getenv("JENKINS_URL"), dest="jenkins_url")
    parser.add_argument("--git-branch", "-g", dest="git_branch", help="The git branch to create the new job for.")

    args = parser.parse_args()

    print args.task

    if not args.repo:
        args.repo = os.getcwd()
    if not args.job_root:
        args.job_root = os.getenv("JENKINS_HOME") + "/jobs"
    config_template = "%s/%s/%s/%s" % (os.getenv("JENKINS_HOME"), "jobs", args.config_template, "config.xml")
    autojob = JenkinsAutoJob(jenkins_url=args.jenkins_url, repo_path=args.repo, root_job_dir=args.job_root, config_template=config_template, prefix=args.prefix)
    if args.verbose: autojob.verbose = True
    if args.task[0] == "poll-and-create":
        autojob.poll_and_create_job()
    elif args.task[0] == "create":
        autojob.create_job(args.git_branch)
        autojob.reload_jenkins()

if __name__ == '__main__':
    command_line_controller()
