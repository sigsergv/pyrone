"""Extend markdown with subscript feature

Replaces "C~0~" with "C<sub>0</sub>"

based on https://github.com/jambonrose/markdown_subscript_extension
"""

from markdown import Extension
from markdown.inlinepatterns import SimpleTagPattern

SUBSCRIPT_RE = r"(\~)([^\~]+)\2"


def makeExtension(*args, **kwargs):
    """register extension"""
    return SubscriptExtension(*args, **kwargs)


class SubscriptExtension(Extension):
    def extendMarkdown(self, md):
        """Insert 'subscript' pattern before 'not_strong' pattern."""
        md.inlinePatterns.add(
            "subscript", SimpleTagPattern(SUBSCRIPT_RE, "sub"), "<not_strong"
        )
