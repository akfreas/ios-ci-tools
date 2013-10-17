import plistlib
import argparse
from Foundation import NSMutableDictionary
from xml.parsers.expat import ExpatError

from tempfile import mkstemp
from shutil import move
from os import remove, close


  
def increment_release_version(filename, version):

    keyToModify = 'CFBundleVersion'
    plist = NSMutableDictionary.dictionaryWithContentsOfFile_(filename)
    if keyToModify in plist.allKeys():
        versionString = plist[keyToModify]
        versionList = versionString.split(".")
        versionList.append(version)
        versionString = ".".join(versionList)
        plist[keyToModify] = versionString
        plist.writeToFile_atomically_(filename, 1)
        return versionString


def increment_development_version(filename, version):

    keyToModify = 'CFBundleShortVersionString'
    plist = NSMutableDictionary.dictionaryWithContentsOfFile_(filename)
    if keyToModify in plist.allKeys():
        versionString = plist[keyToModify]
        versionList = versionString.split(".")
        lastVersionNumber = int(versionList[-1])
        versionList.append(version)
        versionString = ".".join(versionList)
        plist[keyToModify] = versionString
        plist.writeToFile_atomically_(filename, 1)
        return versionString

def change_provisioning_profile(filename, build_conf_name, provisioning_profile):

    pbx_dict = NSMutableDictionary.dictionaryWithContentsOfFile_(filename)
    configurations = [x for x in pbx_dict['objects'] if pbx_dict['objects'][x]['isa'] == "XCBuildConfiguration" and pbx_dict['objects'][x]['name'] == "Release" and "PROVISIONING_PROFILE" in pbx_dict['objects'][x]['buildSettings'].allKeys()]    

    profiles_to_replace = []

    for config in configurations:
        profiles_to_replace.append(pbx_dict['objects'][config]['buildSettings']['PROVISIONING_PROFILE'])
        profiles_to_replace.append(pbx_dict['objects'][config]['buildSettings']['PROVISIONING_PROFILE[sdk=iphoneos*]'])

    for profile in profiles_to_replace:
        print "%s was replaced with %s in %s" % (profile, provisioning_profile, filename)
        replace(filename, profile, provisioning_profile)

def replace(file, pattern, subst):
    #Create temp file
    fh, abs_path = mkstemp()
    new_file = open(abs_path,'w')
    old_file = open(file)
    for line in old_file:
        new_file.write(line.replace(pattern, subst))
    #close temp file
    new_file.close()
    close(fh)
    old_file.close()
    #Remove original file
    remove(file)
    #Move new file
    move(abs_path, file)

def change_bundle_id(filename, new_bundle_id):
	
    keyToModify = 'CFBundleIdentifier'
    plist = NSMutableDictionary.dictionaryWithContentsOfFile_(filename)
    if plist != None and keyToModify in plist.allKeys():
        plist[keyToModify] = new_bundle_id
        plist.writeToFile_atomically_(filename, 1)

def commandLineController():

    parser = argparse.ArgumentParser(description="Allows manipulation of bundle version #s in Xcode project Info.plists.")

    parser.add_argument('--filename', '-f', dest="filename", help="Filename for plist to be modified.")
    parser.add_argument('--version', '-v', dest="version", help="Development version for app.")
    parser.add_argument('--new_bundle_id', '-n', dest="new_bundle_id", help="Bundle ID to change in app.")
    parser.add_argument('--release_provisioning_profile', '-r', dest="release_prov_profile", help="Provisioning profile to use when building with release config.")

    arguments = parser.parse_args()

    if(arguments.version):    
        increment_development_version(arguments.filename, arguments.version)
        increment_release_version(arguments.filename, arguments.version)

    if(arguments.new_bundle_id):
        change_bundle_id(arguments.filename, arguments.new_bundle_id)
    if(arguments.release_prov_profile):
        change_provisioning_profile(arguments.filename, "Release", arguments.release_prov_profile)

def main():
    commandLineController()

if __name__ == '__main__':
    main()
