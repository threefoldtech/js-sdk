import http.cookiejar
import urllib.error
import urllib.parse
import urllib.request
from jumpscale.loader import j


def Connect(username, password, hostname="127.0.0.1", port=8080):
    return BlockingConnection(username, password, hostname, port)


class BlockingConnection:
    def __init__(self, username, password, hostname="127.0.0.1", port=8080):
        self.cookiejar = http.cookiejar.CookieJar()
        data = {"username": username, "password": password}
        self.urlopener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cookiejar))
        if port == 443:
            url = "https://%s" % hostname
        else:
            url = "http://%s:%s" % (hostname, port)
        try:
            self.urlopener.open(url + "/login.cgi", urllib.parse.urlencode(data).encode("utf-8"), timeout=30).close()
            if not self.cookiejar:
                raise Exception("Invalid username or password")
            self.basicAuth = False
        except urllib.error.HTTPError as error:
            if error.code in [501, 401]:  # not Implemented, treat it as an old device
                url = "http://%s:%s@%s:%s" % (username, password, hostname, port)
                self.urlopener = urllib.request.FancyURLopener()

                def handleBasicAuthentication(_, __):
                    # This function is called when the website returns a 401.
                    # Because we already supply the username & password in the url if we get a 401 back it means
                    # that the already supplied username & password combination
                    # is incorrect.
                    raise Exception("Invalid username or password")

                self.urlopener.prompt_user_passwd = handleBasicAuthentication
                self.basicAuth = True
            else:
                raise

        if not self.basicAuth:
            self.get_url = url + "/API.cgi?ADDR=%(addr)s&GUID=%(guid)s&TYPE=G"
            self.set_url = url + "/API.cgi?ADDR=%(addr)s&GUID=%(guid)s&TYPE=S"
            self.reset_url = url + "/API.cgi?ADDR=%(addr)s&GUID=%(guid)s&TYPE=D"
            self.getPointer_url = url + "/monitor.cgi?ADDR=%(addr)s"
            self.get_url_osc = url + "/osc.cgi?mod=%(mod)s&chn=%(chn)s&type=%(dataType)s"
            self.getDetailed_url = url + "/detailed.log?ADDR=%(addr)s&START=%(start)s&END=%(stop)s"
            self.get_url_mod_list = url + "/modlist.cgi"
        else:
            self.get_url = url + "/Data.php?code=G%(guid)s"
            self.set_url = url + "/Data.php?code=S%(guid)s"
            self.reset_url = url + "/Data.php?code=%(guid)s"
        self.urllib = urllib

    def __del__(self):
        self.logout()

    def getAttribute(self, module, guid, port=1, length=1):
        url = self.get_url % {"addr": module, "guid": guid}
        if not self.basicAuth:
            if port > 0:
                url = url + "&INDEX=" + str(port)
                url = url + "&COUNT=" + str(length)
        data = self._send_data(url)
        return data

    def getOscData(self, module, outlet, dataType):
        url = self.get_url_osc % {"dataType": dataType, "chn": outlet, "mod": module[1:]}
        data = self._send_data(url)
        return data

    def getModList(self):
        url = self.get_url_mod_list
        data = self._send_data(url)
        return data

    def getData(self, addr, guid, index=None, count=None, log=None, t1=None, t2=None, fmt=None, var=None):
        """
        This function uses the HTTP API to get information from Racktivity devices.
        """
        url = self.get_url % {"addr": addr, "guid": guid}
        if index is not None:
            url += "&INDEX=%s" % str(index)
        if count is not None:
            url += "&COUNT=%s" % str(count)
        if log is not None:
            url += "&LOG=%s" % str(log)
        if t1 is not None:
            url += "&T1=%s" % str(t1)
        if t2 is not None:
            url += "&T2=%s" % str(t2)
        if fmt is not None:
            url += "&FORMAT=%s" % str(fmt)
        if var is not None:
            url += "&VAR=%s" % str(var)
        data = self._send_data(url)
        return data

    def setAttribute(self, module, guid, value="", port=1, count=1):
        if isinstance(value, bool):
            value = int(value)
        url = self.set_url % {"addr": module, "guid": guid}
        if not self.basicAuth:
            if port > 0:
                url = url + "&INDEX=" + str(port) + "&COUNT=%d" % count

            # Add the encoded value
            url = url + "&LEN=%d" % len(value)
            url = url + "&" + self.urllib.parse.urlencode({"DATA": value})
        data = self._send_data(url)
        return data

    def setData(self, addr, guid, index=None, count=None, data=None, length=None, log=None, t1=None, t2=None, var=None):
        """
        This function can be used to send HTTP requests to racktivity devices using the HTTP API.
        """
        url = self.set_url % {"addr": addr, "guid": guid}
        if index is not None:
            url += "&INDEX=%s" % str(index)
        if count is not None:
            url += "&COUNT=%s" % str(count)
        if data is not None:
            url += "&" + self.urllib.urlencode({"DATA": data})
        if length is not None:
            url += "&LEN=%s" % str(length)
        if log is not None:
            url += "&LOG=%s" % str(log)
        if t1 is not None:
            url += "&T1=%s" % str(t1)
        if t2 is not None:
            url += "&T2=%s" % str(t2)
        if var is not None:
            url += "&VAR=%s" % str(var)
        data = self._send_data(url)
        return data

    def resetAttribute(self, module, guid, port=1):
        url = self.reset_url % {"addr": module, "guid": guid}
        if not self.basicAuth:
            if port > 0:
                url = url + "&INDEX=" + str(port) + "&COUNT=1"
            # , "data": self.urllib.quote(str(value))
        data = self._send_data(url)
        return data

    def getPointer(self, module):
        url = self.getPointer_url % {"addr": module}
        data = self._send_data(url)
        return data

    def _send_data(self, url):
        if isinstance(self.urlopener, urllib.request.OpenerDirector):
            url_f = self.urlopener.open(url, timeout=30)
        else:
            url_f = self.urlopener.open(url)
        data = url_f.read()
        url_f.close()
        if url_f.code != 200:
            raise j.exceptions.Runtime("Server fault code %s message %s" % (url_f.code, data))
        return data

    def getDetailedBinaryLog(self, module, starttime, stoptime, filename):
        url = self.getDetailed_url % {"addr": module, "start": starttime, "stop": stoptime}

        if isinstance(self.urlopener, urllib.request.OpenerDirector):
            url_f = self.urlopener.open(url, timeout=30)
        else:
            url_f = self.urlopener.open(url)

        if url_f.code != 200:
            url_f.close()
            raise j.exceptions.Runtime("Server fault code %s" % (url_f.code))
        else:
            with open(filename, "wb") as fp:
                while True:
                    chunk = url_f.read(65536)
                    if not chunk:
                        break
                    fp.write(chunk)
            url_f.close()

    def logout(self):
        if not hasattr(self, "basicAuth") or not hasattr(self, "cookiejar"):
            return

        if self.basicAuth or not self.cookiejar:
            return

        # check our cookie and logout if needed
        for cookie in self.cookiejar:
            if cookie.name == "auth":
                # this following part is just mimicking the webui
                cookieIndex = ord(cookie.value[0]) - ord("a")
                self.setAttribute("M1", 40038, chr(cookieIndex), 0)

                # remove the cookie from our jar
                self.cookiejar.clear(cookie.domain, cookie.path, cookie.name)
                break
