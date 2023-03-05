from typing import Optional


class Node:
    def __init__(self, data):
        self.data: any = data
        self.parent: Optional[Node] = None
        self.left: Optional[Node] = None
        self.right: Optional[Node] = None


class Splay_Tree:
    def __init__(self):
        self.root: Optional[Node] = None

    # Search Node by Key
    def search(self, root: Node, key: any) -> Optional[Node]:

        # Key is not in tree
        if root is None:
            return None

        # key is in sub-left tree
        if root.data > key:
            return self.search(root.left, key)

        # key is in sub-right tree
        if root.data < key:
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

    def splay(self, root: Node, key: any):
        founded_node = self.search(root, key)

        if founded_node:
            self.splay_node(founded_node)

    def in_order(self, root: Node):
        if root is not None:
            self.in_order(root.left)
            print(root.data, end=' ')
            self.in_order(root.right)

    def insert(self, key):
        node = Node(key)
        y = None
        x = self.root

        while x is not None:
            y = x
            if node.data < x.data:
                x = x.left
            else:
                x = x.right

        # y is parent of x
        node.parent = y
        if y is None:
            self.root = node
        elif node.data < y.data:
            y.left = node
        else:
            y.right = node
        # splay the node
        self.splay_node(node)

# ------------------------------------------------------------------
