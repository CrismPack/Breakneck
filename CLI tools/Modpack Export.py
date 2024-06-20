import os
import json
import subprocess
from shutil import rmtree, make_archive, move
from pathlib import Path

import toml  # pip install toml


user_path = os.path.expanduser("~")

modpack_name = "Breakneck"
minecraft_version = "1.21"
packwiz_side = "client"

# Get path of project dynamically.
script_path = str(__file__)
git_path = script_path.replace("CLI tools\\Modpack Export.py","")
print("[DEBUG] " + git_path)

packwiz_path = git_path + "Packwiz\\" + minecraft_version + "\\"
packwiz_exe_path = os.path.expanduser("~") + "\\go\\bin\\packwiz.exe"
packwiz_manifest = "pack.toml"
packwiz_installer_path = git_path + "CLI tools\\packwiz-installer-bootstrap.jar"
bcc_config_path = packwiz_path + "config\\bcc.json"

print("[DEBUG] " + packwiz_path)

# Remap paths if running on Linux
if os.name == "posix":
    print("Code being run on Linux. Remapping paths...")
    git_path = git_path.replace("\\","/")
    packwiz_path = packwiz_path.replace("\\","/")
    packwiz_exe_path = packwiz_exe_path.replace("\\","/")
    packwiz_installer_path = packwiz_installer_path.replace("\\","/")
    bcc_config_path = bcc_config_path.replace("\\","/")
    print("[DEBUG] " + git_path)

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
    
    # Parse pack.toml for modpack version.
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
        if os.name == "posix":
            mmc_cache_path = mmc_cache_path.replace("\\","/")
        try:
            os.mkdir(mmc_cache_path)
        except:
            pass
        clear_mmc_cache(mmc_cache_path)



        
        file = Path(mmc_cache_path + "packwiz-installer.jar")
        if file.is_file():
            # Export Packwiz modpack to MMC cache folder and zip it.
            subprocess.call(f"java -jar \"{packwiz_installer_path}\" -s {packwiz_side} \"{packwiz_path + packwiz_manifest}\" --bootstrap-no-update", shell=True)
        else:
            # Export Packwiz modpack to MMC cache folder and zip it.
            subprocess.call(f"java -jar \"{packwiz_installer_path}\" -s {packwiz_side} \"{packwiz_path + packwiz_manifest}\"", shell=True)

        # Creates mmc\.minecraft folder if it doesn't already exist.
        mmc_dotminecraft_path = mmc_cache_path + ".minecraft\\"
        if os.name == "posix":
            mmc_dotminecraft_path = mmc_dotminecraft_path.replace("\\","/")
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
        make_archive("mcc-cache", 'zip', mmc_cache_path) # Creates mcc-cache.zip file based on mmc-cache folder.
        
        mmc_config = git_path + "Packwiz\\mmc-export.toml"
        if os.name == "posix":
            mmc_config = mmc_config.replace("\\","/")

        # Export CurseForge modpack using MMC method.
        cf_export_path = git_path + "Export\\CurseForge\\"
        if export_mmc_curseforge:
            print("[MMC] Exporting CurseForge...")
            args = (
                "mmc-export",
                "--input", packwiz_path + "mcc-cache.zip",
                "--format", "CurseForge",
                "-o", cf_export_path,
                "-c", mmc_config,
                "-v", pack_version,
                "--scheme", modpack_name + "-" + minecraft_version + "-{version}",
            ); subprocess.call(args, shell=True)
            print("[MMC] CurseForge exported.")

        # Export Modrinth modpack using MMC method.
        mr_export_path = git_path + "Export\\Modrinth\\"
        if os.name == "posix":
            mr_export_path = mr_export_path.replace("\\","/")
        if export_mmc_modrinth:
            print("[MMC] Exporting Modrinth...")
            args = (
                "mmc-export",
                "--input", packwiz_path + "mcc-cache.zip",
                "--format", "Modrinth",
                "--modrinth-search", "accurate",
                "-o", mr_export_path,
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
        # print("")
        main()
    except KeyboardInterrupt:
        print("Operation aborted by user.")
        exit(-1)
