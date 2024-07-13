import os
import json
import subprocess
from shutil import rmtree, make_archive, move
from pathlib import Path

import toml  # pip install toml
import yaml
from mdutils.mdutils import MdUtils
from mdutils import Html


##########################################################
# Configuration

refresh_only = False
gh_login = False
export_mmc_modrinth = True
export_mmc_curseforge = True
export_packwiz_modrinth = False
update_bcc_version = True
cleanup_cache = True
move_disabled_mods = True
test_linux_mappings = False
create_release_notes = True


##########################################################
# Variables
user_path = os.path.expanduser("~")

modpack_name = "Breakneck"
minecraft_version = "1.21"
packwiz_side = "client"

# Get path of project dynamically.
script_path = __file__
git_path = str(os.path.dirname(os.path.dirname(script_path))).replace("/","\\") # .replace("/","\\") is to ensure that the path will be in the Windows format.

print("[DEBUG] " + git_path)

packwiz_path = git_path + "\\Packwiz\\" + minecraft_version + "\\"
packwiz_exe_path = os.path.expanduser("~") + "\\go\\bin\\packwiz.exe"
packwiz_manifest = "pack.toml"
packwiz_installer_path = git_path + "\\CLI tools\\packwiz-installer-bootstrap.jar"
bcc_config_path = packwiz_path + "config\\bcc.json"

mmc_config = packwiz_path + "mmc-export.toml"
export_path = git_path + "\\Export\\"

mmc_cache_path = packwiz_path + "mmc-cache\\"
mmc_dotminecraft_path = mmc_cache_path + ".minecraft\\"
mmc_input_path = packwiz_path + "mcc-cache.zip"


print("[DEBUG] " + git_path)
print("[DEBUG] " + packwiz_path)
print("[DEBUG] " + packwiz_exe_path)
print("[DEBUG] " + packwiz_installer_path)
print("[DEBUG] " + bcc_config_path)
print("[DEBUG] " + mmc_config)
print("[DEBUG] " + export_path)
print("[DEBUG] " + mmc_cache_path)
print("[DEBUG] " + mmc_dotminecraft_path)
print("[DEBUG] " + mmc_input_path)


# Remap paths if running on Linux
if os.name == "posix" or test_linux_mappings:
    print("Code being run on Linux. Remapping paths...")
    git_path = git_path.replace("\\","/")
    packwiz_path = packwiz_path.replace("\\","/")
    packwiz_exe_path = packwiz_exe_path.replace("\\","/")
    packwiz_installer_path = packwiz_installer_path.replace("\\","/")
    bcc_config_path = bcc_config_path.replace("\\","/")
    
    mmc_config = mmc_config.replace("\\","/")
    export_path = export_path.replace("\\","/")
    
    mmc_cache_path = mmc_cache_path.replace("\\","/")
    mmc_dotminecraft_path = mmc_dotminecraft_path.replace("\\","/")
    mmc_input_path = mmc_input_path.replace("\\","/")    

    print("[DEBUG] " + git_path)
    print("[DEBUG] " + packwiz_path)
    print("[DEBUG] " + packwiz_exe_path)
    print("[DEBUG] " + packwiz_installer_path)
    print("[DEBUG] " + bcc_config_path)
    print("[DEBUG] " + mmc_config)
    print("[DEBUG] " + export_path)
    print("[DEBUG] " + mmc_cache_path)
    print("[DEBUG] " + mmc_dotminecraft_path)
    print("[DEBUG] " + mmc_input_path)


##########################################################
# Functions

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


##########################################################
# Main Program

def main():
    os.chdir(packwiz_path)
    
    # Parse pack.toml for modpack version.
    with open(packwiz_manifest, "r") as f:
        pack_toml = toml.load(f)
    pack_version = pack_toml["version"]
    

    # Used for authenticating with GitHub for faster API responses.
    if gh_login:
        subprocess.call("mmc-export gh-login")
    
    # Parse the related changelog file for overview details and create release markdown files for CF and MR.
    if create_release_notes:
        os.chdir(git_path)
        changelog_path = git_path + f"\\Changelogs\\{minecraft_version}+{pack_version}.yml"
        
        md_element_full_changelog = f"**[[Full Changelog]](https://wiki.crismpack.net/modpacks/breakneck-optimized/changelog/{minecraft_version}#v{pack_version})**"
        md_element_pre_release = '**This is a pre-release. Here be dragons!**'
        # md_element_bh_banner = "[![BisectHosting Banner](https://github.com/CrismPack/CDN/blob/main/desc/breakneck/bh.png?raw=true)](https://bisecthosting.com/CRISM)"
        md_element_crism_spacer = "![CrismPack Spacer](https://github.com/CrismPack/CDN/blob/main/desc/breakneck/79ESzz1-tiny.png?raw=true)"
        html_element_bh_banner = "<p><a href='https://bisecthosting.com/CRISM'><img src='https://github.com/CrismPack/CDN/blob/main/desc/breakneck/bh.png?raw=true' width='1000' /></a></p>"
        
        with open(changelog_path, "r") as f:
            changelog_yml = yaml.safe_load(f)
        update_overview = changelog_yml['Update overview']
        
        mdFile_CF = MdUtils(file_name='CurseForge-Release')
        mdFile_MR = MdUtils(file_name='Modrinth-Release')
        
        print(update_overview)
        
        if "beta" in pack_version or "alpha" in pack_version:
            print("pack_version = " + pack_version)
            mdFile_CF.new_paragraph(md_element_pre_release)
            mdFile_MR.new_paragraph(md_element_pre_release)
        
        mdFile_CF.new_paragraph(update_overview)
        mdFile_CF.new_paragraph("#### " + md_element_full_changelog)
        mdFile_CF.new_paragraph("<br>")
        mdFile_CF.new_paragraph(html_element_bh_banner)
        mdFile_CF.create_md_file()
        
        mdFile_MR.new_paragraph(update_overview)
        mdFile_MR.new_paragraph(md_element_full_changelog)
        mdFile_MR.new_paragraph(md_element_crism_spacer)
        mdFile_MR.create_md_file()
        
        os.chdir(packwiz_path)
        

    if not refresh_only:
        
        # Update version number in BCC
        if update_bcc_version:
            with open(bcc_config_path, "r") as f:
                bcc_json = json.load(f)
            bcc_json["modpackVersion"] = pack_version
            with open(bcc_config_path, "w") as f:
                json.dump(bcc_json, f)

        if move_disabled_mods:
            mods_path = packwiz_path + "mods\\"
            disabled_mods_path = mods_path + "disabled\\"
            if os.name == "posix":
                mods_path = mods_path.replace("\\","/")
                disabled_mods_path = disabled_mods_path.replace("\\","/")
            os.chdir(mods_path)
            
            # Parse mod toml files for (disabled) marker.
            for item in os.listdir():
                try:
                    with open(item, "r") as f:
                        mod_toml = toml.load(f)
                        if "disabled" in mod_toml["side"]:
                            f.close()
                            move(item, disabled_mods_path)

                except OSError as e:
                    print(e)



        os.chdir(packwiz_path)
        # Refresh the packwiz index
        subprocess.call(f"{packwiz_exe_path} refresh", shell=True)


        if export_packwiz_modrinth:
            # Export MR modpack.
            subprocess.call(f"{packwiz_exe_path} mr export", shell=True)
            print("[PackWiz] Modrinth exported.")


        # Creates mmc-cache folder if it doesn't already exist and ensure that it is empty.
        try:
            os.mkdir(mmc_cache_path)
        except:
            pass
        clear_mmc_cache(mmc_cache_path)



        
        file = Path(mmc_cache_path + "packwiz-installer.jar")
        if file.is_file():
            # Export Packwiz modpack to MMC cache folder and zip it.
            subprocess.call(f"java -jar \"{packwiz_installer_path}\" -s {packwiz_side} \"{packwiz_path + packwiz_manifest}\" -g --bootstrap-no-update", shell=True)
        else:
            # Export Packwiz modpack to MMC cache folder and zip it.
            subprocess.call(f"java -jar \"{packwiz_installer_path}\" -s {packwiz_side} \"{packwiz_path + packwiz_manifest}\" -g", shell=True)

        # Creates mmc\.minecraft folder if it doesn't already exist.
        try:
            os.mkdir(mmc_dotminecraft_path)
        except:
            pass
        
        
        # Moves override folders into .minecraft folder
        move_list = ["shaderpacks", "resourcepacks", "mods", "config"]
        for item in os.listdir(os.getcwd()):
            if item in move_list:
                move(item, mmc_dotminecraft_path)

        
        if move_disabled_mods:
            os.chdir(disabled_mods_path)
            retain = [".gitkeep"] # Files that shouldn't be deleted
            try:
                # Moves disabled mods back.
                for item in os.listdir():
                    if item not in retain:
                        move(item, mods_path)
            except OSError as e:
                print(e)
            os.chdir(packwiz_path)
        
        
        make_archive("mcc-cache", 'zip', mmc_cache_path) # Creates mcc-cache.zip file based on mmc-cache folder.
        
        # Export Modrinth modpack using MMC method.
        if export_mmc_modrinth:
            print("[MMC] Exporting Modrinth...")
            args = (
                "mmc-export",
                "--input", mmc_input_path,
                "--format", "Modrinth",
                "--modrinth-search", "loose",
                "-o", export_path,
                "-c", mmc_config,
                "-v", pack_version,
                "--scheme", modpack_name + "-" + minecraft_version + "-{version}",
            ); subprocess.call(args, shell=True)
            print("[MMC] Modrinth exported.")

        # Export CurseForge modpack using MMC method.
        if export_mmc_curseforge:
            print("[MMC] Exporting CurseForge...")
            args = (
                "mmc-export",
                "--input", mmc_input_path,
                "--format", "CurseForge",
                "-o", export_path,
                "-c", mmc_config,
                "-v", pack_version,
                "--scheme", modpack_name + "-" + minecraft_version + "-{version}",
            ); subprocess.call(args, shell=True)
            print("[MMC] CurseForge exported.")
        
        if cleanup_cache:
            os.remove("mcc-cache.zip")
            clear_mmc_cache(mmc_cache_path)
            print("Cache cleanup finished.")
        
        os.chdir(packwiz_path)
        subprocess.call(f"{packwiz_exe_path} refresh", shell=True)
        
    elif refresh_only:
        subprocess.call(f"{packwiz_exe_path} refresh", shell=True)


if __name__ == "__main__":
    try:
        print("")
        main()
    except KeyboardInterrupt:
        print("Operation aborted by user.")
        exit(-1)
