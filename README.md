Contact_BookAdvanced Contact Book Manager
Name: Gaurav Kumar
Roll No: 2501940033
Date: 20 Nov 2025

Project Type: Python Command Line Application

# Description
This is my Python project for a Contact Management System. It runs in the terminal and allows users to store, manage, and search for contacts efficiently. Unlike a simple text file saver, this program uses CSV for storage, supports JSON exporting, and includes advanced features like Undo, Backups, and Duplicate Detection.

# Features
Add Contacts: Save names, phone numbers, emails, tags, and mark as favorite.

Validations: Automatically cleans phone numbers (removes dashes/spaces) and checks email format.

Search: Search by name, phone, or tag. Supports Regex (Regular Expressions) if you wrap the search in slashes (e.g., /^A/ for names starting with A).

Update & Delete: Edit existing contact details or remove them.

Import/Export:

Import contacts from other CSV files.

Export data to JSON or specific contacts to vCard (.vcf) format.

# Safety Features:

Undo: Accidentally deleted or changed something? Option 12 lets you undo the last save.

Backups: Automatically creates daily backups in the backups/ folder.

Error Logging: Crashes or file errors are saved to error_log.txt instead of stopping the program.

Merge Duplicates: Finds contacts with similar names (using difflib) and offers to merge them into one entry.

Requirements
Python 3.x

Standard libraries used: csv, json, os, shutil, re, datetime, difflib (No need to install anything with pip).

# How to Run
Make sure you have Python installed.

Open your terminal or command prompt.

Navigate to the folder containing the script.

Run the following command:

python contact_manager.py

(Replace contact_manager.py with whatever you named the script file)

File Structure
When you run the program, it will automatically create these files:

contacts.csv - The main database where contacts are stored.

contacts.json - Created if you choose the "Export to JSON" option.

error_log.txt - Stores error messages if something goes wrong.

backups/ - A folder containing timestamped copies of your CSV file.

.temp_data.json - A hidden file used for the "Undo" feature.

Usage Notes
Phone Numbers: The program tries to fix format errors. If you type (555) 123-4567, it saves as 5551234567.

Tags: You can add multiple tags separated by commas (e.g., Work, Friends, Gym).

Sorting: You can sort the list by Name or by Favorites in the View menu.