def get_zos_for(identity_name):
    return Zosv2(j.core.identity.get(identity_name))
