import os
import json
import argparse
from colors import color
from pprint import pprint
from datetime import datetime


parser = argparse.ArgumentParser(
    description="script to read .cont files and generate a json")
parser.add_argument(
    "-p", "--path", type=str, default="../raw", help="Path of folder containing raw json data")
parser.add_argument(
    "-t", "--templates", type=str, default="../templates", help="Path of folder containing html templates")
args = parser.parse_args()

CURRENT_DIR = os.getcwd()
RAW = os.path.realpath(args.path)
TEMPLATES = os.path.realpath(args.templates)


def render(template, context):
    for k in context:
        template = template.replace("{{ "+k+" }}", str(context[k]))

    return template.strip('\n').strip()


print(f"reading templates from {TEMPLATES} ...")
tag = open(f"{TEMPLATES}/tag.html").read()
post = open(f"{TEMPLATES}/post.html").read()
feed = open(f"{TEMPLATES}/feed.html").read()
post_excerpt = open(f"{TEMPLATES}/post_excerpt.html").read()
post_preview = open(f"{TEMPLATES}/post_preview.html").read()
map = json.load(open("map.json", "r"))

print(f"reading raw post data from {RAW} ...")
contexts = {}
feeds = {}
for item in os.listdir(RAW):
    context = json.load(open(os.path.join(args.path, item), "r"))
    contexts[context['PK']] = context
    if context['CATEGORY'] not in feeds:
        feeds[context['CATEGORY']] = [context]
    else:
        feeds[context['CATEGORY']].append(context)
# print(contexts)
for k in contexts:
    if int(contexts[k]['NEXT_POST']) > 0:
        contexts[k]['NEXT_POST_URL'] = contexts[contexts[k]
                                                ['NEXT_POST']]['POST_URL']
        print(contexts[k]['NEXT_POST_URL'])
        contexts[k]['NEXT_POST_TITLE'] = contexts[contexts[k]
                                                  ['NEXT_POST']]['TITLE']
    else:
        contexts[k]['NEXT_POST_TITLE'] = "No more posts"
        contexts[k]['NEXT_POST_URL'] = "#"

    if int(contexts[k]['PREVIOUS_POST']) > 0:
        contexts[k]['PREVIOUS_POST_URL'] = contexts[contexts[k]
                                                    ['PREVIOUS_POST']]['POST_URL']
        print(contexts[k]['PREVIOUS_POST_URL'])
        contexts[k]['PREVIOUS_POST_TITLE'] = contexts[contexts[k]
                                                      ['PREVIOUS_POST']]['TITLE']
    else:
        contexts[k]['PREVIOUS_POST_TITLE'] = "No more posts"
        contexts[k]['PREVIOUS_POST_URL'] = "#"

    temp = ""
    for pk in contexts[k]['PREVIEWS'].split(','):
        pk = pk.strip()
        temp += render(post_preview, contexts[pk])+'\n'
    contexts[k]['PREVIEWS'] = temp

    temp = ""
    for t in contexts[k]['TAGS'].split(','):
        t = t.strip()
        temp += render(tag, {'TAG': t, 'TAG_LOWERCASE': t.lower()})+'\n'
    contexts[k]['TAGS'] = temp.strip()[:-1]

    fname = f"{contexts[k]['CATEGORY'].replace(' ' ,'-')}/{contexts[k]['POST_URL']}"
    fname = f"../{fname}"
    fname = os.path.realpath(fname)
    open(fname, "w").write(render(post, contexts[k]))
    print(
        color(f"html file generated at {fname} ...", fg='blue', style='bold'))
    # open(context['TITLE'])
for k in feeds:
    # fname =
    unprintStrptimeFmt = "%Y-%m-%d %H:%M:%S.%f"
    fname = f"../{k.replace(' ','-')}/index.html"
    fname = os.path.realpath(fname)
    posts = {datetime.strptime(
        i['PUBLISH_DATE'], unprintStrptimeFmt).timestamp(): i for i in feeds[k]}

    posts = sorted(posts.items(), key=lambda x: x[0], reverse=True)
    posts = [v for k, v in posts]
    context = {}
    context['PREVIEWS'] = posts[0]['PREVIEWS']
    context['CATEGORY'] = k.title()

    temp = ""
    for post in posts:
        temp += render(post_excerpt, post) + '\n'
    context['EXCERPTS'] = temp

    open(fname, "w").write(render(feed, context))
    print(
        color(f"html file generated at {fname} ...", fg='blue', style='bold'))
