from abc import ABC, abstractmethod
import re
import pygtrie

class BaseReader(ABC):
    def __init__(self, filename, encoding, skiplines=0):
        self.file = open('data/' + filename, 'r', encoding=encoding)
        self.buffer = ''
        self.space_pattern = re.compile('\\s+')
        self.__eof = False
        for _ in range(skiplines):
            self.file.readline()
    
    def __del__(self):
        if not self.__eof:
            self.file.close()
    
    def is_eof(self):
        return self.__eof
    
    def set_eof(self):
        self.__eof = True
        self.file.close()
    
    @abstractmethod
    def read_sentence(self):
        return

class KJVReader(BaseReader):
    def __init__(self):
        super().__init__('kjv.txt', 'utf-8', 20)
        
        self.titles = pygtrie.StringTrie()
        for _ in range(73):
            line = self.file.readline()
            if not self.space_pattern.fullmatch(line):
                self.titles[line] = None
        
        self.verse_pattern = re.compile('\\d+\\:\\d+')
    
    def read_sentence(self):
        if self.is_eof():
            return ''
        
        eos = self.buffer.find('.')
        while eos == -1:
            line = self.file.readline()
            if line == '*** END OF THE PROJECT GUTENBERG EBOOK THE KING JAMES VERSION OF THE BIBLE ***\n':
                self.set_eof()
                return ''
            while self.titles.has_key(line) or self.space_pattern.fullmatch(line) or line == '***\n':
                line = self.file.readline()
                if line == '*** END OF THE PROJECT GUTENBERG EBOOK THE KING JAMES VERSION OF THE BIBLE ***\n':
                    self.set_eof()
                    return ''
            verses = self.verse_pattern.split(line)
            for v in verses:
                v = v.strip()
                if v:
                    self.buffer += v + ' '
            eos = self.buffer.find('.')
        
        output = self.buffer[:eos+1]
        self.buffer = self.buffer[eos+2:]
        return output

class UDHREngReader(BaseReader):
    def __init__(self):
        super().__init__('udhr_eng.txt', 'utf-8', 2)
        self.article_pattern = re.compile('Article \\d')
        self.number_pattern = re.compile('\\d+\\. ')
    
    def read_sentence(self):
        if self.is_eof():
            return ''
        
        eos = self.buffer.find('.')
        while eos == -1:
            line = self.file.readline()
            if line == '':
                self.set_eof()
                return ''
            if self.article_pattern.match(line):
                line = self.file.readline()
            line = self.number_pattern.split(line, maxsplit=1)[-1]
            self.buffer += self.space_pattern.sub(' ', line)
            eos = self.buffer.find('.')
        
        output = self.buffer[:eos+1]
        self.buffer = self.buffer[eos+2:]
        return output