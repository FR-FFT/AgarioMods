UNPACKEDIPA_PATH = "downloads/Agario"

import os
import subprocess
import shutil
import random

"""
usage: pyzule [-h] [-i input] [-o output] [-z .pyzule] [-n name] [-v version] [-b bundle id] [-m minimum] [-c [level]]
              [-k icon] [-x entitlements] [-l plist] [-r url [url ...]] [-f files [files ...]] [-u] [-w] [-d] [-s]
              [-e] [-g] [-p] [-t] [--update]

an azule "clone" written in python3.

options:
  -h, --help            show this help message and exit
  -i input              the .ipa/.app to patch
  -o output             the name of the patched .ipa/.app that will be created
  -z .pyzule            the .pyzule file to get info from
  -n name               modify the app's name
  -v version            modify the app's version
  -b bundle id          modify the app's bundle id
  -m minimum            change MinimumOSVersion
  -c [level]            the compression level of the output ipa (default is 6, 0-9)
  -k icon               an image file to use as the app icon
  -x entitlements       a file containing entitlements to sign the app with
  -l plist              a plist to merge with the existing Info.plist
  -r url [url ...]      url schemes to add
  -f files [files ...]  tweak files to inject into the ipa
  -u                    remove UISupportedDevices
  -w                    remove watch app
  -d                    enable files access
  -s                    fakesigns the ipa (for use with appsync)
  -e                    remove app extensions
  -g                    remove encrypted extensions
  -p                    inject into @executable_path
  -t                    use substitute instead of substrate
  --update              check for updates
  """
def inject_images(mod_type, working_path):
    for item in os.listdir(f"mods/images/{mod_type}"):
        src = f"mods/images/{mod_type}/{item}"
        dst = f"{working_path}/Payload/agar.io.app/{item}"
        if os.path.isdir(src):
            shutil.copytree(src, dst)
        else:
            shutil.copyfile(src, dst)

def inject_other(mod_type, working_path):
    for item in os.listdir(f"mods/other/{mod_type}"):
        src = f"mods/other/{mod_type}/{item}"
        dst = f"{working_path}/Payload/agar.io.app/{item}"
        shutil.copyfile(src, dst)

def inject_tweaks(name, new_unpacked_ipa_path, tweaks):
    cmd = ["pyzule", "-uwdeg", "-i", f"{name}.ipa", "-o", f"{new_unpacked_ipa_path}-patched.ipa", "-f"] + tweaks
    subprocess.run(cmd)


def prepare_files(base_unpacked_ipa_path, type):
    if not os.path.exists(f"working"):
        os.mkdir("working")
    new_unpacked_ipa_path = f"working/{type}/Agario"
    if os.path.exists(new_unpacked_ipa_path):
        shutil.rmtree(new_unpacked_ipa_path) # clean up
    
    print("Copying unpacked ipa to working directory")
    shutil.copytree(base_unpacked_ipa_path, new_unpacked_ipa_path) # just to prevent collision
    


def inject_cracked_kahraba_mod(base_unpacked_ipa_path):
    print("Creating cracked kahraba mod")
    
    prepare_files(base_unpacked_ipa_path, "kahraba")

    new_unpacked_ipa_path = "working/kahraba/Agario"

    # copy necessary files into the payload
    print("Injecting files necessary for the mod to function")
    inject_images("kahraba", new_unpacked_ipa_path)
    inject_other("kahraba", new_unpacked_ipa_path)

    print("Repacking ipa")
    shutil.make_archive("Kahraba cracked", "zip", new_unpacked_ipa_path)
    os.rename( "Kahraba cracked.zip", "Kahraba cracked.ipa")

    inject_tweaks("Kahraba cracked", new_unpacked_ipa_path, ["mods/tweaks/kahraba/AgarioTweak.dylib", "mods/tweaks/kahraba/kahraba.dylib"])
    shutil.rmtree("working")

def inject_xelahot_mod(base_unpacked_ipa_path):
    print("Creating xelahot's mod")
    
    prepare_files(base_unpacked_ipa_path, "xelahot")

    new_unpacked_ipa_path = "working/xelahot/Agario"

    # copy necessary files into the payload
    print("Injecting files necessary for the mod to function")
    inject_images("xelahot", new_unpacked_ipa_path)

    print("Repacking ipa")
    shutil.make_archive("Xelahot", "zip", new_unpacked_ipa_path)
    os.rename( "Xelahot.zip", "Xelahot.ipa")

    inject_tweaks("Xelahot", new_unpacked_ipa_path, ["mods/tweaks/xelahot/xelahot.deb", "mods/tweaks/xelahot/images.deb"])

    shutil.rmtree("working")
    

def inject_ctrl_mod(base_unpacked_ipa_path):
    print("Creating QxAnarky's ctrl mod")
    
    prepare_files(base_unpacked_ipa_path, "qxanarky")

    new_unpacked_ipa_path = "working/ctrl/Agario"

    # copy necessary files into the payload
    print("Injecting files necessary for the mod to function")
    inject_images("qxanarky", new_unpacked_ipa_path)

    print("Repacking ipa")
    shutil.make_archive("Ctrl", "zip", new_unpacked_ipa_path)
    os.rename( "Ctrl.zip", "Ctrl.ipa")

    inject_tweaks("Ctrl", new_unpacked_ipa_path, ["mods/tweaks/qxanarky/ctrl.dylib", "mods/tweaks/xelahot/images.deb"])

    shutil.rmtree("working")

inject_cracked_kahraba_mod("downloads/Agario") # test

