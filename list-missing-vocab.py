import chardet
import pysrt
import re
import spacy
import sys

from ankipandas import Collection
from bs4 import BeautifulSoup

nlp = spacy.load('es', disable=['parser', 'ner'])


def lemmatize(text):
    doc = nlp(text)
    return " ".join([token.lemma_ for token in doc])

def tokenize(text):
    text = lemmatize(text).lower()
    all_words = re.findall('\w+', text)
    clean_words = []
    for word in set(all_words):
        if word.isnumeric() or len(word)<2:
            continue
        clean_words.append(word)
    return set(clean_words)

def get_file_encoding(filename):
    with open(filename, 'rb') as f:
        encoding = chardet.detect(f.read())
    return encoding['encoding']

def get_text_from_file(filename):
    encoding = get_file_encoding(filename)
    if filename[-3:] == 'srt':
        text = get_text_from_srt_file(filename, encoding)
    else:
        with open(filename, encoding=encoding) as f:
            text = f.read()
    return text

def get_text_from_srt_file(filename, encoding):
    subs = pysrt.open(filename, encoding=encoding)
    text = ''
    for sub in subs:
        text += '{}\n'.format(BeautifulSoup(sub.text).get_text())
    return text

def get_learned_words():
    col = Collection()

    is_spanish = col.cards['cdeck'] == 'Spanish'
    spanish = col.cards[is_spanish]
    is_due = spanish['cqueue'] == 'due'
    spanish_learned = spanish[is_due]

    spanish_learned.merge_notes(inplace=True)

    learned_words = []
    for index, row in spanish_learned.iterrows():
        word = row['nflds'][0]
        word = word.partition(' ')[0] # Only keep the main word
        learned_words.append(word)

    return set(learned_words)


text = get_text_from_file(sys.argv[1])
words = tokenize(text)
learned_words = get_learned_words()
tolearn_words = words - learned_words

print(tolearn_words)
print(len(tolearn_words))
print(len(words))
