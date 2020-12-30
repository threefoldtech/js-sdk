import pytest
from jumpscale.loader import j


@pytest.mark.skip("https://github.com/threefoldtech/js-sdk/issues/2062")
def test_stellar_client_get_asset_known_assets():
    # public network
    stellarclient = j.clients.stellar.new(j.data.random_names.random_name())
    asset = stellarclient._get_asset(code="TFT")
    assert asset.code == "TFT"
    assert asset.issuer == "GBOVQKJYHXRR3DX6NOX2RRYFRCUMSADGDESTDNBDS6CDVLGVESRTAC47"
    asset = stellarclient._get_asset(code="TFTA")
    assert asset.code == "TFTA"
    assert asset.issuer == "GBUT4GP5GJ6B3XW5PXENHQA7TXJI5GOPW3NF4W3ZIW6OOO4ISY6WNLN2"
    asset = stellarclient._get_asset(code="FreeTFT")
    assert asset.code == "FreeTFT"
    assert asset.issuer == "GCBGS5TFE2BPPUVY55ZPEMWWGR6CLQ7T6P46SOFGHXEBJ34MSP6HVEUT"
