const BASE_URL = "/docsites"
var converter = new showdown.Converter();

// A simple request cache with expiration
// because we only do get requests
function DocsiteRequestsCache() {
    this.keyPrefix = 'DocsiteCache';
    this.expireIn = 120000; // 2m as milliseconds
}

DocsiteRequestsCache.prototype.getKey = function (url, postfix) {
    let key = this.keyPrefix + '_' + url;
    if (postfix) {
        return key + '_' + postfix;
    }
    return key;
};
DocsiteRequestsCache.prototype.getData = function (value) {
    var self = this;
    return JSON.stringify({
        value: value,
        expireIn: Date.now() + self.expireIn
    });
};
DocsiteRequestsCache.prototype.set = function (url, value) {
    localStorage.setItem(this.getKey(url), this.getData(value));
};
DocsiteRequestsCache.prototype.get = function (url) {
    var self = this;

    var data = localStorage.getItem(self.getKey(url));
    if (data) {
        data = JSON.parse(data);
        if (data.expireIn >= Date.now()) {
            return data.value;
        }
    }
};

function DocSite(onLoaded) {
    this.cache = new DocsiteRequestsCache();
    this.tokensKey = this.cache.getKey(window.location.pathname, 'tokens');

    this.docsiteLoaded = onLoaded || function () { };
}

DocSite.prototype.makeRequest = function (url, varsObj) {
    var self = this;
    var request = new XMLHttpRequest();

    return new Promise(function (resolve, reject) {
        var cached = self.cache.get(url);
        if (cached) {
            self.parseResponse(cached, varsObj);
            resolve();
            return;
        }

        request.onreadystatechange = function () {
            if (request.readyState !== 4) return;
            if (request.status >= 200 && request.status < 300) {
                self.cache.set(url, request.responseText);
                self.parseResponse(request.responseText, varsObj);
                resolve()
            } else {
                reject({
                    status: request.status,
                    statusText: request.statusText
                });
            }
        };
        request.open('GET', url, true);
        request.send();
    });
};
DocSite.prototype.parseResponse = function (contents, varsObj) {
    var matches = contents.match(/\++([^\+]+)\++([^]*)/i);
    var variablesLines = matches[1].trim().split("\n");
    for (let i in variablesLines) {
        let line = variablesLines[i];
        if (line.includes('=')) {
            const [name, ...values] = line.split('=');
            varsObj[name.trim()] = values.join('=').trim().replace(/'/g, "").replace(/"/g, "");
        }
    }
    varsObj.content = converter.makeHtml(matches[2].trim());
};
DocSite.prototype.removeLoadingDiv = function () {
    var el = document.getElementById('loading-div');
    if (el) {
        el.remove();
    }
}
DocSite.prototype.hasHandlebars = function (s) {
    if (!s) {
        return;
    }
    return s.includes('{{{') && s.includes('}}}');
}
DocSite.prototype.getHandlebarsWithElements = function () {
    var self = this;
    let all = [];

    let iter = document.createNodeIterator(
        document.body, NodeFilter.SHOW_TEXT | NodeFilter.SHOW_ELEMENT, null);
    let node = iter.nextNode();

    while (node) {
        if (node.nodeType == Node.TEXT_NODE) {
            if (self.hasHandlebars(node.textContent)) {
                all.push({
                    element: node,
                    reference: node.textContent,
                });
            }
        }

        // maybe any attribute too
        for (let i in node.attributes) {
            let attr = node.attributes[i];
            if (self.hasHandlebars(attr.value)) {
                all.push({
                    element: node,
                    reference: attr.value,
                    attr: attr.name,
                });
            }
        }

        node = iter.nextNode();
    }

    return all;
}
DocSite.prototype.getTokens = function (tokenizer) {
    let tokens = {};

    for (let i in tokenizer.body) {
        const token = tokenizer.body[i];
        if (token.type == 'MustacheStatement') {
            // token.path.original will be like `githubAccount.githubRepo.path.to.file.md.variableName`
            const parts = token.path.original.split(".");
            const variableName = parts.pop();
            const docSite = parts.shift();
            const mdPath = parts.join(".");

            // Build tokens object that we will loop on it to get variables
            tokens[docSite] = tokens[docSite] || {};
            tokens[docSite][mdPath] = tokens[docSite][mdPath] || {};
            tokens[docSite][mdPath][variableName] = "";
        }
    }

    return tokens;
};
DocSite.prototype.fetchData = function (tokens, onSuccess) {
    var self = this;
    // Get values md pages
    promises = [];
    for (let docSite in tokens) {
        for (let mdPath in tokens[docSite]) {
            let url = `${BASE_URL}/${docSite}/${mdPath.replace(/\./g, "/")}.md`;
            promises.push(self.makeRequest(url, tokens[docSite][mdPath]));
        }
    }

    // Wait for all promises till complete
    const reflect = p => p.then(v => ({ v, status: "fulfilled" }),
        e => ({ e, status: "rejected" }));

    Promise.all(promises.map(reflect)).then(() => {
        onSuccess();
    });
};
DocSite.prototype.populateData = function (handles, tokens) {
    var self = this;

    // update element by element
    for (let i in handles) {
        let handle = handles[i];
        let value = Handlebars.compile(handle.reference)(tokens);
        // value can be only text content or an html string
        if (handle.attr) {
            handle.element.setAttribute(handle.attr, value);
        } else {
            // if not an attribute, replace the element itself with a new fragment
            // that contains one or more elements (or even a single text element)
            let frag = document.createRange().createContextualFragment(value);
            handle.element.replaceWith(frag);
        }
    }
    // remove loading div
    self.removeLoadingDiv();
    self.docsiteLoaded();
};
DocSite.prototype.onWindowLoaded = function () {
    var self = this;

    handles = self.getHandlebarsWithElements();
    let references = handles.map(function (handle) {
        return handle.reference;
    });

    let tokens = self.cache.get(self.tokensKey);
    if (!tokens) {
        let tokenizer = Handlebars.parse(references.join("\n"));
        tokens = self.getTokens(tokenizer);
        self.fetchData(tokens, function () {
            self.populateData(handles, tokens);
            self.cache.set(self.tokensKey, tokens);
        })
    } else {
        self.populateData(handles, tokens);
    }
};
DocSite.prototype.init = function () {
    window.addEventListener("DOMContentLoaded", this.onWindowLoaded.bind(this));
}
