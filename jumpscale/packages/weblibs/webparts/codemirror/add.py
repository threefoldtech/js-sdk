from Jumpscale import j
import os

mypath = j.sal.fs.getDirName(os.path.abspath(__file__))


def add(
    self,
    code,
    template="python",
    path="",
    edit=True,
    exitpage=True,
    spacename="",
    pagename="",
    linenr=False,
    linecolor="#eee",
    linecolortopbottom="1px solid black",
    wrap=True,
    wrapwidth=100,
    querystr=None,
    theme="monokai",
    autorefresh=False,
    beforesave=None,
):
    """
    TODO: define types of templates supported
    @template e.g. python
    if path is given and edit=True then file can be editted and a edit button will appear on editor
    """
    # if codeblock no postprocessing(e.g replacing $$space, ...) should be
    # done

    if edit:
        self.processparameters["postprocess"] = False
    self.js_add("%s/codemirror/lib/codemirror.js" % self.liblocation)
    self.css_add("%s/codemirror/lib/codemirror.css" % self.liblocation)
    self.js_add("%s/codemirror/mode/javascript/javascript.js" % self.liblocation)
    self.css_add("%s/codemirror/theme/%s.css" % (self.liblocation, theme))
    # self.css_add("%s/codemirror/doc/docs.css"% self.liblocation)
    self.js_add("%s/codemirror/mode/%s/%s.js" % (self.liblocation, template, template))

    # add the id
    self._codeblockid += 1

    # call the template engine
    config = {}
    config["linecolortopbottom"] = linecolortopbottom
    config["linecolor"] = linecolor
    config["id"] = self._codeblockid
    config["code"] = code
    config["path"] = path
    config["linenr"] = linenr
    config["wrap"] = wrap
    config["theme"] = theme
    config["template"] = template
    config["autorefresh"] = autorefresh

    CSS = j.tools.jinja2.file_render("%s/codemirror.css" % mypath, config=config)

    self.css_add(cssContent=CSS)

    HTML = j.tools.jinja2.file_render("%s/codemirror.html" % mypath, config=config)
    self.html_add(HTML)

    if path != "" and edit:
        raise RuntimeError("not implemented, need to see how to do with blueprints")
        # F=j.data.text.strip(F)
        # F = F.replace("$id", str(self._codeblockid))
        # guid = j.data.idgenerator.generateGUID()
        # content = {'space': spacename, 'path': path, 'page': pagename, 'querystr': querystr}
        # j.apps.system.contentmanager.dbmem.set(guid, content, 60)
        # F = F.replace("$guid", guid)
        # self.part_add(F)

    # if not self._hasCodeblock:
    if linenr:
        linenr = "true"
    else:
        linenr = "false"

    JS = j.tools.jinja2.file_render("%s/codemirror.js" % mypath, config=config)

    self.js_add(jsContent=JS, header=False)
    self._hasCodeblock = True


# def addCodePythonBlock(self, code, title="", removeLeadingTab=True):
#     # todo
#     if removeLeadingTab:
#         check = True
#         for line in code.split("\n"):
#             if not(line.find("    ") == 0 or line.strip() == ""):
#                 check = False
#         if check == True:
#             code2 = code
#             code = ""
#             for line in code2.split("\n"):
#                 code += "%s\n" % line[4:]
#     self.addCodeBlock(code)
