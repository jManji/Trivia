

class Cache(object):
    """Caches the correct answer per question."""

    def __init__(self):
        self.cache = {}
        
    def put(self, k, v):
        self.cache[k] = v
        return k
    
    def put(self, question):
        id = question['id']
        self.cache[id] = question['correct_option']
        return id
        
    def get(self, id):
        return self.cache.pop(id, None)