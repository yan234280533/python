#!/usr/bin/env/python
#
# More of a reference of using jinaj2 without actual template files.
# This is great for a simple output transformation to standard out.
#
# Of course you will need to "sudo pip install jinja2" first!
#
# I like to refer to the following to remember how to use jinja2 :)
# http://jinja.pocoo.org/docs/templates/
#

from jinja2 import Environment
from jinja2 import Environment, PackageLoader, select_autoescape
import jinja2
import re
import os

HTML = """
<html>
<head>
<title>{{ title }}</title>
</head>
<body>
Hello.
</body>
</html>
"""
loader = jinja2.FileSystemLoader('.')
class RelEnvironment(jinja2.Environment):
    """Override join_path() to enable relative template paths."""
    def join_path(self, template, parent):
        return os.path.join(os.path.dirname(parent), template)
env = RelEnvironment(loader=loader)


def print_html_doc():
    env = Environment(
        loader=jinja2.FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('mytemplate.html')

    print("11111")

    print("%s" % (template.render({"title":'Hellow Gist from GutHub',"name":'dddddd'})) )

if __name__ == '__main__':
    print_html_doc()