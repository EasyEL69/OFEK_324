from typing import Optional
from ..Exalt_File.message_ex import Msg_1553
from dataclasses import dataclass


@dataclass
class Node_data_elements:
    """Class for keeping track of an item in inventory."""
    data_1553: Optional[Msg_1553] = None
    file_position: Optional[int] = None


class Node:
    def __init__(self, data, key):
        self.data: Node_data_elements = data  # (Msg_1553, file_position)
        self.key: any = key
        self.parent: Optional[Node] = None
        self.left: Optional[Node] = None
        self.right: Optional[Node] = None


class SplayTree:
    def __init__(self):
        self.root: Optional[Node] = None

    # Search Node by Key
    def search(self, root: Optional[Node], key: any) -> Optional[Node]:

        # Key is not in tree
        if root is None:
            return None

        # key is in sub-left tree
        if root.key > key:
            return self.search(root.left, key)

        # key is in sub-right tree
        if root.key < key:
            return self.search(root.right, key)

        # key is founded
        return root

    def left_rotate(self, x: Node):
        y = x.right
        x.right = y.left
        if y.left is not None:
            y.left.parent = x

        y.parent = x.parent
        if x.parent is None:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y

        # rotate right at node x

    def right_rotate(self, x: Node):
        y = x.left
        x.left = y.right
        if y.right is not None:
            y.right.parent = x

        y.parent = x.parent
        if x.parent is None:
            self.root = y
        elif x == x.parent.right:
            x.parent.right = y
        else:
            x.parent.left = y

        y.right = x
        x.parent = y

    # Splaying operation, Moves x to the root of the tree
    def splay_node(self, x: Node):
        while x.parent is not None:
            if x.parent.parent is None:
                if x == x.parent.left:
                    # zig rotation
                    self.right_rotate(x.parent)
                else:
                    # zag rotation
                    self.left_rotate(x.parent)
            elif x == x.parent.left and x.parent == x.parent.parent.left:
                # zig-zig rotation
                self.right_rotate(x.parent.parent)
                self.right_rotate(x.parent)
            elif x == x.parent.right and x.parent == x.parent.parent.right:
                # zag-zag rotation
                self.left_rotate(x.parent.parent)
                self.left_rotate(x.parent)
            elif x == x.parent.right and x.parent == x.parent.parent.left:
                # zig-zag rotation
                self.left_rotate(x.parent)
                self.right_rotate(x.parent)
            else:
                # zag-zig rotation
                self.right_rotate(x.parent)
                self.left_rotate(x.parent)

    def splay(self, root: Optional[Node], key: any) -> Optional[Node]:
        founded_node = self.search(root, key)

        if founded_node:
            self.splay_node(founded_node)

        return founded_node

    def in_order(self, root: Node):
        if root is not None:
            self.in_order(root.left)
            print(root.data, end=' ')
            self.in_order(root.right)

    def insert(self, data, key):
        node = Node(data, key)
        y = None
        x = self.root

        while x is not None:
            y = x
            if node.key < x.key:
                x = x.left
            else:
                x = x.right

        # y is parent of x
        node.parent = y
        if y is None:
            self.root = node
        elif node.key < y.key:
            y.left = node
        else:
            y.right = node

        # splay the node
        self.splay_node(node)

# ------------------------------------------------------------------
