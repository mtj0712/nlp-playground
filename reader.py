from abc import ABC, abstractmethod
import string
import re
import pygtrie

class BaseReader(ABC):
    def __init__(self, filename, encoding, skiplines=0):
        self.file = open('data/' + filename, 'r', encoding=encoding)
        self.buffer = ''
        self.space_pattern = re.compile('\\s+')
        self.end_mark_pattern = re.compile('\\!|\\.|\\?')
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

class BCPReader(BaseReader):
    def __init__(self):
        super().__init__('bcp.txt', 'utf-8')

    def read_sentence(self):
        if self.is_eof():
            return ''
        
        if self.buffer == '':
            self.buffer = self.file.readline()
            while self.buffer != '' and (self.buffer[0] == '\n' or self.buffer[0] == '#'):
                self.buffer = self.file.readline()
        
        # End of file reached
        if self.buffer == '':
            self.set_eof()
            return ''
        
        # First sentence of the buffer returned
        eos = self.end_mark_pattern.search(self.buffer)
        i = eos.start()
        output = self.buffer[:i+1]
        self.buffer = self.buffer[i+2:]
        return output

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
        
        eos = self.end_mark_pattern.search(self.buffer)
        while eos == None:
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
            eos = self.end_mark_pattern.search(self.buffer)
        
        i = eos.start()
        output = self.buffer[:i+1]
        self.buffer = self.buffer[i+2:]
        return output

class ShakespeareReader(BaseReader):
    def __init__(self):
        super().__init__('shakespeare.txt', 'utf-8', 31)
        
        self.titles = pygtrie.StringTrie()
        for _ in range(44):
            self.titles[self.file.readline().strip()] = None
        
        # 0: sonnets, 1: plays, 2: poems
        self.stage = 0
        
        self.play_beginnings = pygtrie.StringTrie([
            ('ACT I', None),
            ('INDUCTION', None),
            ('PROLOGUE', None),
            ('THE PROLOGUE', None)
        ])
    
    def read_sentence(self):
        if self.is_eof():
            return ''
        
        eos = self.end_mark_pattern.search(self.buffer)
        while eos == None:
            while True:
                line = self.file.readline().strip()
                if self.titles.has_key(line):
                    if line == 'ALL’S WELL THAT ENDS WELL':
                        self.stage = 1
                    elif line == 'A LOVER’S COMPLAINT':
                        self.stage = 2
                    
                    if self.stage == 1:
                        while self.file.readline().strip() != 'Dramatis Personæ':
                            pass
                        while not self.play_beginnings.has_key(self.file.readline().strip()):
                            pass
                    
                elif line != '':
                    if self.stage == 0:
                        if (not line.isdigit()) and line != 'THE END':
                            break
                    elif self.stage == 1:
                        if line[:3] != 'ACT' and line[:5] != 'SCENE' and not line.isupper():
                            # Below is a simple algorithm for removing square brackets and all texts within them.
                            # This simple algorithm is justified because our text (data/shakespeare.txt) does not contain square brackets within another pair of square brackets.
                            open_bracket = line.find('[')
                            close_bracket = line.find(']')
                            while open_bracket != -1:
                                left_side = line[:open_bracket].strip()
                                if close_bracket != -1:
                                    right_side = line[close_bracket+1:].strip()
                                    if left_side == '':
                                        line = right_side
                                    elif right_side == '':
                                        line = left_side
                                    else:
                                        line = left_side + ' ' + right_side
                                else:
                                    line = left_side
                                    while close_bracket == -1:
                                        next_part = self.file.readline().strip()
                                        close_bracket = next_part.find(']')
                                    right_side = next_part[close_bracket+1:].strip()
                                    if left_side != '' and right_side != '':
                                        line += ' ' + right_side
                                    else:
                                        line += right_side
                                open_bracket = line.find('[')
                                close_bracket = line.find(']')
                            line.replace('_', '')
                            if line != '':
                                break
                    else:
                        if line[:23] == 'TO THE RIGHT HONOURABLE':
                            for _ in range(2):
                                self.file.readline()
                        elif line[:15] == 'Your Lordship’s' or line[:6] == '_Vilia' or line[:25] == 'Your honour’s in all duty':
                            self.file.readline()
                        elif line == '*** END OF THE PROJECT GUTENBERG EBOOK THE COMPLETE WORKS OF WILLIAM SHAKESPEARE ***':
                            self.set_eof()
                            return ''
                        elif (not line.isupper()) and line[:2] != '* ':
                            line = line.rstrip(string.digits + string.whitespace)
                            break
            if line != '':
                self.buffer += line + ' '
                eos = self.end_mark_pattern.search(self.buffer)
        
        i = eos.start()
        output = self.buffer[:i+1]
        self.buffer = self.buffer[i+1:].lstrip()
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
