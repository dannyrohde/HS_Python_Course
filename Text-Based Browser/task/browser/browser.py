import argparse
import json
import os
import re
from typing import List, Tuple

import httpx
from bs4 import BeautifulSoup, Tag
from colorama import init as colorama_init, Fore
from pydantic import BaseModel, AnyUrl, ValidationError

colorama_init()


# write your code here

class WebRequest(BaseModel):
    url: AnyUrl


FILE_NAME = "websites.json"
url_stack = []
tag: Tag
output: List[Tuple[str, List[str]]] = []

parser = argparse.ArgumentParser(description='Text based browser')
parser.add_argument('dir', metavar='directory', type=str, help='A file path where the websites are stored')
args = parser.parse_args()

path = getattr(args, "dir", "tb_tabs")

# Create target Directory if don't exist
if not os.path.exists(path):
    os.mkdir(path)

while True:
    url_input = input()

    if url_input == "exit":
        break
    elif url_input == "back":

        if url_stack:
            _ = url_stack.pop()
            url.url = url_stack.pop()
        else:
            continue

    else:

        try:
            url = WebRequest(url=url_input)
        except ValidationError as e:
            if e.errors()[0]["type"] == "value_error.url.scheme":
                url = WebRequest(url="https://" + url_input)

    if url and url.url:
        if url.url.host_type != "int_domain":
            resp = httpx.get(url.url)
            url_stack.append(url.url)

            soup = BeautifulSoup(resp.content, 'html.parser')
            # print(soup.get_text())
            for tag in soup.find_all(re.compile("^p$|^h\d$|^a$|^li$")):  # ^ul$|^ol$
                output.append((tag.name, [string for string in tag.stripped_strings]))

            for line in output:
                if line[0] == "a":
                    print(Fore.BLUE, *line[1], sep="")
                else:
                    print(*line[1])

            with open(path + "/" + FILE_NAME, "w+") as f:
                json.dump({url_input: output}, f)
        else:
            print("Error: Incorrect URL")
