def merge_queues(additional):
    if not additional:
        return
    
    from smac.conf import topology
    from smac.amqp import RESPONSES, UNICAST, BROADCAST, SERVICES
    
    for queue in additional:
        queues = filter(lambda q: q['name']==queue.queue, topology.QUEUES)
        
        if len(queues):
            target_queue = queues[0]
        else:
            continue
        
        for binding in queue.bindings:
            exchange = locals().get(binding.exchange)
            l = list(target_queue['bindings'])
            l.append((exchange, str(binding.routing_key)))
            target_queue['bindings'] = tuple(l)
            