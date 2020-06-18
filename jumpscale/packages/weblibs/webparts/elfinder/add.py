from Jumpscale import j
import os

mypath = j.sal.fs.getDirName(os.path.abspath(__file__))


def add(self, path="", dockey=None, height=500, width=750, readonly=False, tree=False):
    self.jquery_add()
    self.js_add("%s/jquery/jquery-ui.min.js" % self.liblocation)
    self.js_add("%s/elfinder/jquery-ui.min.js" % self.liblocation)
    self.css_add("%s/jquery-ui.css" % self.liblocation)
    self.css_add("%s/elfinder/css/elfinder.min.css" % self.liblocation)
    self.css_add("%s/elfinder/css/theme.css" % self.liblocation)
    self.js_add("%s/elfinder/js/elfinder.min.js" % self.liblocation)
    self.js_add("%s/elfinder/js/proxy/elFinderSupportVer1.js" % self.liblocation)
    # codemirror resources
    self.css_add("%s/codemirror/lib/codemirror.css" % self.liblocation)
    self.css_add("%s/codemirror/addon/hint/show-hint.css" % self.liblocation)
    self.css_add("%s/codemirror/theme/elegant.css" % self.liblocation)
    self.js_add("%s/codemirror/lib/codemirror.js" % self.liblocation)
    self.js_add("%s/codemirror/addon/hint/show-hint.js" % self.liblocation)
    self.js_add("%s/codemirror/addon/hint/python-hint.js" % self.liblocation)
    self.js_add("%s/codemirror/mode/python/python.js" % self.liblocation)

    if readonly:
        commands = """
        commands : [
        'open', 'reload', 'home', 'up', 'back', 'forward', 'getfile',
        'archive',
        'resize', 'sort', 'ping'
        ],"""
        dircmd = "'reload', 'back', 'ping'"
        filecmd = "'open', '|', 'download', 'ping', '|', 'archive',"
    else:
        # customData : {rootpath:'$path'} ,
        commands = """
        commands : [
        'quicklook', 'reload', 'home', 'up', 'back', 'forward', 'getfile',
        'rm', 'duplicate', 'rename', 'mkdir', 'mkfile', 'upload', 'copy',
        'cut', 'paste','extract', 'archive', 'help',
        'resize', 'sort', 'edit', 'ping', 'download'
        ],"""
        dircmd = "'reload', 'back', 'ping', '|', 'upload', 'mkdir', 'mkfile', 'paste'"
        filecmd = "'quicklook', '|', 'download', '|', 'copy', 'cut', 'paste', 'duplicate', '|',\
                'rm', '|', 'edit', 'ping', 'rename', 'resize', '|', 'archive', 'extract',"

    config = {}
    config["height"] = str(height)
    config["width"] = str(width)
    config["commands"] = j.data.text.strip(commands)
    config["dircmd"] = j.data.text.strip(dircmd)
    config["filecmd"] = j.data.text.strip(filecmd)

    # why do we need this, prob because there is a backend for this
    if dockey is None:
        dockey = j.data.hash.md5_string(path)
    config["filecmd"] = dockey

    # //var elf = $('#elfinder').elfinder(options);
    self._explorerInstance += 1
    config["nr"] = self._explorerInstance

    if tree:
        config["tree"] = "'places', 'tree',"
    else:
        config["tree"] = ""

    # now execute the jinja
    jscode = j.tools.jinja2.file_render("%s/elfinder.js" % mypath, config=config)

    self.scriptbody_add(jscode)

    self.bootstrap3_add(jquery=False)
    self.part_add('<div id="elfinder%s"></div>' % self._explorerInstance)
