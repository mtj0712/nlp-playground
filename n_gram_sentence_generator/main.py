import re
import math

import pygtrie
import numpy as np
from numpy import random

import sys
import os

os.chdir('..')
sys.path.append(os.getcwd())

from reader import *

punc_pattern = re.compile('[‘’“”!\"#$%&\'()*+,\\-./:;<=>?@[\\\\\\]^_`{|}~]')
end_mark_set = {'!', '.', '?'}
no_space_after_this = {'-', '/', '(', '’*', '*’*', '‘', '“'}
no_space_before_this = {'”', '’', '*’', '*’*', ')', '-', '/', ':', ';', ',', '!', '.', '?'}

print('Begin converting text files into a list of words.')

bcp = BCPReader()
kjv = KJVReader()
wsh = ShakespeareReader()
eme_list = []

while not bcp.is_eof():
    units = bcp.read_sentence().lower().split()
    for u in units:
        while u:
            match = punc_pattern.search(u)
            if match:
                i = match.start()
                if i != 0:
                    eme_list.append(u[:i])
                
                if u[i:i+2] == '&c':
                    punc = u[i:i+2]
                    u = u[i+2:]
                else:
                    punc = u[i]
                    if punc == '’':
                        if i != 0 and u[i-1].isalpha():
                            punc = '*' + punc
                        if i+1 < len(u) and u[i+1] != ' ':
                            punc += '*'
                    u = u[i+1:]
                eme_list.append(punc)
            else:
                eme_list.append(u)
                break

print('Finished converting data/bcp.txt into a list of words.')

while not kjv.is_eof():
    units = kjv.read_sentence().lower().split()
    for u in units:
        while u:
            match = punc_pattern.search(u)
            if match:
                i = match.start()
                if i != 0:
                    eme_list.append(u[:i])
                
                punc = u[i]
                if punc == '’':
                    if i != 0 and u[i-1].isalpha():
                        punc = '*' + punc
                    if i+1 < len(u) and u[i+1] != ' ':
                        punc += '*'
                u = u[i+1:]
                eme_list.append(punc)
            else:
                eme_list.append(u)
                break

print('Finished converting data/kjv.txt into a list of words.')

while not wsh.is_eof():
    units = wsh.read_sentence().lower().split()
    for u in units:
        while u:
            match = punc_pattern.search(u)
            if match:
                i = match.start()
                if i != 0:
                    eme_list.append(u[:i])
                
                if u[i:i+2] == '&c':
                    punc = u[i:i+2]
                    u = u[i+2:]
                else:
                    punc = u[i]
                    if punc == '’':
                        if i != 0 and u[i-1].isalpha():
                            punc = '*' + punc
                        if i+1 < len(u) and u[i+1].isalpha():
                            punc += '*'
                    u = u[i+1:]
                eme_list.append(punc)
            else:
                eme_list.append(u)
                break

print('Finished converting data/shakespeare.txt into a list of words.')

# Building the unigram model

eme_trie = pygtrie.StringTrie()
eme_v = 0 # size of the vocabulary
eme_wordlist = []

for w in eme_list:
    try:
        eme_trie[w] += 1
    except KeyError:
        eme_trie[w] = 1
        eme_wordlist.append(w)
        eme_v += 1

print('Finished building a trie for unigrams')

# Building bigram ~ 5-gram models

for n in range(2, 6):
    ngram = [''] * n
    for w in eme_list:
        ngram[-1] = w
        try:
            eme_trie['/'.join(ngram)] += 1
        except KeyError:
            eme_trie['/'.join(ngram)] = 1
    
        if w in end_mark_set:
            ngram[:-1] = [''] * (n - 1)
        else:
            ngram[:-1] = ngram[1:]
    
    print(f'Finished building a trie for {'bi' if n == 2 else ('tri' if n == 3 else f'{n}-')}grams')

for n in range(2, 6):
    print('========== ' + ('bi' if n == 2 else ('tri' if n == 3 else f'{n}-')) + 'gram ==========')
    print()
    
    ngram = [''] * n
    sentence_len = 0
    
    while ngram[-1] not in end_mark_set:
        if 200 <= sentence_len:
            print(' <<< The sentence being generated has exceeded 200 tokens. Sentence finishing failed. >>>')
            break
        
        ngram[:-1] = ngram[1:]
        
        if ngram[-2] == '':
            history = '/' * (n - 2)
            history_count = eme_trie['.'] + eme_trie['?'] + eme_trie['!']
        else:
            history = '/'.join(ngram[:-1])
            history_count = eme_trie[history]
        
        p = np.zeros(eme_v)
        for i in range(eme_v):
            try:
                p[i] = eme_trie[history + '/' + eme_wordlist[i]] / history_count
            except KeyError:
                pass
        
        ngram[-1] = eme_wordlist[random.choice(eme_v, p=p)]
        
        output_text = '’' if '’' in ngram[-1] else ngram[-1]
        if sentence_len == 0 or ngram[-2] in no_space_after_this or ngram[-1] in no_space_before_this:
            output = output_text
        else:
            output = ' ' + output_text
        print(output, end='')
        
        sentence_len += 1
    
    print()
    print()

print('Finish.')
