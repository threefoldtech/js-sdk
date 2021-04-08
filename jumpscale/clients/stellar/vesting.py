import stellar_sdk
from jumpscale.loader import j


_TFT_ISSUERS = {
    "TEST": "GA47YZA3PKFUZMPLQ3B5F2E3CJIB57TGGU7SPCQT2WAEYKN766PWIMB3",
    "STD": "GBOVQKJYHXRR3DX6NOX2RRYFRCUMSADGDESTDNBDS6CDVLGVESRTAC47",
}

_VESTING_ACTIVATORS = {
    "TEST": "GAXSJCVW7FBQCW3COY5B67S5QB6PLKTFL6ATLYXLZGCACO3KLYA6FVI7",
    "STD": "GB2P3V4GZNYTI3E5IOQHAF2E46GKMW26RHVTD4TZEZAELKLJHUYPH4FR",
}


_COSIGNERS = {
    "TEST": [
        "GBOZV7I3NJGXIFBMGHTETCY7ZL36QMER25IJGRFEEX3KM36YRUMHEZAP",
        "GCU5OGRCFJ3NWQWUF3A4MAGNYABOPJMCHMXYQ7TC4RQ6IYBIZBEOGN6H",
        "GAK2Q3P3YOAPK6MCM4P3ASDJYSHQ376LIO64CHBXNKIRFZECH2JY2LYX",
        "GALOCGHPJ2KQ67VIZRSLOAPJIBCUL54WG6ZHFDB6AKPIMEQXHU374UCJ",
        "GC3IFIJ7KEOZ5CUZS57HMLJLXISS7N45INIGXO2JFNJBLKOGYTSADFPB",
        "GD56QGOWI5ZRJAXNLMAH6BQ3MQEXNWI5H6Q57BFMOQZKPMRLPIYK4RC6",
        "GAJFU5JCWRVJ5G7HDYSW6NMDSS6XTRPCNEULD5MWCKQEIGFFSJMDZXUA",
        "GDBDJCWCEHLCCJ74HJUDJIBTZO7JVFCI2IIDLEPL33FHOAKVDCNAUE4P",
        "GBMXLD4BEJWWETPCFTO2NI7MFRGGBFZDIOVA7OHHFA5XBTB7YHUQBQME",
    ],
    "STD": [
        "GARF35OFGW2XFHFG764UVO2UTUOSDRVL5DU7RXMM7JJJOSVWKK7GATXU",
        "GDORF4CKQ2GDOBXXU7R3EXV3XRN6LFCGNYTHMYXDPZ5NECZ6YZLJGAA2",
        "GDTTKKRECHQMYWJWKQ5UTONRMNK54WRN3PB4U7JZAPUHLPI75ALN7ORU",
        "GDSKTNDAIBUBGQZXEJ64F3P37T7Y45ZOZQCRZY2I46F4UT66KG4JJSOU",
        "GCHUIUY5MOBWOXEKZJEQU2DCUG4WHRXM4KAWCEUQK3NTQGBK5RZ6FQBR",
        "GDTFYNE5MKGFL625FNUQUHILILFNNRSRYAAXADFFLMOOF5E6V5FLLSBG",
        "GDOSJPACWZ2DWSDNNKCVIKMUL3BNVVV3IERJPAZXM3PJMDNXYJIZFUL3",
        "GALQ4TZA6VRBBBBYMM3KSBSXJDLC5A7YIGH4SAS6AJ7N4ZA6P6IHWH43",
        "GDMMVCANURBLP6O64QWJM3L2EZTDSGTFL4B2BNXKAQPWYDX6WNAFNWK4",
    ],
}

DATA_ENTRY_KEY = "tft-vesting"

VESTING_SCHEME = "month1=05/2021,48months,priceunlock=tftvalue>month*0.015+0.15"


def _is_valid_cleanup_transaction(
    vesting_account_id: str, preauth_signer: str, network, network_passphrase, _get_unlockhash_transaction
) -> bool:

    unlock_tx = _get_unlockhash_transaction(unlockhash=preauth_signer)
    if not unlock_tx:
        return False
    txe = stellar_sdk.TransactionEnvelope.from_xdr(unlock_tx["transaction_xdr"], network_passphrase)
    tx = txe.transaction
    if not type(tx.source) is stellar_sdk.keypair.Keypair:
        return False
    if tx.source.public_key != vesting_account_id:
        return False
    if len(tx.operations) != 3:
        return False
    change_trust_op = tx.operations[0]
    if not type(change_trust_op) is stellar_sdk.operation.change_trust.ChangeTrust:
        return False
    if not change_trust_op.source is None:
        return False
    if int(change_trust_op.limit) != 0:
        return False
    if change_trust_op.asset.code != "TFT" or change_trust_op.asset.issuer != _TFT_ISSUERS[network]:
        return False
    manage_data_op = tx.operations[1]
    if not type(manage_data_op) is stellar_sdk.operation.manage_data.ManageData:
        return False
    if not manage_data_op.source is None:
        return False
    if manage_data_op.data_name != DATA_ENTRY_KEY:
        return False
    if not manage_data_op.data_value is None:
        return False
    account_merge_op = tx.operations[2]
    if not type(account_merge_op) is stellar_sdk.operation.account_merge.AccountMerge:
        return False
    if not account_merge_op.source is None:
        return False
    if account_merge_op.destination != _VESTING_ACTIVATORS[network]:
        return False
    return True


def _verify_signers(
    account_record, owner_address: str, network, network_passphrase, _get_unlockhash_transaction
) -> bool:
    # verify tresholds
    tresholds = account_record["thresholds"]
    if tresholds["low_threshold"] != 10 or tresholds["med_threshold"] != 10 or tresholds["high_threshold"] != 10:
        return False
    ## signers found for account
    signers = {signer["key"]: (signer["weight"], signer["type"]) for signer in account_record["signers"]}
    # example of signers item --> {'GCWPSLTHDH3OYH226EVCLOG33NOMDEO4KUPZQXTU7AWQNJPQPBGTLAVM':(5,'ed25519_public_key')}

    # Check all cosigners are in account signers with weight 1
    for correct_signer in _COSIGNERS[network]:
        if (
            correct_signer in signers.keys()
            and signers[correct_signer][0] == 1
            and signers[correct_signer][1] == "ed25519_public_key"
        ):
            continue
        else:
            return False

    account_id = account_record["account_id"]

    cleanup_signer_correct = False
    master_key_weight_correct = False
    owner_key_weight_correct = False
    for signer in account_record["signers"]:
        if signer["type"] == "preauth_tx":
            if signer["weight"] != 10:
                return False
            cleanup_signer_correct = _is_valid_cleanup_transaction(
                account_id, signer["key"], network, network_passphrase, _get_unlockhash_transaction
            )
            continue
        if signer["type"] != "ed25519_public_key":
            return False
        if signer["key"] == account_id:
            master_key_weight_correct = signer["weight"] == 0
        if signer["key"] == owner_address:
            owner_key_weight_correct = signer["weight"] == 5

    if len(account_record["signers"]) == 12:
        return cleanup_signer_correct and master_key_weight_correct and owner_key_weight_correct
    return len(account_record["signers"]) == 11 and master_key_weight_correct and owner_key_weight_correct


def is_vesting_account(
    account_record: dict, owner_address: str, network, network_passphrase, _get_unlockhash_transaction
) -> bool:
    if DATA_ENTRY_KEY in account_record.get("data"):
        decoded_data = j.data.serializers.base64.decode(account_record["data"][DATA_ENTRY_KEY]).decode()
        if decoded_data == VESTING_SCHEME:
            if _verify_signers(account_record, owner_address, network, network_passphrase, _get_unlockhash_transaction):
                return True
    return False
