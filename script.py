#!/usr/bin/env python3
import sys
import keyring
from py_setenv import setenv
from git import Repo
import subprocess
import os

os.system('')

MGIT_ENV = "MGIT_ENV"
MGIT_SERVICE = "MGIT_SERVICE"

repo = Repo(os.getcwd())


def run_git_command(cmd):
    try:
        result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, universal_newlines=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return e.stderr


def getHelp(showGreetings=True):
    if showGreetings:
        print(
            f"\033[1m\033[4m\033[35m\033[5m\n\t\t\t\tWelcome to MultiGit\t\t\t\033[0m")
        print()
    print(f"\033[1m\033[36mset <username> <token>         \033[0m=>       to set git username and password")
    print(
        f"\033[1m\033[36mget                              \033[0m=>       to get all users")
    print(
        f"\033[1m\033[36mremove <username>                \033[0m=>       to get all users")
    print(f"\033[1m\033[36mpush                             \033[0m=>       to push to github using account")
    print(f"\033[1m\033[36mpull                             \033[0m=>       to pull from github using account")
    print(
        f"\033[1m\033[36mhelp                             \033[0m=>       to show help menu")
    print()


def wrongArgError(msg="\033[1m\033[4m\033[31m\033[3m\nError: Invalid Sequence of argument or argument do not exist! Please check the Arguments from Following:\n\033[0m"):
    print(msg)
    getHelp(False)


def add_credentials(username, password):
    var_value = setenv(MGIT_ENV, user=True, suppress_echo=True)
    if len(var_value) == 0:
        var_to_set = f"|{username}"
        setenv(MGIT_ENV, var_to_set, user=True, suppress_echo=True)
    else:
        if (username not in var_value):
            var_to_set = f"{var_value}|{username}"
            setenv(MGIT_ENV, var_to_set, user=True, suppress_echo=True)
    keyring.set_password(MGIT_SERVICE, username, password)


def get_credentials():
    var_value = setenv(MGIT_ENV, user=True, suppress_echo=True)
    if len(var_value) == 0:
        print("No User Found!")
    else:
        counter = 1
        userList = var_value.split("|")
        numUser = 0
        newUserList = []
        for i in userList:
            if len(i) != 0:
                newUserList.append(i)
                numUser += 1
        print(f"{numUser} Users Found!\n")
        for i in newUserList:
            print(f"{counter}) {i}")
            counter += 1


def remove_credentials(username):
    var_value = setenv(MGIT_ENV, user=True, suppress_echo=True)
    if len(var_value) == 0:
        print("No User Found!")
    elif username not in var_value:
        print("No User Exist with provided username!")
    else:
        new_var_value = var_value.split(f"|{username}")
        if len(new_var_value[0]) == 0 and len(new_var_value[1]) == 0:
            setenv(MGIT_ENV, "", user=True, suppress_echo=True)
        elif len(new_var_value[0]) != 0 and len(new_var_value[1]) == 0:
            setenv(MGIT_ENV, new_var_value[0], user=True, suppress_echo=True)
        elif len(new_var_value[0]) == 0 and len(new_var_value[1]) != 0:
            setenv(MGIT_ENV, new_var_value[1], user=True, suppress_echo=True)
        elif len(new_var_value[0]) != 0 and len(new_var_value[1]) != 0:
            setenv(
                MGIT_ENV, new_var_value[0] + new_var_value[1], user=True, suppress_echo=True)
        print(f"User {username} deleted successfully!")
        keyring.delete_password(MGIT_SERVICE, username)


def getUserInputForAction(action):
    if (len(repo.remotes) == 0):
        print(
            "\033[1m\033[4m\033[31m\033[3m\nError: No Remote is set! Please publish the repo first.\n\033[0m")
        return
    get_credentials()
    user = input(
        "\nPlease make selection by entering a number to perform action using the user: ")
    print()
    if (str.isnumeric(user)):
        var_value = setenv(MGIT_ENV, user=True, suppress_echo=True)
        userList = var_value.split("|")
        numUser = 0
        newUserList = []
        for i in userList:
            if len(i) != 0:
                newUserList.append(i)
                numUser += 1
        if (int(user) > numUser):
            print(
                "\033[1m\033[4m\033[31m\033[3m\nError: Argument Out of Bounds! Please enter a number from the list.\n\033[0m")
        else:
            creds = keyring.get_credential(
                MGIT_SERVICE, newUserList[int(user) - 1])
            rmtUrl = "https://" + creds.username + ":" + creds.password + "@" + \
                repo.remotes[0].config_reader.get("url").split("https://")[1]
            if (action == "push"):
                branch = run_git_command("git rev-parse --abbrev-ref HEAD")
                resp = run_git_command(f"git push --set-upstream {rmtUrl} {branch}")
                print(resp)
                # print(f"git push {rmtUrl} {branch}")
            else:
                resp = run_git_command(f"git pull {rmtUrl}")
                print(resp)
    else:
        print(
            "\033[1m\033[4m\033[31m\033[3m\nError: Invalid Positional Argument! Argument must be a number.\n\033[0m")


if __name__ == "__main__":
    argLen = len(sys.argv)
    if argLen == 1:
        getHelp()
    elif argLen == 2:
        arg2 = sys.argv[1]
        if arg2 == "help":
            getHelp()
        elif arg2 == "pull":
            getUserInputForAction("pull")
        elif arg2 == "push":
            getUserInputForAction("push")
        elif arg2 == "get":
            get_credentials()
        else:
            wrongArgError()
    elif argLen == 3:
        arg2 = sys.argv[1]
        arg3 = sys.argv[2]
        if arg2 == "remove":
            remove_credentials(arg3)
        else:
            wrongArgError()
    elif argLen == 4:
        arg2 = sys.argv[1]
        arg3 = sys.argv[2]
        arg4 = sys.argv[3]
        if arg2 == "set":
            add_credentials(arg3, arg4)
            print(f"Added user {arg3}!")
        else:
            wrongArgError()
    else:
        wrongArgError()
