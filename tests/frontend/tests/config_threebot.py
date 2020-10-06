import os
from jumpscale.loader import j

tname = os.environ.get("TNAME")
email = os.environ.get("EMAIL")
words = os.environ.get("WORDS")
explorer_url = "https://explorer.testnet.grid.tf/api/v1"
if not (tname and email and words):
    raise Exception("Please add (TNAME, EMAIL, WORDS) of your 3bot identity as environment variables")

# Check if there is identity registered to set it back after the tests are finished.
me = None
if j.core.identity.list_all() and hasattr(j.core.identity, "me"):
    me = j.core.identity.me

# Configure test identity and start threebot server.
identity_name = j.data.random_names.random_name()
identity = j.core.identity.new(identity_name, tname=tname, email=email, words=words, explorer_url=explorer_url)
identity.register()
j.core.identity.set_default(identity_name)
