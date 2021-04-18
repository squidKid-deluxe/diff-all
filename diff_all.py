"""
Simple script that iterates through two given directories and diffchecks them from each other.

colordiff is the only thing to be installed, everything else is standard python3.
"""

# Used to hash the directory's files
import hashlib
# Used to find each file in the directories
import os
# Used to execute the 'colordiff' command, as well as to install it, if needed.
from subprocess import call


def find_colordiff():
    """Check if colordiff, a required module for this program, is installed."""
    try:
        # If we can't access the colordiff help, it must be installed.
        call("colordiff --help".split())
        print("\033c")
    except ImportError:
        # Ask the user before installing things,
        #  so he/she does not freak out about sudo asking their password.
        print(
            "\033c"
            + "You are missing the module 'colordiff', which is required to use this program.\n"
            + "Press enter to install it using the following command:\n"
            + "sudo apt-get install colordiff"
        )
        input()
        # Install colordiff
        call("sudo apt-get install colordiff".split())


def hash_directory(path):
    """Give the hash of the directory or file path given."""
    # Create a digest object.
    digest = hashlib.sha256()
    # If the path given is that of a file...
    if os.path.isfile(path):
        # Open it...
        with open(path, "rb") as f_obj:
            while True:
                # ...and add it's data to the digest.
                buf = f_obj.read(1024 * 1024)
                if not buf:
                    break
                digest.update(buf)
    # Otherwise, since the path must then be that of a directory,
    #  iterate through the files in that directory.
    else:
        for root, _, files in os.walk(path):
            for names in files:
                file_path = os.path.join(root, names)
                # Hash the path and add to the digest to account for empty files/directories
                digest.update(hashlib.sha1(file_path[len(path):].encode()).digest())
                if os.path.isfile(file_path):
                    with open(file_path, "rb") as f_obj:
                        while True:
                            buf = f_obj.read(1024 * 1024)
                            if not buf:
                                break
                            digest.update(buf)

    # Return the hash.
    return digest.hexdigest()


def main():
    """Process that actually does the iterating throught the directories."""
    # Make sure that colordiff is installed.
    find_colordiff()

    # Ask the user for the directories to check
    directory1 = input(
        f"What should directory #1 (off of the current) be?\n\t{os.path.abspath(os.getcwd())}/"
    )
    directory1 = os.path.abspath(os.getcwd()) + "/" + directory1
    directory2 = input(
        f"What should directory #2 (off of the current) be?\n\t{os.path.abspath(os.getcwd())}/"
    )
    directory2 = os.path.abspath(os.getcwd()) + "/" + directory2

    # Hash all of the files in the first and second directory
    hashed_files_d_1 = {}
    for _, _, files in os.walk(directory1):
        for name in files:
            file = directory1 + "/" + name
            hashed_files_d_1[name] = hash_directory(file)
            print(file)
    hashed_files_d_2 = {}
    for _, _, files in os.walk(directory2):
        for name in files:
            file = directory2 + name
            hashed_files_d_2[name] = hash_directory(file)
            print(file)

    # Find which files the two directories have in common.
    checkable_hashes = []
    for key in hashed_files_d_2:
        try:
            hashed_files_d_1[key]
            checkable_hashes.append(key)
        except KeyError:
            pass

    # 'colordiff' all of those files.
    for file in checkable_hashes:
        if hashed_files_d_1[file] != hashed_files_d_2[file]:
            print("\033c")
            run = ["colordiff", "-y", "-W", "70"]
            run.append((directory1 + "/" + file))
            run.append((directory2 + "/" + file))
            call(run)
            input("\n\n\nPress enter to continue to the next file.")


if __name__ == "__main__":
    main()
