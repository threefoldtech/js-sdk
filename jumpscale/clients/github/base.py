from jumpscale.clients.base import Client
from jumpscale.core.base import Base, fields
from jumpscale.loader import j

replacelabels = {
    "bug": "type_bug",
    "duplicate": "process_duplicate",
    "enhancement": "type_feature",
    "help wanted": "state_question",
    "invalid": "state_question",
    "question": "state_question",
    "wontfix": "process_wontfix",
    "completed": "state_verification",
    "in progress": "state_inprogress",
    "ready": "state_verification",
    "story": "type_story",
    "urgent": "priority_urgent",
    "type_bug": "type_unknown",
    "type_story": "type_unknown",
}


class base(Base):
    def __init__(self):
        super().__init__()

    @property
    def body_without_tags(self):
        # remove the tag lines from the body
        out = ""
        if self.body is None:
            return ""
        for line in self.body.split("\n"):
            if line.startswith("##") and not line.startswith("###"):
                continue
            out += "%s\n" % line

        out = out.rstrip() + "\n"
        return out

    # @tags.setter
    # def tags(self, ddict):
    #     if isinstance(ddict,dict) is False:
    #         raise Exception("Tags need to be dict as input for setter, now:%s" % ddict)

    #     keys = sorted(ddict.keys())

    #     out = self.body_without_tags + "\n"
    #     for key, val in ddict.items():
    #         out += ".. %s:%s\n" % (key, val)

    #     self.body = out
    #     return self.tags

    def __str__(self):
        return str(self._ddict)

    __repr__ = __str__
