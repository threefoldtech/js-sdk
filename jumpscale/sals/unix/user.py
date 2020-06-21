import os, pwd, grp

__all__ = ["get_user_pwd", "get_current_pwd", "get_group_grp", "get_current_grp"]


def get_user_pwd(uid):
    """get user passwd record
    Args:
        uid (int): uid of the user

    Returns:
        pwd.struct_passwd
    """
    return pwd.getpwuid(uid)


def get_current_pwd():
    """get current user passwd record

    Returns:
        pwd.struct_passwd
    """
    return get_user_pwd(os.getuid())


def get_group_grp(gid):
    """get group info
    Args:
        gid (int): gid of the group

    Returns:
        grp.struct_group
    """
    return grp.getgrgid(gid)


def get_current_grp():
    """get current group info

    Returns:
        grp.struct_group
    """
    return get_group_grp(os.getgid())
