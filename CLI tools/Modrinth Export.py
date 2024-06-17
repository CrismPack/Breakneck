import os
import json
import subprocess
from typing import IO
from pathlib import Path
from zipfile import ZipFile
from shutil import unpack_archive

import toml  # pip install toml


#user_path = os.path.expanduser("D:")
git_path = "D:\\GitHub Projects\\Breakneck\\"
minecraft_version = "1.21"
packwiz_path = git_path + "Packwiz\\" + minecraft_version + "\\"
#packwiz_exe_path = os.path.join("..", "packwiz.exe")
packwiz_exe_path = os.path.expanduser("~") + "\\go\\bin\\packwiz.exe"

# cf_zip_path = ""
pack_version = "4.0.0_pre2"

refresh_only = False
mmc_export_modrinth_export = True




def main():
    os.chdir(packwiz_path)
    
    # Export Modrinth pack and manifest via mmc-export method
    if mmc_export_modrinth_export and not refresh_only:
        
        subprocess.call(f"{packwiz_exe_path} cf export", shell=True)
        cf_zip = f"Breakneck-{minecraft_version}-{pack_version}.zip"
        print("[Debug]: " + cf_zip)
        
        #mmc_zip_root = str(Path(cf_zip).parents[0])
        #print("[Debug]: " + mmc_zip_root)
        
        mmc_config = git_path + "Packwiz\\mmc-export.toml"
        
        args = (
            "mmc-export",
            "--input", "Breakneck-1.21-4.0.0_pre2.zip",#cf_zip,
            "--format", "Modrinth",
            "--modrinth-search", "loose",
            #"-o", "\\",
            "-c", mmc_config,
            "-v", pack_version,
            "--scheme", "{name}-{version}",
        ); subprocess.call(args, shell=True)
    
    elif refresh_only:
        subprocess.call(f"{packwiz_exe_path} refresh", shell=True)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Operation aborted by user.")
        exit(-1)
