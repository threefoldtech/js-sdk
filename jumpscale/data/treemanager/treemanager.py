"""
This is a module with a general tree implementation.
A sample usage of the Tree class as a file manager
```
if __name__ == "__main__":
    tree = Tree()
    tree.add_node_by_path("root", {"file_name": "root",
                                   "modified": "12/3/2019"})
    tree.add_node_by_path("etc", {"file_name": "etc",
                                  "modified": "13/3/2018"})
    tree.add_node_by_path("etc.hosts", {"file_name": "hosts",
                                        "modified": "14/3/2017"})
    tree.add_node_by_path("etc.passwd", {"file_name": "passwd",
                                         "modified": "14/3/2016"})
    pred = lambda x: x.data["modified"].split("/")[-1] < "2018"
    too_old = tree.search_custom(pred)
    print("Too old files (before 2018):\n")
    for f in too_old:
        print(f.name + "\n")
    print("Tree before removing /etc/hosts")
    print(tree)
    print("Tree after removing /etc/hosts")
    tree.remove_node_by_path("etc.hosts")
    print(tree)
    passwd_file = tree.get_by_path("etc.passwd")
    passwd_date = passwd_file.data["modified"]
    print("Last time /etc/passwd was modified is: " + passwd_date)
```
"""
from .exceptions import NameExistsError, EmptyNameError, RootRemoveError


class TreeNode:
    def __init__(self, name, parent, data=None):
        """
        name     (str)               : The name associated with the node
        children (dict[str:TreeNode]): A mapping between names and child nodes
        parent   (TreeNode or None)  : The parent TreeNode (None for the root)
        data                         : Data associated with the node
        """
        self.name = name
        self.parent = parent
        self.data = data
        self.children = {}

    def add_child(self, node):
        """Adds a new child

        Args:
            node (TreeNode): The node to be added

        Returns:
            TreeNode: The newly added node
        """
        child_name = node.name
        if child_name in self.children:
            raise NameExistsError("A child with the given name already exists")
        self.children[child_name] = node
        return node

    def search_by_name(self, name):
        """Search in the node's subtree for nodes with the given name

        Args:
            name (str): The name to be searched for

        Returns:
            list of TreeNode: The found nodes
        """
        return self.search_custom(lambda x: x.name == name)

    def search_by_data(self, data):
        """Search in the node's subtree for nodes with the given data

        Args:
            data: The data to be searched for

        Returns:
            list of TreeNode: The found nodes
        """
        return self.search_custom(lambda x: x.data == data)

    def search_custom(self, func):
        """Search the node's subtree the nodes satisfying the given predicate

        Args:
            func (function): A predicate the recieves a TreeNode

        Returns:
            list of TreeNode: The nodes found
        """
        result = []
        for v in self.children.values():
            result.extend(v.search_custom(func))

        if self.name != "" and func(self):
            result.append(self)
        return result

    def get_child_by_name(self, name):
        """Get the child with the given name

        Args:
            name (str): The name of the child

        Returns:
            TreeNode: The reqiested child. None if it doesn't exist.
        """
        return self.children.get(name)

    def remove_child(self, node):
        """Remove the node from the children if it exists

        Args:
            node (TreeNode): The node to be deleted

        Returns:
            TreeNode: The deleted node
        """
        return self.remove_child_by_name(node.name)

    def remove_child_by_name(self, name):
        """Remove the node from the children

        Args:
            node (TreeNode): The node to be deleted

        Returns:
            TreeNode: The deleted node. None if it doesn't exist
        """
        if name in self.children:
            node = self.children[name]
            del self.children[name]
            return node

    def get_path(self):
        """Retrieves the path of the node

        Returns:
            str: The path
        """
        if self.name == "":
            return ""
        parent_path = self.parent.get_path()
        if parent_path == "":
            return self.name
        else:
            return parent_path + "." + self.name

    def __str__(self, indentation=0):
        """Returns a string representing the node's subtree

        Args:
            indentation (int, optional): The level to which the representation\
                                         will be indented. Defaults to 0.

        Returns:
            str: The tree representation
        """
        result = "\t" * indentation + self._string_repr() + "\n"
        for v in self.children.values():
            result += v.__str__(indentation + 1)
        return result

    def _string_repr(self):
        """A helper function to return the node's name and data as a string

        Returns:
            str: The node's string representation
        """
        if self.name == "":
            return "dummy_root"
        else:
            return self.name + str(self.data).replace("\n", "\\n")


class Tree:
    """"
    A class to represent a tree
    """

    def __init__(self):
        self.root = TreeNode("", None)

    def search_by_data(self, data):
        """Search the nodes in the tree with the given data

        Args:
            func (function): A predicate the recieves a TreeNode

        Returns:
            list of TreeNode: The nodes found
        """
        return self.root.search_by_data(data)

    def search_by_name(self, name):
        """Search the nodes in the tree with the passed name

        Args:
            func (function): A predicate the recieves a TreeNode

        Returns:
            list of TreeNode: The nodes found
        """
        return self.root.search_by_name(name)

    def search_custom(self, func):
        """Search the nodes in the tree satisfying the given predicate

        Args:
            func (function): A predicate the recieves a TreeNode

        Returns:
            list of TreeNode: The nodes found
        """
        return self.root.search_custom(func)

    def get_by_path(self, path):
        """Retrieves a node designated by the given path

        Args:
            path (str): A string of names separated by a '.' that reaches\
             the desired node when followed

            data: The data associated with the newly added node

        Returns:
            None if an intermidiate node is not found.\
            Else the searched node is returned
        """
        path_arr = path.split(".")
        current_node = self.root
        for name in path_arr:
            next_node = current_node.get_child_by_name(name)
            if next_node is None:
                return None
            current_node = next_node
        return current_node

    def remove_node(self, node):
        """Remove a node from the tree.

        Args:
            node (TreeNode): The node to be removed
        """
        if node == self.root:
            raise RootRemoveError("Can't remove the root node")
        node.parent.remove_child(node)
        return node

    def add_node_by_path(self, path, data=None):
        """Add a node designated by the given path

        Args:
            path (str): A string of names separated by a '.' that reaches\
             the desired node when followed

            data: The data associated with the newly added node

        Notes:
            If intermidiate nodes are not found while traversing the path,\
            they are created with data=None.
        """
        path_arr = path.split(".")
        current_node = self.root
        for path_name in path_arr[:-1]:
            if path_name == "":
                raise EmptyNameError("Nodes with empty names are not allowed")
            next_node = current_node.get_child_by_name(path_name)
            if next_node is None:
                next_node = TreeNode(path_name, current_node)
                current_node.add_child(next_node)
            current_node = next_node
        new_node = TreeNode(path_arr[-1], current_node, data)
        return current_node.add_child(new_node)

    def remove_node_by_path(self, path):
        """Remove a node designated by the given path

        Args:
            path (str): A string of names separated by a '.' that reaches\
             the desired node when followed
        """
        path_arr = path.split(".")
        current_node = self.root
        parent_node = None
        for path_name in path_arr:
            next_node = current_node.get_child_by_name(path_name)
            if next_node is None:
                return None
            parent_node = current_node
            current_node = next_node
        return parent_node.remove_child(current_node)

    def __str__(self):
        "Return a string representation of the tree"
        return self.root.__str__(0)
