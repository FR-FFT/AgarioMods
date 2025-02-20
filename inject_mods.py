PACKEDIPA_PATH = "downloads/Agario.zip"

import json
import os
import subprocess
import shutil
import time

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

def flatten_name(name):
    return "".join([c for c in name if c.isalpha()]).lower()

def inject_files(mod_type, working_path):
    if os.path.isdir(f"mods/{mod_type}/files"):
        for item in os.listdir(f"mods/{mod_type}/files"):
            src = f"mods/{mod_type}/files/{item}"
            dst = f"{working_path}/Payload/agar.io.app/{item}"
            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                shutil.copyfile(src, dst)


def inject_tweaks(name, new_unpacked_ipa_path, tweaks, mod_config):
    # check if we have a custom icon
    if os.path.isfile(f"icons/{name}.png"):
        cmd = ["cyan", "-uwdeg", "-i", f"{name}.ipa", "-o", f"{name} patched.ipa", "-b", f"com.miniclip.agar.io.{flatten_name(name)}", "-k", f"icons/{name}.png", "-n", mod_config["app_name"], "-f"] + tweaks
    else:
        cmd = ["cyan", "-uwdeg", "-i", f"{name}.ipa", "-o", f"{name} patched.ipa", "-b", f"com.miniclip.agar.io.{flatten_name(name)}", "-n", mod_config["app_name"], "-f"] + tweaks
    subprocess.run(cmd)
    os.remove(f"{name}.ipa") # unpatched version no longer necessary
    os.sync()
    tries = 0
    while tries < 5:
        try:
            os.replace( f"{name} patched.ipa", f"{name}.ipa")
            break
        except PermissionError:
            tries += 1
            if tries >= 5:
                raise
            print("File locked, sleeping")
            time.sleep(7.5)


def prepare_files(base_packed_ipa_path, type):
    if not os.path.exists(f"working"):
        os.mkdir("working")
    if not os.path.exists(f"working/{type}"):
        os.mkdir(f"working/{type}")
    new_unpacked_ipa_path = f"working/{type}/Agario"

    # clean up
    if os.path.exists(new_unpacked_ipa_path):
        shutil.rmtree(new_unpacked_ipa_path) 
    if os.path.exists(f"{new_unpacked_ipa_path}.zip"):
        os.remove(f"{new_unpacked_ipa_path}.zip") 
    
    print("Copying packed ipa to working directory")
    shutil.copyfile(base_packed_ipa_path, f"{new_unpacked_ipa_path}.zip") # just to prevent collision

    shutil.unpack_archive(f"{new_unpacked_ipa_path}.zip", new_unpacked_ipa_path)
    
def inject_mods(base_packed_ipa_path, mod_config, name):
    # TODO: potential improvements: separate mods more clearly, add combinations
    assert len(mod_config["mods"]) > 0

    # use mods/mod_type/ to get tweaks
    tweaks = list(set([f"mods/{mod_type}/tweaks/{f}" for mod_type in mod_config["mods"] for f in os.listdir(f"mods/{mod_type}/tweaks")]))

    print(f"Creating {name}")
    
    prepare_files(base_packed_ipa_path, name)

    new_unpacked_ipa_path = f"working/{name}/Agario"

    # copy necessary files into the payload
    print("Injecting files necessary for the mod to function")
    for mod_type in mod_config["mods"]:
        inject_files(mod_type, new_unpacked_ipa_path)


    print("Repacking ipa") # TODO: use low compression because we're going to unpack it again
    shutil.make_archive(name, "zip", new_unpacked_ipa_path)

    os.sync()
    tries = 0
    while tries < 5:
        try:
            os.replace( f"{name}.zip", f"{name}.ipa")
            break
        except PermissionError:
            tries += 1
            if tries >= 5:
                raise
            print("File locked, sleeping")
            time.sleep(7.5)


    inject_tweaks(name, new_unpacked_ipa_path, list(set(tweaks)), mod_config)



    print("Deleting working directory")
    shutil.rmtree("working")
    print("Moving modified ipa to ModifiedIPAs")
    shutil.move(f"{name}.ipa", f"ModifiedIPAs/{name}.ipa")
    print(f"Done creating {name}")


def main():
    os.mkdir("ModifiedIPAs")

    # better?
    # name must be unique
    config = json.load(open("config.json"))
    for mod_type in config:
        inject_mods(PACKEDIPA_PATH, config[mod_type], mod_type)


if __name__ == "__main__":
    main()