from collections import Counter

TEMP = 10

class LexicalGraph(object):
    def __init__(self, filtered_tokens, N):
        words = [t[1] for t in filtered_tokens]
        self.V = list(Counter(words))

        model = {}
        
