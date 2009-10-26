from twisted.python.log import FileLogObserver, _safeFormat, textFromEventDict


class TxAMQPLoggingObserver(FileLogObserver):
    
    def __init__(self, client, address, send_printed=False):
        self.client = client
        self.module_address = address.to_module_address()
        self.send_printed = send_printed
    
    def emit(self, eventDict):
        if not self.send_printed and eventDict.get('printed', False):
            return
        
        if self.client._transport.channel.closed:
            self.stop()
            return
        
        text = textFromEventDict(eventDict)
        
        if text is None:
            return
        
        timeStr = self.formatTime(eventDict['time'])
        fmtDict = {'system': eventDict['system'], 'text': text.replace("\n", "\n\t")}
        msgStr = _safeFormat("[%(system)s] %(text)s\n", fmtDict)
        
        self.client.receive_log_entry(self.module_address, timeStr + " " + msgStr)
        
