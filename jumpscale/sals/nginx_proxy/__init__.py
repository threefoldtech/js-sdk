HEADER_PREFIX = "proxy_set_header "


class NginxReverseProxyConfig:
    """
        Provides ways to override options and headers for http and https server blocks.
        It's intended for usage in a nginx reverse proxy that serves a single domain.
        Maybe later we can add more customization to add new server blocks or modify global options.
    """

    def __init__(self):
        self.http_options = {
            "proxy_set_header X-Real-IP": "$remote_addr",
            "proxy_set_header Host": "$host",
            "proxy_set_header X-Forwarded-For": "$proxy_add_x_forwarded_for",
            "proxy_set_header X-Forwarded-Proto": "$scheme",
            "proxy_connect_timeout": "600",
            "proxy_send_timeout": "86400",
            "proxy_read_timeout": "86400",
            "send_timeout": "600",
            "proxy_http_version": "1.1",
            "proxy_set_header Upgrade": "$http_upgrade",
            "proxy_set_header Connection": '"upgrade"',
        }

        self.https_options = {
            "proxy_set_header X-Real-IP": "$remote_addr",
            "proxy_set_header Host": "$host",
            "proxy_set_header X-Forwarded-For": "$proxy_add_x_forwarded_for",
            "proxy_set_header X-Forwarded-Proto": "$scheme",
            "proxy_connect_timeout": "600",
            "proxy_send_timeout": "86400",
            "proxy_read_timeout": "86400",
            "send_timeout": "600",
            "proxy_http_version": "1.1",
            "proxy_set_header Upgrade": "$http_upgrade",
            "proxy_set_header Connection": '"upgrade"',
        }

    def add_http_option(self, key, *args):
        """add an option to http. Override if exists.

        Args:
            key (str): The name of the option to be set
            args (list): Joined by spaces after stringifying its entries to get the header value.

        """
        val = " ".join([str(x) for x in args])
        self.http_options[key] = val

    def add_https_option(self, key, *args):
        """add an option to https. Override if exists.

        Args:
            key (str): The name of the option to be set
            args (list): Joined by spaces after stringifying its entries to get the header value.

        """
        val = " ".join([str(x) for x in args])
        self.https_options[key] = val

    def add_option(self, key, *args):
        """add an option to http and https. Override if exists.

        Args:
            key (str): The name of the option to be set
            args (list): Joined by spaces after stringifying its entries to get the header value.

        """
        self.add_http_option(key, *args)
        self.add_https_option(key, *args)

    def add_http_header(self, name, *args):
        """add a header to http. Override if exists.

        Args:
            name (str): The name of the header to be set
            args (list): Joined by spaces after stringifying its entries to get the header value.

        """
        name = str(name)
        self.add_http_option(HEADER_PREFIX + name, *args)

    def add_https_header(self, name, *args):
        """add a header to https. Override if exists.

        Args:
            name (str): The name of the header to be set
            args (list): Joined by spaces after stringifying its entries to get the header value.

        """
        name = str(name)
        self.add_https_option(HEADER_PREFIX + name, *args)

    def add_header(self, name, *args):
        """add a header to http and https. Override if exists.

        Args:
            name (str): The name of the header to be set
            args (list): Joined by spaces after stringifying its entries to get the header value.

        """
        self.add_http_header(name, *args)
        self.add_https_header(name, *args)

    def remove_http_option(self, key):
        """remove an http option

        Args:
            key (str): The name of the option to be deleted
        """
        key = str(key)
        self.http_options.pop(key, None)

    def remove_https_option(self, key):
        """remove an https option

        Args:
            key (str): The name of the option to be deleted.
        """
        key = str(key)
        self.https_options.pop(key, None)

    def remove_option(self, key):
        """remove an option from both http and https

        Args:
            key (str): The name of the option to be deleted.
        """
        self.remove_http_option(key)
        self.remove_https_option(key)

    def remove_http_header(self, name):
        """remove a specific http header by its name

        Args:
            header (str): The name of the header to be deleted.
        """
        name = str(name)
        self.remove_http_option(HEADER_PREFIX + name)

    def remove_https_header(self, name):
        """remove a specific https header by its name

        Args:
            header (str): The name of the header to be deleted.
        """
        name = str(name)
        self.remove_https_option(HEADER_PREFIX + name)

    def remove_header(self, name):
        """remove a specific header from http and https

        Args:
            header (str): The name of the header to be deleted.
        """
        self.remove_http_header(name)
        self.remove_https_header(name)

    def clear_http(self):
        """clear all http headers"""
        self.http_options = {}

    def clear_https(self):
        """clear all https headers"""
        self.https_options = {}

    def clear_all(self):
        """clear all http and https headers"""
        self.clear_http()
        self.clear_https()

    def serialize_http(self):
        """Seriallize the http options

        Returns:
            A string representing the http options to be added to the nginx http location block
        """
        res = ""
        for k, v in self.http_options.items():
            res += f"{k} {v};\n"
        return res

    def serialize_https(self):
        """Seriallize the https options

        Returns:
            A string representing the http options to be added to the nginx https location block
        """
        res = ""
        for k, v in self.https_options.items():
            res += f"{k} {v};\n"
        return res

    def serialize(self):
        """Seriallize the http and https options

        Returns:
            A pair of strings representing the http/https options to be added to the nginx http/https location block
        """
        return self.serialize_http(), self.serialize_https()
