import os
import shutil

os.system("python3 -m pygbag --archive src/main.py")

shutil.move("src/build/web.zip", "web.zip")
shutil.rmtree("src/build")