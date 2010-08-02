class SessionRegister(object):
    def __init__(self):
        self.sessions = []
        self.next_id = 0
    
    def add(self, session):
        self.sessions.append(session)
        self.last_id += 1
        return self.last_id - 1