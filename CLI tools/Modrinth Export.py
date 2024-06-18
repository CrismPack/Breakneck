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
git_path = "D:\\GitHub Projects\\Breakneck\\"
minecraft_version = "1.21"
pack_version = "4.0.0_pre2"
packwiz_side = "client"



packwiz_path = git_path + "Packwiz\\" + minecraft_version + "\\"
packwiz_exe_path = os.path.expanduser("~") + "\\go\\bin\\packwiz.exe"
packwiz_manifest = "pack.toml"
packwiz_installer_path = git_path + "CLI tools\\packwiz-installer-bootstrap.jar"


refresh_only = False
gh_login = False
export_mmc_modrinth = True
export_mmc_curseforge = True
export_packwiz_modrinth = False


def main():
    os.chdir(packwiz_path)
    
    # Used for authenticating with GitHub for faster API responses.
    if gh_login:
        subprocess.call("mmc-export gh-login")
    

    if not refresh_only:
        if export_packwiz_modrinth:
            # Export MR modpack.
            subprocess.call(f"{packwiz_exe_path} mr export", shell=True)
        

        # Creates mmc-cache folder if it doesn't already exist.
        mmc_cache_path = packwiz_path + "mmc-cache\\"
        try:
            os.mkdir(mmc_cache_path)
        except:
            print("")
        
        os.chdir(mmc_cache_path)


        retain = ["packwiz-installer.jar"] # Files that shouldn't be deleted
        
        # Loop through everything in folder in current working directory
        for item in os.listdir(os.getcwd()):
            if item not in retain:  # If it isn't in the list for retaining
                try:
                    os.remove(item)  # Remove the item
                except OSError as e:
                    print(e)
                try:
                    rmtree(item)
                except OSError as e:
                    print(e)


        # Export Packwiz modpack to MMC cache folder and zip it.
        subprocess.call(f"java -jar \"{packwiz_installer_path}\" -s {packwiz_side} \"{packwiz_path + packwiz_manifest}\"", shell=True)
        

        move_list = ["shaderpacks", "resourcepacks", "mods", "config"]
        

        # Creates mmc\.minecraft folder if it doesn't already exist.
        mmc_dotminecraft_path = mmc_cache_path + ".minecraft\\"
        try:
            os.mkdir(mmc_dotminecraft_path)
        except:
            print("")

        # Moves override folders into .minecraft folder
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
        
    elif refresh_only:
        subprocess.call(f"{packwiz_exe_path} refresh", shell=True)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Operation aborted by user.")
        exit(-1)
