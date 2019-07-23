from jumpscale.clients.base import SecureClient
from jumpscale.god import j

class Gitlab(SecureClient):
    def __init__(self, instance_name='myinstance'):
        self.instance_name = instance_name
        super().__init__(self)
    
    def hi(self):

        print("gitlab client")
        j.sals.fs.basename('aa')
        g = j.clients.github.Github('xmon')
        print(g.config.data)
        g.config.data = {"a": "1", "__pass": "abcegithub"}

if __name__ == "__main__":
    g = Gitlab('xmon')
    print(g.config.data)
    g.config.data = {"a": "1", "__pass": "abcegitlab"}

    print(g.config.data)

    gogs = Gogs('main')
    print(gogs.config.data)
    gogs.config.data = {"user":"ahmed", "__tok":"ghijk"}
    print(gogs.config.data)