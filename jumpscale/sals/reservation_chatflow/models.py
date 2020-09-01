from datetime import datetime

from jumpscale.core.base import Base, fields
from enum import Enum


class SolutionType(Enum):
    Pools = "pools"
    FourToSixGw = "4to6gw"
    DelegatedDomain = "delegated_domain"
    Exposed = "exposed"
    Flist = "flist"
    Gitea = "gitea"
    Kubernetes = "kubernetes"
    Minio = "minio"
    Network = "network"
    Ubuntu = "ubuntu"
    Monitoring = "monitoring"
    Publisher = "publisher"
    Peertube = "peertube"
    Discourse = "discourse"
    Threebot = "threebot"
    Gollum = "gollum"
    Mattermost = "mattermost"
    Cryptpad = "cryptpad"
    Unknown = "unknown"


class TfgridSolution1(Base):
    id = fields.Integer()
    name = fields.String(default="")
    solution_type = fields.Enum(SolutionType)
    rid = fields.Integer()
    form_info = fields.Typed(dict)
    explorer = fields.String(default="")


class TfgridSolutionsPayment1(Base):
    id = fields.Integer()
    rid = fields.Integer()
    explorer = fields.String(default="")
    currency = fields.String(default="")
    escrow_address = fields.String(default="")
    escrow_asset = fields.String(default="")
    total_amount = fields.String(default="")
    transaction_fees = fields.String(default="")
    payment_source = fields.String(default="")
    farmer_payments = fields.Typed(dict, default={})
    time = fields.DateTime(default=datetime.utcnow)
