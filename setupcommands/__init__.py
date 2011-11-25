# -*- coding: utf-8 -*-
"""
This package contains additional commands for setuptools script
"""
import os
import re
import codecs
import time, datetime
from setuptools import Command
from babel.messages.pofile import read_po
import logging

log = logging.getLogger(__name__)

def write_js(fileobj, catalog, use_fuzzy=False):
    """
    Write a catalog to specified file-like object
    """
    messages = list(catalog)
    if not use_fuzzy:
        messages[1:] = [m for m in messages[1:] if not m.fuzzy]
    messages.sort()
    ids = strs = ''
    jss = list()

    for message in messages:
        # For each string, we need size and file offset.  Each string is NUL
        # terminated; the NUL does not count into the size.
        if message.pluralizable:
            msgid = '\x00'.join([
                msgid.encode(catalog.charset) for msgid in message.id
            ])
            msgstrs = []
            for idx, string in enumerate(message.string):
                if not string:
                    msgstrs.append(message.id[min(int(idx), 1)])
                else:
                    msgstrs.append(string)
            msgstr = ''.join([
                msgstr.encode(catalog.charset) for msgstr in msgstrs
            ])
        else:
            msgid = message.id.encode(catalog.charset)
            if not message.string:
                msgstr = message.id.encode(catalog.charset)
            else:
                msgstr = message.string.encode(catalog.charset)
                
        if msgid != '' and msgstr != msgid:
            # escape msgstr
            msgstr = msgstr.replace("'", "\\'")
            jss.append("'%s': '%s'" % (msgid, msgstr))
            
        #print msgid, msgstr
    js = "Ext.ns('Pyrone.tr');\n\nPyrone.tr = {\n"
    js += ',\n'.join(jss)
    js += "\n};\n"
    fileobj.write(js)
    
class ExtractMessagesJs(Command):
    description = 'extract javascript translation strings from the javascript source files'
    user_options = [ 
        ('input-dirs', 'i', 'input directories') 
        ]
    
    output_file = None
    
    """
    comma separated list of input directories
    """
    input_dirs = []
    
    def initialize_options(self):
        """
        init options
        """
        pass
    
    def finalize_options(self):
        """
        finalize options
        """
        pass
    
    def run(self):
        """
        runner
        """
        # find all *.js files in the directory self.input_dirs
        js_files = []
        for root, dirs, files in os.walk(self.input_dirs):
            for fn in files:
                if fn.endswith('.js'):
                    js_files.append(os.path.join(root, fn))
                    
        # now scan js_files for tr() strings
        tr_re = re.compile("tr\('([0-9A-Z_]+)'\)");
        keys = dict()
        
        for fn in js_files:
            fp = open(fn, 'r')
            text = fp.read()
            fp.close()
            
            mp = tr_re.findall(text)
            for k in mp:
                keys[k] = True
                
        # create .pot-file
        pot_header_template = '''# Translations template for pyrone.
# Copyright (C) 2011 ORGANIZATION
# This file is distributed under the same license as the pyrone project.
# FIRST AUTHOR <EMAIL@ADDRESS>, 2011.
#
#, fuzzy
msgid ""
msgstr ""
"Project-Id-Version: pyrone 0.2.3\\n"
"Report-Msgid-Bugs-To: EMAIL@ADDRESS\\n"
"POT-Creation-Date: %(now)s\\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n"
"Language-Team: LANGUAGE <LL@li.org>\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=utf-8\\n"
"Content-Transfer-Encoding: 8bit\\n"
"Generated-By: pyrone setup command\\n"
'''
        mytz="%+4.4d" % (time.timezone / -(60*60) * 100) # time.timezone counts westwards!
        now = datetime.datetime.now()
        pot_header = pot_header_template % dict(now=now.strftime('%Y-%m-%d %H:%M') + mytz)
        
        fp = codecs.open(self.output_file, 'w', encoding='utf-8')
        fp.write(pot_header)
        
        for k,v in keys.iteritems():
            fp.write('\n#: file\nmsgid "%s"\nmsgstr ""\n' % k);
        fp.close()
        
class CompileCatalogJs(Command):
    description = 'extract javascript translation strings from the javascript source files'
    user_options = [ 
        ('input-file', 'i', 'input directories'),
        ('directory', 'd', 'path to base directory containing the catalogs') 
        ]
    
    out_directory = None
    input_file = None
    directory = None
    domain = None
    statistics = None
    use_fuzzy = False
    
    def initialize_options(self):
        """
        init options
        """
        pass
    
    def finalize_options(self):
        """
        finalize options
        """
        pass
    
    def run(self):
        """
        compile .po file into the javascript file
        """
        #print self.locale
        po_files = list()
        js_files = list()
        
        # code is based on Babel (babel/messages/frontend.py)
        for locale in os.listdir(self.directory):
            po_file = os.path.join(self.directory, locale,
               'LC_MESSAGES', self.domain + '.po')
            if os.path.exists(po_file):
                po_files.append((locale, po_file))
                js_files.append(os.path.join(self.out_directory,
                    locale + '.js'))
                
        for idx, (locale, po_file) in enumerate(po_files):
            js_file = js_files[idx]
            infile = open(po_file, 'r')
            try:
                catalog = read_po(infile, locale)
            finally:
                infile.close()

            if self.statistics:
                translated = 0
                for message in list(catalog)[1:]:
                    if message.string:
                        translated +=1
                percentage = 0
                if len(catalog):
                    percentage = translated * 100 // len(catalog)
                log.info('%d of %d messages (%d%%) translated in %r',
                         translated, len(catalog), percentage, po_file)

            if catalog.fuzzy and not self.use_fuzzy:
                log.warn('catalog %r is marked as fuzzy, skipping', po_file)
                continue

            for message, errors in catalog.check():
                for error in errors:
                    log.error('error: %s:%d: %s', po_file, message.lineno,
                              error)

            log.info('compiling catalog %r to %r', po_file, js_file)

            outfile = open(js_file, 'wb')
            try:
                write_js(outfile, catalog, use_fuzzy=self.use_fuzzy)
            finally:
                outfile.close()
            
        
