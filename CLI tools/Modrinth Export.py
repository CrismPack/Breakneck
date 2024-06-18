import os
import json
import subprocess
from typing import IO
from pathlib import Path
from zipfile import ZipFile
from shutil import unpack_archive, rmtree, make_archive, move

import toml  # pip install toml


#user_path = os.path.expanduser("D:")
modpack_name = "Breakneck"
minecraft_version = "1.21"
git_path = "D:\\GitHub Projects\\Breakneck\\"
packwiz_side = "client"


packwiz_path = git_path + "Packwiz\\" + minecraft_version + "\\"
packwiz_exe_path = os.path.expanduser("~") + "\\go\\bin\\packwiz.exe"
packwiz_manifest = "pack.toml"
packwiz_installer_path = git_path + "CLI tools\\packwiz-installer-bootstrap.jar"
bcc_config_path = packwiz_path + "config\\bcc.json"

refresh_only = False
gh_login = False
export_mmc_modrinth = True
export_mmc_curseforge = True
export_packwiz_modrinth = False
update_bcc_version = True
cleanup_cache = True


def clear_mmc_cache(path):
    os.chdir(path)
    retain = ["packwiz-installer.jar"] # Files that shouldn't be deleted
    
    # Loop through everything in folder in current working directory
    for item in os.listdir(os.getcwd()):
        if item not in retain:  # If it isn't in the list for retaining
            try:
                os.remove(item)  # Remove the item
            except:
                pass
            try:
                rmtree(item)
            except:
                pass



def main():
    os.chdir(packwiz_path)
    
    with open(packwiz_manifest, "r") as f:
        pack_toml = toml.load(f)
    pack_version = pack_toml["version"]
    
    # Used for authenticating with GitHub for faster API responses.
    if gh_login:
        subprocess.call("mmc-export gh-login")
    

    if not refresh_only:
        # Update version number in BCC
        if update_bcc_version:
            with open(bcc_config_path, "r") as f:
                bcc_json = json.load(f)
            bcc_json["modpackVersion"] = pack_version
            with open(bcc_config_path, "w") as f:
                json.dump(bcc_json, f)

        # Refresh the packwiz index
        subprocess.call(f"{packwiz_exe_path} refresh", shell=True)

        if export_packwiz_modrinth:
            # Export MR modpack.
            subprocess.call(f"{packwiz_exe_path} mr export", shell=True)
            print("[PackWiz] Modrinth exported.")

        # Creates mmc-cache folder if it doesn't already exist and ensure that it is empty.
        mmc_cache_path = packwiz_path + "mmc-cache\\"
        try:
            os.mkdir(mmc_cache_path)
        except:
            pass
        clear_mmc_cache(mmc_cache_path)


        # Export Packwiz modpack to MMC cache folder and zip it.
        subprocess.call(f"java -jar \"{packwiz_installer_path}\" -s {packwiz_side} \"{packwiz_path + packwiz_manifest}\"", shell=True)
        

    
        # Creates mmc\.minecraft folder if it doesn't already exist.
        mmc_dotminecraft_path = mmc_cache_path + ".minecraft\\"
        try:
            os.mkdir(mmc_dotminecraft_path)
        except:
            pass
        
        
        # Moves override folders into .minecraft folder
        move_list = ["shaderpacks", "resourcepacks", "mods", "config"]
        for item in os.listdir(os.getcwd()):
            if item in move_list:
                move(item, mmc_dotminecraft_path)



        os.chdir(packwiz_path)
        make_archive("mcc-cache", 'zip', mmc_cache_path)

        mmc_config = git_path + "Packwiz\\mmc-export.toml"

        if export_mmc_curseforge:
            args = (
                "mmc-export",
                "--input", packwiz_path + "mcc-cache.zip",
                "--format", "CurseForge",
                "-o", packwiz_path,
                "-c", mmc_config,
                "-v", pack_version,
                "--scheme", modpack_name + "-" + minecraft_version + "-{version}",
            ); subprocess.call(args, shell=True)
            print("[MMC] CurseForge exported.")

        if export_mmc_modrinth:
            args = (
                "mmc-export",
                "--input", packwiz_path + "mcc-cache.zip",
                "--format", "Modrinth",
                "--modrinth-search", "accurate",
                "-o", packwiz_path,
                "-c", mmc_config,
                "-v", pack_version,
                "--scheme", modpack_name + "-" + minecraft_version + "-{version}",
            ); subprocess.call(args, shell=True)
            print("[MMC] Modrinth exported.")
        
        if cleanup_cache:
            os.remove("mcc-cache.zip")
            clear_mmc_cache(mmc_cache_path)
            print("Cache cleanup finished.")

    elif refresh_only:
        subprocess.call(f"{packwiz_exe_path} refresh", shell=True)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Operation aborted by user.")
        exit(-1)
