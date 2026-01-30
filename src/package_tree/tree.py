# -*- coding: utf-8 -*-

import argparse
import os
import pkg_resources
import six
import subprocess
import tempfile


class inf_loop(list):

    def __init__(self, *args):
        for x in args:
            self.append(x)

    def __iter__(self):
        while True:
            for x in list.__iter__(self):
                yield x


@six.python_2_unicode_compatible
class Style(dict):

    _colors = iter(inf_loop('#a6cee3', '#b2df8a', '#fb9a99', '#fdbf6f',
                            '#cab2d6', '#ffff99', '#1f78b4', '#33a02c',
                            '#e31a1c', '#ff7f00', '#6a3d9a', '#b15928'))

    def __init__(self, color=None):
        self['color'] = color or six.next(self._colors)
        self['shape'] = 'box'
        self['style'] = 'filled'

    def __str__(self):
        return ', '.join('%s="%s"' % x for x in self.items())


def get_site_package(path):
    folders = []
    while True:
        path, folder = os.path.split(path)
        if folder != "":
            folders.append(folder)
        else:
            break
    folders.reverse()
    try:
        idx = folders.index('site-packages')
        folders = folders[0:idx]
    except ValueError:
        pass
    return '/' + '/'.join(folders)


def format_label(pkg):
    lines = [pkg.key]
    lines.append('<font point-size="10">%s</font>'
                 % get_site_package(pkg.location))
    lines.append('<font point-size="10">%s</font>' % pkg.version)
    return '<br/>'.join(lines)


def get_graph():
    """
    Packages and dependencies in dot language.

    Return:
        List of lines
    """
    pkgs = pkg_resources.working_set
    deps = set()
    for pkg in pkgs:
        for requirement in pkg.requires():
            deps.add((pkg.key, requirement.key))

    result = []
    result.append("rankdir=LR;")

    styles = {}

    for pkg in sorted(pkgs, key=lambda x: x.key):
        site_package = get_site_package(pkg.location)
        if site_package not in styles:
            styles[site_package] = Style()
        result.append('"%s" [%s, label=<%s>]' % (
            pkg.key, styles[site_package], format_label(pkg))
        )
    for relation in sorted(deps):
        result.append('"%s" -> "%s";' % relation)

    return result


def write_dot_file(stream):
    """
    Write full dot script to stream.
    """
    stream.write("digraph G {\n")
    for l in get_graph():
        stream.write("    ")
        stream.write(l)
        stream.write("\n")
    stream.write("}\n")


def build(script_file, outfile, fmt="png"):
    """
    Invoke dot.
    """
    subprocess.call(['dot', '-T' + fmt], stdin=script_file, stdout=outfile)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Dependencies of python packages")
    parser.add_argument(
        'filename',
        help="Fichier de sortie")
    parser.add_argument(
        '-f', '--format',
        choices=['png', 'svg', 'dot'],
        default='png',
        help='Output format')
    return parser.parse_args()


def main():
    args = parse_args()
    if args.format == 'dot':
        with open(args.filename, 'w') as outfile:
            write_dot_file(outfile)
    else:
        with tempfile.TemporaryFile('w') as script_file, \
             open(args.filename, 'wb') as outfile:
            write_dot_file(script_file)
            script_file.seek(0)
            build(script_file, outfile, args.format)
