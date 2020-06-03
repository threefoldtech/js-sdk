from jumpscale.core.base import Base, fields
from enum import Enum


class SolutionType(Enum):
    FourToSixGw = "4to6gw"
    DelegatedDomain = "delegated_domain"
    Exposed = "exposed"
    Flist = "flist"
    Gitea = "gitea"
    Kubernetes = "kubernetes"
    Minio = "minio"
    Network = "network"
    Ubuntu = "ubuntu"


class TfgridSolution1(Base):
    id = fields.Integer()
    name = fields.String(default="")
    solution_type = fields.Enum(SolutionType)
    rid = fields.String(default="")
    form_info = fields.Typed(dict)
    explorer = fields.String(default="")


class TfgridSolutionsPayment1(Base):
    id = fields.Integer()
    rid = fields.String(default="")
    explorer = fields.String(default="")
    currency = fields.String(default="")
    escrow_address = fields.String(default="")
    escrow_asset = fields.String(default="")
    total_amount = fields.String(default="")
    transaction_fees = fields.String(default="")
    payment_source = fields.String(default="")
    farmer_payments = fields.Typed(dict)
    time = fields.Date()
