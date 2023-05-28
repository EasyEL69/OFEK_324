from typing import Optional
from ..Exalt_File.message_ex import Msg_1553
from dataclasses import dataclass


@dataclass
class NodeDataElements:
    """Class for keeping track of an item in inventory."""
    data_1553: Optional[Msg_1553] = None
    file_position: Optional[int] = None


class Node:
    def __init__(self, data, key):
        self.data: NodeDataElements = data  # (Msg_1553, file_position)
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

    # zag(x)
    def left_rotate(self, x: Node):
        # x : stand for parent
        # y : stand for the son we checked

        # y point to x right son
        y = x.right

        # point to parent.right_son to son.left_son to set point pointers right
        x.right = y.left

        # if son.left_son is not none it can point back
        if y.left is not None:
            y.left.parent = x

        # the new root subtree point to his grandparent and will be the root subtree
        y.parent = x.parent

        # if grandparent is none, meaning that y is going to be the root itself
        if x.parent is None:
            self.root = y

        # over-wise, check if parent is a left son or right in order to set grandparent pointer to his "new" son
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y

        # rotate left son and his parent: son will point to his parent.
        # parent will point back to his son
        y.left = x
        x.parent = y

        # rotate right at node x

    # zig(x)
    def right_rotate(self, x: Node):
        # x : stand for parent
        # y : stand for the son we checked

        # y point to x left son
        y = x.left

        # point to parent.left_son to son.right_son to set point pointers right
        x.left = y.right

        # if son.right_son is not none it can point back
        if y.right is not None:
            y.right.parent = x

        # the new root subtree point to his grandparent and will be the root subtree
        y.parent = x.parent

        # if grandparent is none, meaning that y is going to be the root itself
        if x.parent is None:
            self.root = y

        # over-wise, check if parent is a right son or left in order to set grandparent pointer to his "new" son
        elif x == x.parent.right:
            x.parent.right = y
        else:
            x.parent.left = y

        # rotate right son and his parent: son will point to his parent.
        # parent will point back to his son
        y.right = x
        x.parent = y

    # Splaying operation, Moves x to the root of the tree
    def splay_node(self, x: Node):
        # while x is not the root of tree...
        while x.parent is not None:
            # checks that x parent is the root
            if x.parent.parent is None:
                # checks for right rotate if x is left son (zig(parent))
                if x == x.parent.left:
                    # zig rotation
                    self.right_rotate(x.parent)

                # checks for left rotate if x is left son (zag(parent))
                else:
                    # zag rotation
                    self.left_rotate(x.parent)

            # checks if x is a left son and his parent is a left son also. needs to right rotate twice!
            # zig - zig: zig(x.grandparent) then zig(x.parent)
            elif x == x.parent.left and x.parent == x.parent.parent.left:
                # zig-zig rotation
                self.right_rotate(x.parent.parent)
                self.right_rotate(x.parent)

            # checks if x is a right son and his parent is a right son also. needs to left rotate twice!
            # zag - zag: zag(x.grandparent) then zag(x.parent)
            elif x == x.parent.right and x.parent == x.parent.parent.right:
                # zag-zag rotation
                self.left_rotate(x.parent.parent)
                self.left_rotate(x.parent)

            # checks if x is a right son and his parent is a left son.
            # zag - zig: zag(x.parent) then zig(x.parent)
            elif x == x.parent.right and x.parent == x.parent.parent.left:
                # zag-zig rotation
                self.left_rotate(x.parent)
                self.right_rotate(x.parent)

            # then, x is a left son and his parent is a right son.
            # zig - zag: zig(x.parent) then zag(x.parent)
            else:
                # zig-zag rotation
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
