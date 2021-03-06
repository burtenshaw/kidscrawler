from __future__ import division
import nltk
import string
from collections import defaultdict
from nltk import word_tokenize
from nltk.tag import pos_tag
import numpy as np

# Levenstein
from nltk.metrics import *

# Stopwords
from nltk.corpus import stopwords

# To use the stop words list:
stops = set(stopwords.words("english"))

Stemmer = nltk.PorterStemmer()

Lemmatizer = nltk.WordNetLemmatizer()

def sentence_tokenizer(string):
    # Break up a text into sentences
    import nltk.data
    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    sentence_list = sent_detector.tokenize(string.strip())
    return sentence_list

# Handling words as simple strings:

def sieve(string_list):
    '''
    Remove extras from a list
    '''
    string_list.sort(key=lambda s: len(s), reverse=True)
    out = []
    for s in string_list:
        if not any([s in o for o in out]):
            out.append(s)
    return out

def crossBagger(X,Y):
    '''
    Turn a two lists into one, with no extras.
    '''
    words = []
    for i in X:
        if i in Y:
            words.append(i)
    words = sieve(words)
    return words

# Handling words via their part of speach.

def posScraper(string, X):
    '''
    Scrape all the words from a string, ascociated to one POS.
    '''
    text = nltk.pos_tag(word_tokenize(string))
    pos = []
    for i in text:
        if i[1].startswith(X):
            pos.append(i[0])
    return pos

def phraseScraper(string, POS, window):
    pos_list = posScraper(string, POS)
    list = string.split()
    pos_phrases = []
    for i,item in enumerate(list):
        if item in pos_list:
            phrase = list[i-window], list[i], list[i+window]
            pos_phrases.append(phrase)
    return pos_phrases

def nounPhrases(string):
    '''
    Breaks up a sentence into chunks of nouns.
    For example, ['The Blue School'], rather than ['the', 'blue', 'school']
    '''
    grammar = r"""
        NP: {<DT|PP\$>?<JJ>*<NN>}   # chunk determiner/possessive, adjectives and noun
        {<NNP>+}                # chunk sequences of proper nouns
        {<NN>+}                 # chunk consecutive nouns
        """

    cp = nltk.RegexpParser(grammar)
    tagged_sent = nltk.pos_tag(string.split())
    parsed_sent = cp.parse(tagged_sent)
    for subtree in parsed_sent.subtrees():
      if subtree.label() == 'NP':
        yield ' '.join(word for word, tag in subtree.leaves())

def nounPropper(string):
    '''
    Tokenises the propper nouns.
    '''
    grammar = r"""
        NNP: {<DT|PP\$>?<JJ>*<NNP>}
        {<NNP>+}
        """
    cp = nltk.RegexpParser(grammar)
    tagged_sent = nltk.pos_tag(string.split())
    parsed_sent = cp.parse(tagged_sent)
    for subtree in parsed_sent.subtrees():
      if subtree.label() == 'NNP':
        yield ' '.join(word for word, tag in subtree.leaves())


def propperNounList(string):
    '''
    takes in a plain string and gives back a list of the propper nouns.
    '''
    sent_tokenized = word_tokenize(string)
    pn_list = []
    for npstr in nounPropper(string):
         pn_list.append(npstr)
    return pn_list


def nounList(string):
    '''
    takes in a plain string and gives back a list of the nouns.
    '''
    tokens = nltk.word_tokenize(string)
    tagged = nltk.pos_tag(tokens)
    nouns = [word for word,pos in tagged \
    	if (pos == 'NN' or pos == 'NNP' or pos == 'NNS' or pos == 'NNPS')]
    return nouns

# Handling 'semantically'

def levenstein(query, dataset):
    '''
    Compare the levenstein distance between the words in a sentence, and a dataset of keywords.
    To use:
    query = "I want to go and play football"
    dataset = corpus.load("data/keywords_dictionary.json")
    returns a tuple of score and ID
    '''
    for l in dataset:
        score = (0,"")
        for w1 in l[2]:
            for w2 in query:
                x = edit_distance(w1, w2)
                if x > score[0]:
                    score = (x, l[1])
    return 

def levensteinWord(query, dataset):
    '''
    Compare the levenstein distance between the words in a sentence, and a dataset of keywords.
    To use:
    query = "I want to go and play football"
    dataset = "play"
    returns the max score
    '''
    similarity = 0.0
    for w1 in dataset:
        for w2 in query:
            x = edit_distance(w1, w2)
            bigger = max(len(w1),len(w2))
            pct = (bigger - x)/bigger
            if pct > similarity:
                similarity = pct
    return similarity
    
def jaccard_sim(x,y):
    """
    Compute Jaccard similarity between two bags of words
    """
    return len(set(x) & set(y)) / float(len(set(x) | set(y)))

# Twitter crawler for Training.

def tweetCrawl(search_term, cnt):
    '''
    Search Twitter for a term and return (cnt) number of tweets as a list of tuples of tweet and first response.
    '''
    twitter = Twitter(language='en')
    tweets = twitter.search(search_term, cached=False, count=cnt)
    pairs = []
    for t in tweets:
        try:
            replies = [i.get_text() for i in BeautifulSoup(requests.get(t['url']).content, 'html.parser').select(".tweet-text")]
            pairs.append((t['text'],replies[1]))
        except IndexError:
            pass
    return pairs

## To use tweetCrawl
# search_term = "What movie should i watch?"
# cnt =999
# tweets = tweetCrawl(search_term, cnt)
