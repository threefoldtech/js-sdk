def get_chatbot():
    from .chatflows import GedisChatBot
    return GedisChatBot

def test_example():
    from gevent import monkey
    monkey.patch_all()
    
    import gevent
    from jumpscale.god import j

    server = j.servers.gedis.get("chatflows")
    server.actor_add('example', '/sandbox/code/github/js-next/js-ng/jumpscale/chatflows/actors/chatbot.py')
    gevent.spawn(server.start)
    # server.start()

    # http_server = j.servers.gedis_http.get("chatflows")
    # gevent.spawn(http_server.start)