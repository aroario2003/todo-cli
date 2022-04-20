# NAME

    **todo-cli** - A to-do list manager for the command line

# SYNOPSIS

    **todo-cli** \[**-cr** | **--create** todo_list] \[**-a** | **--add** todo_list todo_item] \[**-r** | **--remove** todo_list] 
    \[**-md** | **--mark-as-done** todo_list todo_item] \[**-mi** | **--mark-as-incomplete** todo_list todo_item]
    \[**-p** | **--print** todo_list] 
    \[**-c** | **--clear**] \[**-h** | **--help**] \[**-l** | **--list**] \[**-v** | **--version**]
    
# DESCRIPTION

    **todo-cli** is a command line to-do list manager. This tool is made to help people who predominatly 
    use the command line manage their schedule without having to leave the terminal and disrupt their 
    workflow. **todo-cli** will write to files in order to store the to-do lists made by the user.
    The tool will also read from files in order to display the items within a to-do list. **NOTE** this
    program does store files in the .local directory, however they can be deleted by using the **-r** or 
    **--remove** flags.
    
# OPTIONS
   
#### -h --help
Print the help message
    
#### -c --clear
Clear all to-do lists made by this program
    
#### -l --list
List all to-do lists made by this program 


#### -v --version 
Print the version of this program

#### -p --print 
Print the to-do list specified by the user as an argument

#### -md --mark-as-done 
Mark the to-do item specified by the user as done. This flag requires 
two arguments, the name of the to-do list and the item to mark as done.

#### -mi --mark-as-incomplete
Mark the to-do item specified by the user as incomplete. This flag requires
two arguments, the name of the to-do list and the item to mark as incomplete.

#### -a --add
Add the specified item to the specified to-do list. This flag requires two arguments,
the name of the to-do list and the item to add.
    
#### -r --remove
Delete a specified to-do list 

#### -cr --create
Create a new to-do list

#### -i --info
Print all info about items in a specified to-do list including date the item is due

#### -ad --add-date
Add a due date to a specified item in a spcified to-do list
    
# EXAMPLES

#### todo-cli -cr school
Create a new to-do list named school
     
#### todo-cli -a school math
Add math to the school to-do list

#### todo-cli -ad school math 04/18/2022
Add a due date to the math item in the school to-do list

#### todo-cli -i school
Print all info about the items in the school to-do list

#### todo-cli -mi school math
Mark the math item in the school to-do list as incomplete
 
#### todo-cli -md school math
Mark the math item in the school to-do list as done

#### todo-cli -p school
Print the current school to-do list
     
#### todo-cli -c
Clear all to-do lists
     
#### todo-cli -r school
Delete the school to-do list
     
#### todo-cli -l 
List all to-do lists
     
#### todo-cli -v 
Print the version of todo-cli
        
# AUTHOR

Alejandro Rosario borkbork1031@gmail.com
    
# SEE ALSO

todo-cli(1)
