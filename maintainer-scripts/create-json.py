import os
import re
import copy
import json
import time
import random
import argparse
from datetime import datetime
from string import ascii_lowercase, digits

parser = argparse.ArgumentParser(
    description="script to read .cont files and generate a json")
parser.add_argument(
    "-k", "--key", type=str, help="Key number for filepath for the main content")
args = parser.parse_args()


class Post:
    def __init__(self, path, key):
        self.key = key
        self.path = path
        self.text = open(path, "r").read()
        self.attrs = {
            attr[3:-3]: None for attr in re.findall("<__.*__>", self.text)}
        # self.update_date = datetime.fromtimestamp(time.time())

    def sign(self):
        if 'PUBLISH_DATE' in self.attrs:
            self.create_date = float(self.text.split(
                '<__PUBLISH_DATE__>')[-1].strip('\n').split('\n')[0].strip())
            # self.create_date = datetime.fromtimestamp(float(self.create_date))
            # print(self.create_date)
        else:
            self.create_date = time.time()
            temp = open(self.path, "a")
            temp.write("\n<__PUBLISH_DATE__>")
            temp.write(f"\n{self.create_date}")

        if 'ID' in self.attrs:
            self.id = self.text.split('<__ID__>')[-1].strip('\n').strip()
            # print(self.op)
        else:
            self.id = ''.join(random.sample(ascii_lowercase+digits, 16))
            temp = open(self.path, "a")
            temp.write("\n<__ID__>")
            temp.write(f"\n{self.id}")
        self.update_map()

    def parse(self, verbose=False):
        self.sign()
        self.update_date = time.time()
        i = ''
        for k in self.attrs:
            self.attrs[k] = self.text.split(
                "<__"+k+"__>")[-1].strip('\n').strip()
            if i != '':
                self.attrs[i] = self.attrs[i].replace(
                    self.attrs[k], "").replace(f"<__{k}__>", "").strip('\n').strip()
            i = k

        if verbose:
            print("———————————————————————————————————")
            print(f"ID: \n{self.id}")
            print("———————————————————————————————————")
            print(f"LAST_UPDATED: \n{self.update_date}")
            print("———————————————————————————————————")
            print(f"PUBLISH_DATE: \n{self.create_date}")
            print("———————————————————————————————————")
            for k in self.attrs:
                print(f"{k}: \n{self.attrs[k]}")
                print("———————————————————————————————————")

    def update_map(self):
        map = json.load(open("map.json", "r"))
        map[self.key] = self.id
        print(map)
        json.dump(map, open("map.json", "w"))

    def dump(self):
        obj = copy.deepcopy(self.attrs)
        obj['PK'] = self.key
        obj['PUBLISH_DATE'] = datetime.fromtimestamp(self.create_date)
        obj['PUBLISH_DATE_STR'] = obj['PUBLISH_DATE'].strftime(
            "%B %-d, %Y")
        obj['PUBLISH_DATE'] = obj['PUBLISH_DATE'].__str__()
        obj['LAST_UPDATED'] = datetime.fromtimestamp(self.update_date)
        obj['LAST_UPDATED_STR'] = obj['LAST_UPDATED'].strftime(
            "%B %-d, %Y")
        obj['LAST_UPDATED'] = obj['LAST_UPDATED'].__str__()

        os.chdir("../raw")
        fname = f"{self.id}.json"
        temp = open(fname, "w")
        print(f"dumped file at {os.path.join(os.getcwd(), fname)} ...")
        json.dump(obj, temp)
        temp.close()


fname = f"../content/{args.key}.ctxt"
post = Post(fname, args.key)
# print(post.attrs)
# post.sign()
post.parse(verbose=True)
post.dump()
