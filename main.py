#!/usr/bin/env python3

import os
import re
import smtplib
import time
import json
import argparse as ap
import shutil as sh
from pathlib import Path
from datetime import date, datetime
from threading import Thread
from tabulate import tabulate 
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
parser.add_argument('-ri', '--remove-item', nargs=2, metavar=('todo-list', 'todo-item'), help="Remove a to-do list item")
parser.add_argument('-cr', '--create', metavar="todo-list", help="Create a new to-do list")
parser.add_argument('-i', '--info', metavar="todo-list", help="List items in the specified to-do list and dates when they are due")
parser.add_argument('-ad', '--add-date', nargs=3, metavar=("todo-list", "todo-item", "due-date"), help="Add a due date to the specified to-do list item")
parser.add_argument('-d', '--daemonize', action="store_true", help="Start a background process to remind you when certain to-do items are due")
parser.add_argument('-me', '--message', action="store_true", help="Start a background process that checks if something is due in the interval specified and send a sms message if so")
parser.add_argument('-pt', '--print-table', action="store_true", help="Print a table of all items with information about each")
args = parser.parse_args()

HOME = os.path.expanduser('~')
DIRECTORY = HOME + "/.local/share/todo/"
VERSION = "0.0.1"
CONFIGURATION = HOME + "/.config/todo-cli/config.json"
CARRIER_DICT = {
        "verizon": "vtext.com",
        "tmobile": "tmomail.net",
        "sprint": "messaging.sprintpcs.com",
        "at&t": "txt.att.net",
        "boost": "smsmyboostmobile.com",
        "cricket": "sms.cricketwireless.net",
        "uscellular": "email.uscc.net",
        }

with open (CONFIGURATION, "r") as f:
    config = json.load(f)
    NOTIFICATION_INTERVAL = config["config"]["todo-cli"]["notif-interval"]
    CHECK_INTERVAL = config["config"]["todo-cli"]["check-interval"]
    COMPARE_UNIT = config["config"]["todo-cli"]["compare-unit"]
    EMAIL = config["config"]["todo-cli"]["email-address"]
    EMAIL_PASS = config["config"]["todo-cli"]["email-password"]
    PHONE_NUMBER = config["config"]["todo-cli"]["phone-number"]
    PHONE_CARRIER = config["config"]["todo-cli"]["phone-carrier"]

def print_version() -> None:
    print(f"todo-cli {VERSION}")

def create_todo(create) -> None:
    if not os.path.exists(DIRECTORY):
        os.mkdir(DIRECTORY)
    Path(DIRECTORY + "todo-" + create + ".txt").touch()

def add_item(todo_list: str, todo_item: str) -> None:
    name = todo_list
    todo_list = "todo-" + name + ".txt"
    if not os.path.exists(DIRECTORY):
        os.mkdir(DIRECTORY)
    with open (DIRECTORY + todo_list, "a") as f:
        f.write(todo_item + "\n")

def remove_list(todo_list: str) -> None:
    name = todo_list
    todo_list = "todo-" + name + ".txt"
    for file in os.walk(DIRECTORY):
        for todo in file[2]:
            if todo == todo_list:
                os.remove(DIRECTORY + todo)

def convert_interval(interval) -> int:
    number = re.compile('[0-9]')
    amount = number.search(interval)
    amount = amount.group()
    letter = re.compile('[a-z]')
    unit = letter.search(interval)
    unit = unit.group()
    if unit == "s":
        return int(amount)
    elif unit == "m":
        return int(amount) * 60
    elif unit == "h":
        return int(amount) * 3600
    elif unit == "d":
        return int(amount) * 86400
    elif unit == "w":
        return int(amount) * 604800
    elif unit == "M":
       return int(amount) * 2628000 

def compare_date(due_date, unit: str = COMPARE_UNIT) -> int:
    today = date.today().strftime("%m/%d/%Y")
    today = datetime.strptime(today, "%m/%d/%Y")
    due = datetime.strptime(due_date, "%m/%d/%Y")
    if unit == "minute":
        return (due - today).total_seconds() // 60
    elif unit == "hour":
        return (due - today).days * 24 + (due - today).seconds // 3600
    elif unit == "day" or unit is None:
        return (due - today).days 
    elif unit == "week":
        return (due - today).days // 7
    elif unit == "month":
        return (due - today).days // 30
       
def remind_if_due() -> None:
    display = os.environ["DISPLAY"] 
    todo_lists = os.listdir(DIRECTORY)
    for file in todo_lists:
        name_of_list = file.strip("todo-").strip(".txt")
        with open (DIRECTORY + file, "r") as f:
            lines = f.readlines()
            for line in lines:
               if "✓ " not in line:
                    pattern = re.compile('\d\d/\d\d/\d\d\d\d') 
                    result = pattern.search(line)
                    item = re.compile('[a-z]|[A-Z]|\s')
                    item_search = item.findall(line)
                    final_item = "".join(item_search)
                    if result is not None:
                         result = result.group()
                    if result:
                        if compare_date(result, unit = COMPARE_UNIT) == int(NOTIFICATION_INTERVAL):
                            if display:
                                 notif("todo-cli", f"Your to-do item {final_item}from the {name_of_list} to-do list is due in " + str(NOTIFICATION_INTERVAL) + " " + COMPARE_UNIT + "(s)")
                            elif not display:
                                 print("Entering no-display mode:\nThe script has detected that you are not in a GUI environment and will now send notifications to the console")
                                 print(f"Your item {final_item}from the {name_of_list} to-do list is due tomorrow")
                        elif compare_date(result, unit = COMPARE_UNIT) == 0:
                             if display: 
                                 notif("todo-cli", f"Your to-do item {final_item}from the {name_of_list} to-do list is due today")
                             elif not display:
                                print("Entering no-display mode:\nThe script has detected that you are not in a GUI environment and will now send notifications to the console")
                                print(f"Your item {final_item}from the {name_of_list} to-do list is due today")
                        elif compare_date(result, unit = COMPARE_UNIT) < 0:
                                print("hello", end='')
    time.sleep(convert_interval(CHECK_INTERVAL))

def send_sms_if_due() -> None:
    todo_lists = os.listdir(DIRECTORY)
    for file in todo_lists:
        name_of_list = file.strip("todo-").strip(".txt")
        with open (DIRECTORY + file, "r") as f:
            lines = f.readlines()
            for line in lines:
               pattern = re.compile('\d\d/\d\d/\d\d\d\d') 
               result = pattern.search(line)
               item = re.compile('[a-z]|[A-Z]|\s')
               item_search = item.findall(line)
               final_item = "".join(item_search)
               if result is not None:
                    result = result.group()
               if result:
                   if compare_date(result, unit = COMPARE_UNIT) == int(NOTIFICATION_INTERVAL):
                        try:
                            sms_server = smtplib.SMTP("smtp.gmail.com", 587)
                            sms_server.starttls()
                            sms_server.login(EMAIL, EMAIL_PASS)
                            sms_body = (f"From: {EMAIL}\nTo: {PHONE_NUMBER}\n\nThis is the todo-cli reminder system: "
                            f"Your to-do item {final_item}from the {name_of_list} to-do list is due in " + str(NOTIFICATION_INTERVAL) + " " + COMPARE_UNIT + "(s)")
                            sms_server.sendmail(EMAIL, PHONE_NUMBER + "@" + CARRIER_DICT[PHONE_CARRIER], sms_body)
                            sms_server.close()
                        except:
                            print("Error: unable to send text")
    time.sleep(convert_interval(CHECK_INTERVAL))

def start_notification_daemon() -> None:
    while True:
        reminder = Thread(target=remind_if_due, daemon=True)
        reminder.start()
        reminder.join()
        
def start_message_daemon() -> None:
    while True:
        message_reminder = Thread(target=send_sms_if_due, daemon=True)
        mesage_reminer.start()
        message_reminder.join()

def print_table():
    table = [['list name', 'item', 'due date', 'is done']]
    todo_lists = os.listdir(DIRECTORY)
    for file in todo_lists:
        with open (DIRECTORY + file, "r") as f:
            lines = f.readlines()
            for line in lines:
                date_pattern = re.compile('\d\d/\d\d/\d\d\d\d')
                date_result = date_pattern.search(line)
                if date_result:
                    date = date_result.group()
                else:
                    date = "N/A"
                item_pattern = re.compile('[a-z]|[A-Z]|\s')
                item_result = item_pattern.findall(line)
                item = "".join(item_result)
                if "✓" in line:
                    is_done = True
                elif "🗶 " in line:
                    is_done = False
                else:
                    is_done = False
                table.append([file.strip("todo-").strip(".txt"), item, date, is_done])
    print(tabulate(table, headers='firstrow', tablefmt='fancy_grid'))
                 

def mark_as_done(todo_list: str, todo_item: str) -> None:
    name = todo_list
    todo_list = "todo-" + name + ".txt"
    with open (DIRECTORY + todo_list, "r") as f:
        lines = f.readlines()
        for line in lines:
           if todo_item in line and not "✓ " in line:
                    newline = line.replace(line, "✓ " + line)
                    newline = newline.replace("🗶 ", "")
                    lines[lines.index(line)] = newline
           elif todo_item in line and "🗶 " in line:
                    newline = line.replace(line, "✓ " + line)
                    lines[lines.index(line)] = newline
           elif todo_item in line and "✓ " in line:
                    print("This item is already marked as done")
    with open (DIRECTORY + todo_list, "w") as f:
        f.writelines(lines)

def mark_as_incomplete(todo_list: str, todo_item: str) -> None:
    name = todo_list
    todo_list = "todo-" + name + ".txt"
    with open (DIRECTORY + todo_list, "r") as f:
        lines = f.readlines()
        for line in lines:
            if todo_item in line and not "✓ " in line:
                newline = line.replace(line, "🗶 " + line)
                lines[lines.index(line)] = newline
            elif todo_item in line and "✓ " in line:
                print("This item has been marked as done")
    with open (DIRECTORY + todo_list, "w") as f:
        f.writelines(lines)

def add_date(todo_list: str, todo_item: str, date_due) -> None:
    name = todo_list
    todo_list = "todo-" + name + ".txt"
    with open (DIRECTORY + todo_list, "r") as f:
        lines = f.readlines()
        for line in lines:
            if todo_item in line:
                newline = line.replace(line, line.strip("\n") + " " + date_due + "\n")
                lines[lines.index(line)] = newline
    with open (DIRECTORY + todo_list, "w") as f:
        f.writelines(lines)

def print_info(todo_list: str) -> None:
    name = todo_list
    todo_list = "todo-" + name + ".txt"
    with open (DIRECTORY + todo_list, "r+") as f:
        lines = f.readlines()
        for line in lines:
            print(line)

def print_todo(todo_list: str) -> None:
    name = todo_list
    todo_list = "todo-" + name + ".txt"
    if not os.path.exists(DIRECTORY + todo_list):
        print(f"{todo_list} does not exist")
    else:
        print(name + ":")
        with open (DIRECTORY + todo_list, "r") as f:
            for line in f:
                print("\t" + re.sub('[0-9]|/', '', line))

def list_todo() -> None:
    print("\033[0;34m Todo-lists:\033[0m")
    for file in os.walk(DIRECTORY):
        for todo_list in file[2]:
            print("\t" + "\uf061 " + todo_list.strip("todo-").strip(".txt"))

def clear_history() -> None:
    for file in os.listdir(DIRECTORY):
        if os.path.getsize(DIRECTORY + file) > 0:
            with open (DIRECTORY + file, "w") as f:
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
        start_notification_daemon()
    elif args.message:
        send_sms_if_due()
    elif args.print_table:
        print_table()
    else:
        print("No arguments given please supply an argument. For help do 'todo-cli -h'")
   
if __name__ == '__main__':
    main()

   
