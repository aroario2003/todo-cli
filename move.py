import os

home = os.path.expanduser("~")

def setup():
    print("setting up...")
    os.system("cp " + home + " /todo-cli/src/todo-cli/main.py " + home + " /.local/bin/todo-cli")
    print("script installed .local/bin")
