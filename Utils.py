#!/usr/bin/env python
import os
from tempfile import mkstemp
from Foundation import NSDictionary
import re
import pystache

def create_build_command(commands = ['build'], preprocessor_definitions=None,  **kwargs) :

    build_command = "xcodebuild"
    for flag in kwargs.keys():
        build_command += " -%s %s " % (flag, kwargs[flag])

    if preprocessor_definitions != None: 
        build_command += " GCC_PREPROCESSOR_DEFINITIONS"
        for gccflag in preprocessor_definitions.keys():
            build_command += " %s=%s" % (gccflag, preprocessor_definitions[gccflag])

    build_command += " ".join(commands)

    return build_command

def format_file_with_vars(the_file, template_vars):

    opened_file = open(the_file, "r")
    formatted_file = pystache.render(opened_file.read(), template_vars)
    temp_file_descriptor, temp_file_path = mkstemp()

    temp_file = os.fdopen(temp_file_descriptor, "w")
    temp_file.writelines(formatted_file)
    temp_file.close()

    return temp_file_path

def brand_icon(icon_path, version, tag_name):

    import _imaging
    from PIL import ImageFont, Image, ImageDraw

    image = Image.open(icon_path)
    #font = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.dfont", 15)
    drawing = ImageDraw.ImageDraw(image)
    drawing.text((10, image.size[1] * 0.8), tag_name)#, font=font)
    drawing.text((10, image.size[1] * 0.2), version)#, font=font)
    image.save(icon_path)



def build_settings_dict(pbxfile, native_target, configuration):

    pbxproj_plist = NSDictionary.dictionaryWithContentsOfFile_(pbxfile)['objects']
    build_conf_for_target = [pbxproj_plist[hashf]['buildConfigurationList'] for hashf in pbxproj_plist if pbxproj_plist[hashf]['isa'] == "PBXNativeTarget" and pbxproj_plist[hashf]['name'] == native_target][0]
    build_conf_list = pbxproj_plist[build_conf_for_target]['buildConfigurations']
    build_conf_dict_for_target = [pbxproj_plist[build_conf] for build_conf in build_conf_list if pbxproj_plist[build_conf]['name'] == configuration][0]

    conf_atom = build_conf_dict_for_target['buildSettings']

    atom = PBXAtom(conf_atom)

    return atom

def get_plist_path_from_pbxfile(pbxfile, native_target, configuration):

    conf_dict = build_settings_dict(pbxfile, native_target, configuration)
    info_plist_path = conf_dict['INFOPLIST_FILE']

    if "${PRODUCT_NAME}" in info_plist_path:
        info_plist_path = info_plist_path.replace("${PRODUCT_NAME}", native_target)

    return info_plist_path


class PBXAtom(dict):

    def __getitem__(self, key):

        regex = re.compile("\$\((.*)\)") 
        match = regex.match(super(PBXAtom, self).__getitem__(key))

        if match == None:
            return super(PBXAtom, self).__getitem__(key)
        else:
            new_key = match.groups()[0]
            return self.__getitem__(new_key)

       
