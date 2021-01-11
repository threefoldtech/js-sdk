import pytest
from jumpscale.loader import j


def test_stellar_client_get_asset_known_assets():

    stellarclient = j.clients.stellar.new(j.data.random_names.random_name(), network="TEST")
    # native XLM
    asset = stellarclient._get_asset(code="XLM")
    assert asset.is_native()
    # No issuer supplied and unknown code
    with pytest.raises(ValueError):
        stellarclient._get_asset(code="unknown")
    # testnet
    asset = stellarclient._get_asset(code="TFT")
    assert asset.code == "TFT"
    assert asset.issuer == "GA47YZA3PKFUZMPLQ3B5F2E3CJIB57TGGU7SPCQT2WAEYKN766PWIMB3"
    asset = stellarclient._get_asset(code="TFTA")
    assert asset.code == "TFTA"
    assert asset.issuer == "GB55A4RR4G2MIORJTQA4L6FENZU7K4W7ATGY6YOT2CW47M5SZYGYKSCT"
    asset = stellarclient._get_asset(code="FreeTFT")

    assert asset.code == "FreeTFT"
    assert asset.issuer == "GBLDUINEFYTF7XEE7YNWA3JQS4K2VD37YU7I2YAE7R5AHZDKQXSS2J6R"

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
