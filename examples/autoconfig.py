#!./python3
from access import Access
import jinja2
import re
import os

def render_all_template(**args):
    print **args

loader = jinja2.FileSystemLoader('.')
class RelEnvironment(jinja2.Environment):
    """Override join_path() to enable relative template paths."""
    def join_path(self, template, parent):
        return os.path.join(os.path.dirname(parent), template)
env = RelEnvironment(loader=loader)

access=Access()
curr=access.curr

datas=open("data.dotline").read().splitlines()

pair_list=[list(map(lambda x:x.strip(),i.split('='))) for i in datas if '=' in i]
for pair in pair_list:
    access.set(pair[0],pair[1])

render_all_template(curr=curr)