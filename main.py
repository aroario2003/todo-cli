#!/usr/bin/env python3

import os
import sys
from pathlib import Path
import argparse as ap
import shutil as sh
from datetime import date
from datetime import datetime
import re
import time
from threading import Thread as th
from notify import notification as notif

parser = ap.ArgumentParser()
parser.add_argument('-c', '--clear', action="store_true", help="Clear all to-do lists made by this program")
parser.add_argument('-p', '--print', metavar="todo-list", help="Print the specified to-do list")
parser.add_argument('-l', '--list', action="store_true", help="Lists all to-do lists that have been made")
parser.add_argument('-a', '--add', nargs=2, metavar=("todo-list", "todo-item"), help="Add to the to-do list")
parser.add_argument('-r', '--remove', metavar="todo-list", help="Remove the specified to-do list")
parser.add_argument('-v', '--version', action="store_true", help="Prints the version of the program")
parser.add_argument('-md', '--mark-as-done', nargs=2, metavar=("todo-list", "todo-item"), help="Mark a to-do list item as done")
parser.add_argument('-mi', '--mark-as-incomplete', nargs=2, metavar=("todo-list", "todo-item"), help="Mark a to-do list item as incomplete")
parser.add_argument('-cr', '--create', metavar="todo-list", help="Create a new to-do list")
parser.add_argument('-i', '--info', metavar="todo-list", help="List items in the specified to-do list and dates when they are due")
parser.add_argument('-ad', '--add-date', nargs=3, metavar=("todo-list", "todo-item", "due-date"), help="Add a due date to the specified to-do list item")
parser.add_argument('-t', '--time', metavar="interval", help="Set the amount of time before an item is due for the program to remind you")
parser.add_argument('-d', '--daemonize', action="store_true", help="Start a background process to remind you when certain to-do items are due")
args = parser.parse_args()

home = os.path.expanduser('~')
directory = home + "/.local/share/todo/"
version = "0.0.1"

def print_version():
    print(f"todo-cli {version}")

def create_todo(create):
    if not os.path.exists(directory):
        os.mkdir(directory)
    Path(directory + "todo-" + create + ".txt").touch()

def add_item(todo_list, todo_item):
    name = todo_list
    todo_list = "todo-" + name + ".txt"
    if not os.path.exists(directory):
        os.mkdir(directory)
    with open (directory + todo_list, "a") as f:
        f.write(todo_item + "\n")

def remove_list(todo_list):
    name = todo_list
    todo_list = "todo-" + name + ".txt"
    for file in os.walk(directory):
        for todo in file[2]:
            if todo == todo_list:
                os.remove(directory + todo)

# def set_interval(interval):

def compare_date(due_date) -> int:
    today = date.today().strftime("%m/%d/%Y")
    today = datetime.strptime(today, "%m/%d/%Y")
    due = datetime.strptime(due_date, "%m/%d/%Y")
    return abs((due - today).days)

def remind_if_due():
    todo_lists = os.listdir(directory)
    display = os.environ["DISPLAY"]
    for file in todo_lists:
        name_of_list = file.strip("todo-").strip(".txt")
        with open (directory + file, "r") as f:
            lines = f.readlines()
            for line in lines:
               pattern = re.compile('\d\d/\d\d/\d\d\d\d') 
               global result
               result = pattern.search(line)
               item = re.compile('[a-z]|[A-Z]')
               item_search = item.findall(line)
               final_item = "".join(item_search)
               result = result.group()
               if result:
                   if compare_date(result) == 1:
                       if display:
                           notif("todo-cli", f"Your to-do item {final_item} from the {name_of_list} to-do list is due tommorrow")
                       elif not display:
                           print("Entering no-display mode:\nThe script has detected that you are not in a GUI environment and will now send notifications to the console")
                           print(f"Your item {final_item} from the {name_of_list} to-do list is due tomorrow")
                   if compare_date(result) == 0:
                        if display: 
                            notif("todo-cli", f"Your to-do item {final_item} from the {name_of_list} to-do list is due today")
                        elif not display:
                            print("Entering no-display mode:\nThe script has detected that you are not in a GUI environment and will now send notifications to the console")
                            print(f"Your item {final_item} from the {name_of_list} to-do list is due today")

# def start_daemon():

def mark_as_done(todo_list, todo_item):
    name = todo_list
    todo_list = "todo-" + name + ".txt"
    with open (directory + todo_list, "r") as f:
        lines = f.readlines()
        for line in lines:
           if todo_item in line and not "✓ " in line:
                    newline = line.replace(line, "✓ " + line)
                    lines[lines.index(line)] = newline
    with open (directory + todo_list, "w") as f:
        f.writelines(lines)

def mark_as_incomplete(todo_list, todo_item):
    name = todo_list
    todo_list = "todo-" + name + ".txt"
    with open (directory + todo_list, "r") as f:
        lines = f.readlines()
        for line in lines:
            if todo_item in line and not "✓ " in line:
                newline = line.replace(line, "🗶 " + line)
                lines[lines.index(line)] = newline
    with open (directory + todo_list, "w") as f:
        f.writelines(lines)

def add_date(todo_list, todo_item, date_due):
    name = todo_list
    todo_list = "todo-" + name + ".txt"
    with open (directory + todo_list, "r") as f:
        lines = f.readlines()
        for line in lines:
            if todo_item in line:
                newline = line.replace(line, line.strip("\n") + " " + date_due)
                lines[lines.index(line)] = newline
    with open (directory + todo_list, "w") as f:
        f.writelines(lines)

def print_info(todo_list):
    name = todo_list
    todo_list = "todo-" + name + ".txt"
    with open (directory + todo_list, "r+") as f:
        lines = f.readlines()
        for line in lines:
            print(line)

def print_todo(todo_list):
    name = todo_list
    todo_list = "todo-" + name + ".txt"
    if not os.path.exists(directory + todo_list):
        print(f"{todo_list} does not exist")
    else:
        print(name + ":")
        with open (directory + todo_list, "r") as f:
            for line in f:
                print("\t" + re.sub('[0-9]|/', '', line))

def list_todo():
    print("\033[0;34m Todo-lists:\033[0m")
    for file in os.walk(directory):
        for todo_list in file[2]:
            print("\t" + "\uf061 " + todo_list.strip("todo-").strip(".txt"))

def clear_history():
    for file in os.listdir(directory):
        if os.path.getsize(directory + file) > 0:
            with open (directory + file, "w") as f:
                f.write("")

def main():
    if args.clear:
       clear_history()
    elif args.add:
        add_item(args.add[0], args.add[1])
    elif args.create:
        create_todo(args.create)
    elif args.print:
        print_todo(args.print)
    elif args.list:
        list_todo()
    elif args.remove:
        remove_list(args.remove)
    elif args.mark_as_done:
        mark_as_done(args.mark_as_done[0], args.mark_as_done[1])
    elif args.mark_as_incomplete:
        mark_as_incomplete(args.mark_as_incomplete[0], args.mark_as_incomplete[1])
    elif args.version:
        print_version()
    elif args.add_date:
        add_date(args.add_date[0], args.add_date[1], args.add_date[2])
    elif args.info:
        print_info(args.info)
    elif args.daemonize:
        remind_if_due()

if __name__ == '__main__':
    main()

   
