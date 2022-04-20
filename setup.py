import os
from setuptools import setup 
import src.todo-cli as todo-cli

def man():
    home = os.path.expanduser("~")
    real_file = "/usr/share/man/man1/todo-cli"
    opt_file = home + "/todo-cli/todo-cli.1"
    if os.path.exists(real_file):
        os.system("man " + real_file)
    elif not os.path.exists('/usr/share/man/man1/todo-cli'):
        os.system("man -l " + opt_file)

setup(
       name="todo-cli",
       version="0.0.1",
       author="Alejandro Rosario",
       author_email="borkbork1031@gmail.com",
       description="A command line tool for managing your to-do lists and tasks",
       long_description=man(),
       package_dir={'': 'src'},
       long_description_content_type="text/troff",
       classifiers=[
           "todo-lists :: Python :: to-do lists",
           "Free Software :: Linux Compatible :: Open Source",
           "Organization :: Daemons :: Programming Language"
       ],
       packages=["todo-cli"],
       install_requires=["notify-send", "datetime", "pytest-shutil", "argparse"],
       entry_points={
           "console_scripts": [
               "todo-cli = todo-cli.todo-cli:main"
           ]
       },
       python_requires=">=3.9")


