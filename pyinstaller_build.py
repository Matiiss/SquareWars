import PyInstaller.__main__ as pyi
import os
import shutil
import platform

# get ready for some super hax code
pyi.run([
    "run.py",
    "-n",
    "SquareWars",
    "-y"
])

export_direction = "SquareWarsBuild"

shutil.rmtree(export_direction, ignore_errors=True)

shutil.copytree("dist/SquareWars", export_direction)
shutil.copytree("src/res", f"{export_direction}/src/res", dirs_exist_ok=True)
shutil.make_archive(f"SquareWars-{platform.system()}", "zip", export_direction)
