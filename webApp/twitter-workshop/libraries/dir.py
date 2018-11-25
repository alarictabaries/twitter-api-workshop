# Operations with directories

import os
from os import listdir

# Return a list of files in a directory
def list_dir(dir, prefix):

    # Return the modification date of a file
    def get_mtime(name):
        path = os.path.join(dir, name)
        return os.path.getmtime(path)

    files = [f for f in listdir(dir) if f.startswith(prefix)]
    return sorted(files, key=get_mtime, reverse=True)


# Separate various files data to a list
def get_files_data(files):
    urls = []
    files_urls = []

    for file in files:
        file_s = file.split("_")
        file_short = file_s[6].split(".")
        url = "data_set?subject=" + file_s[1] + "&count=" + file_s[2] + "&language=" + file_s[3] + "&date=" + file_s[
            4] + "&hour=" + file_s[5] + "&seed=" + file_short[0]
        urls.append(url)

    for file, url in zip(files, urls):
        file_s = file.split("_")
        file_short = file_s[6].split(".")
        subject = file_s[1]
        count = file_s[2]
        language = file_s[3]
        if language == "fr":
            language = "French"
        elif language == "en":
            language = "English"
        date = file_s[4] + " " + file_s[5].replace("-", ":")
        seed = file_short[0]
        combined = [file, url, subject, count, language, date, seed]
        files_urls.append(combined)

    return files_urls
