import pytest

from jumpscale.god import j
from jumpscale.data.treemanager.exceptions import NameExistsError, EmptyNameError, RootRemoveError


def convert_to_names_dict(subtree):
    result = {}
    for ch in subtree.children.values():
        result[ch.name] = convert_to_names_dict(ch)
    return result


def same_names(subtree, names_dict):
    return convert_to_names_dict(subtree) == names_dict


@pytest.fixture
def fs():
    fs = j.data.treemanager.Tree()
    fs.add_node_by_path("root", {"file_name": "root", "modified": "12/3/2019"})
    fs.add_node_by_path("etc", {"file_name": "etc", "modified": "13/3/2018"})
    fs.add_node_by_path("etc.hosts", {"file_name": "hosts", "modified": "14/3/2017"})
    fs.add_node_by_path("etc.passwd", {"file_name": "passwd", "modified": "14/3/2016"})
    fs.add_node_by_path("root.desktop", {"file_name": "desktop", "modified": "14/3/2015"})
    fs.add_node_by_path("root.desktop.hosts", {"file_name": "hosts", "modified": "14/3/2014"})
    fs.add_node_by_path("root.desktop.passwd", {"file_name": "passwd", "modified": "14/3/2016"})
    return fs


@pytest.fixture
def names_dict():
    return {"root": {"desktop": {"hosts": {}, "passwd": {}}}, "etc": {"hosts": {}, "passwd": {}}}


def test_construction(fs, names_dict):
    # number of nodes
    assert len(fs.search_custom(lambda x: True)) == 7
    assert same_names(fs.root, names_dict)


def test_search_by_data(fs):
    data = {"file_name": "passwd", "modified": "14/3/2016"}
    found = fs.search_by_data(data)
    assert len(found) == 2
    assert found[0].data == data and found[1].data == data
    names_list = list(map(lambda x: x.get_path(), found))
    names_list.sort()
    assert names_list == ["etc.passwd", "root.desktop.passwd"]


def test_search_by_name(fs):
    name = "hosts"
    found = fs.search_by_name(name)
    assert len(found) == 2

    assert found[0].name == name and found[1].name == name
    names_list = list(map(lambda x: x.get_path(), found))
    names_list.sort()
    assert names_list == ["etc.hosts", "root.desktop.hosts"]


def test_search_custom(fs):
    pred = lambda x: x.data["modified"].split("/")[-1] < "2018"
    too_old = fs.search_custom(pred)
    assert len(too_old) == 5
    names_list = list(map(lambda x: x.get_path(), too_old))
    ref_list = ["etc.hosts", "etc.passwd", "root.desktop", "root.desktop.hosts", "root.desktop.passwd"]
    names_list.sort()
    ref_list.sort()
    assert names_list == ref_list


def test_get_by_path(fs):
    assert fs.get_by_path("root").name == "root"
    assert fs.get_by_path("etc.hosts").name == "hosts"
    assert fs.get_by_path("root.desktop.passwd").name == "passwd"
    assert fs.get_by_path("root.desktop.omar") is None


def test_remove_node(fs, names_dict):
    fs.remove_node(fs.get_by_path("root.desktop.passwd"))
    del names_dict["root"]["desktop"]["passwd"]
    assert same_names(fs.root, names_dict)
    fs.remove_node(fs.get_by_path("etc"))
    del names_dict["etc"]
    assert same_names(fs.root, names_dict)
    with pytest.raises(RootRemoveError):
        fs.remove_node(fs.root)


def test_add_node_by_path(fs, names_dict):
    fs.add_node_by_path("root.desktop.omar", {"file_name": "omar", "modified": "0/0/0"})
    names_dict["root"]["desktop"]["omar"] = {}
    assert same_names(fs.root, names_dict)
    fs.add_node_by_path("dev.sda", {"file_name": "sda", "modified": "13/5/2015"})
    names_dict["dev"] = {"sda": {}}
    assert same_names(fs.root, names_dict)
    assert fs.root.children["dev"].data is None
    assert fs.root.children["dev"].children["sda"].data == {"file_name": "sda", "modified": "13/5/2015"}
    assert fs.root.children["root"].children["desktop"].children["omar"].data == {
        "file_name": "omar",
        "modified": "0/0/0",
    }
    with pytest.raises(EmptyNameError):
        fs.add_node_by_path("root..omar", None)


def test_remove_node_by_path(fs, names_dict):
    fs.remove_node_by_path("root.desktop.passwd")
    del names_dict["root"]["desktop"]["passwd"]
    assert same_names(fs.root, names_dict)
    fs.remove_node_by_path("etc")
    del names_dict["etc"]
    assert same_names(fs.root, names_dict)
    fs.remove_node_by_path("root.desktop.omar")
    assert same_names(fs.root, names_dict)


# TreeNode


def test_add_child(fs, names_dict):
    node = fs.get_by_path("root.desktop.passwd")
    added_node = j.data.treemanager.TreeNode("creep", node, {})
    node.add_child(added_node)
    names_dict["root"]["desktop"]["passwd"]["creep"] = {}
    assert same_names(fs.root, names_dict)
    with pytest.raises(NameExistsError):
        node.add_child(added_node)


def test_get_child_by_name(fs):
    node = fs.get_by_path("root.desktop")
    child_node = fs.get_by_path("root.desktop.passwd")
    assert node.get_child_by_name("passwd") == child_node
