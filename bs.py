#!/usr/bin/env python3

# Fucntions to wrap diatheke for some more complex stuff.
import sys
import subprocess
import re

BIBLE = 'NET'
GK_BIBLE = '2TGreek'
HB_BIBLE = 'OSMHB'
GK_DICT = 'MLStrong'
HB_DICT = 'BDBGlosses_Strongs'

# wraps most of diatheke in python. -r (range) is called scope.
def diatheke(key, module=BIBLE, options='cva', search_type=None, scope=None):
    cmd = 'diatheke -b %s' %(module)
    if options is not None: cmd = '%s -o %s' % (cmd, options)
    if search_type is not None: cmd = '%s -s %s' % (cmd, search_type)
    if scope is not None: cmd = '%s -r %s' % (cmd, scope)
    cmd = '%s -k %s' % (cmd, key)
    return subprocess.getoutput(cmd)

# turns diatheke search output into a python list
def mklist(search):
    return re.sub(r'.*-- (.*) --.*', r'\1', search).split(' ; ')

# figure out the appropriate string for any given input string
def getclass(key):
    if re.match('[a-zA-Z]+\s+\d+', key.strip()):
        class_ = Ref(key)
    elif re.match('[GgHh]\d+', key.strip()):
        class_ = Num(key)
    else:
        class_ = Word(key)
    return class_


class Word:
    
    def __init__(self, key):
        self.key = key
    # Word.search returns a lists of strings (usually verses refs).
    def search(self, module=BIBLE, scope=None):
        return mklist(diatheke(self.key, module=module, scope=scope,
                               search_type='phrase'))
    # search dictionary glosses. returns a cached list of StrongNrs.
    def hb_gloss_init(self):
        self.hb_gloss = []
        for gloss in self.search(HB_DICT):
            self.hb_gloss.append(Num(gloss))
        return self.hb_gloss

    def gk_gloss_init(self):
        self.gk_gloss = []
        for gloss in self.search(GK_DICT):
            self.gk_gloss.append(Num(gloss))
        return self.gk_gloss


class Num: # Strong's number, that is (prefixed with 'H' or 'G')

    def __init__(self, key):
        if key.startswith('H'):
            self.key = key
            self.dict_ = HB_DICT
            self.bible = HB_BIBLE
        else:
            self.key = re.sub('G0*', 'G', key) 
            self.dict_ = GK_DICT
            self.bible = GK_BIBLE
        self.define = re.sub(
            '<.*?>', '', re.sub('<sense.*?n="(\w*)".*?>', r'<s>\n\t\1',
                                diatheke(self.key, module=self.dict_)))
    # Number.search returns a list of verse refs.
    def search(self, scope=None):
        key = '"<%s>"' % (self.key)
        return mklist(diatheke(key, module=self.bible, options='n',
                               scope=scope, search_type='phrase'))


class Ref: # to a verse, chaper or range

    def __init__(self, ref):
        self.ref = ref
        self.versions = {BIBLE: self.divide()}

    def add(self, module):
        self.versions[module] = self.divide(module)
    
    def divide(self, module=BIBLE):
        return re.sub(r'(\d*:\d*:)\s*\n', r'\1 ',
                      re.sub('\n\(.*\)', '',
                             diatheke(self.ref, module=module))
                      ).split('\n')


def main():
    key = getclass(' '.join(sys.argv[1:]))
    if type(key) == Ref:
        print('\n'.join(key.versions[BIBLE]))
    elif type(key) == Num:
        print(key.define)
        print(' '.join(key.search()))
    elif type(key) == Word:
        for i in key.hb_gloss_init():
            print(i.key, end=' ')
        print()
        for i in key.gk_gloss_init():
            print(i.key, end=' ')
        print()
    

if __name__ == '__main__':
    main()
