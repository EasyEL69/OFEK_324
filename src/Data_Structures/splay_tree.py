from typing import Optional


class Node:
    def __init__(self, data):
        self.data: any = data
        self.parent: Optional[Node] = None
        self.left: Optional[Node] = None
        self.right: Optional[Node] = None


class TreeNode:
    def __init__(self, data):
        self.data: any = data
        self.parent: Optional[Node] = None
        self.left: Optional[Node] = None
        self.right: Optional[Node] = None


class SplayTree:
    def __init__(self):
        self.root: Optional[Node] = None

    def left_rotate(self, x: Node):
        y = x.right
        x.right = y.left
        if y.left is not None:
            y.left.parent = x

        y.parent = x.parent
        # x is root
        if x.parent is None:
            self.root = y
        # x is left child
        elif x == x.parent.left:
            x.parent.left = y
        # x is right child
        else:
            x.parent.right = y

        y.left = x
        x.parent = y

    def right_rotate(self, x: Node):
        y = x.left
        x.left = y.right
        if y.right is not None:
            y.right.parent = x

        y.parent = x.parent
        # x is root
        if x.parent is None:
            self.root = y
        # x is right child
        elif x == x.parent.right:
            x.parent.right = y
        # x is left child
        else:
            x.parent.left = y

        y.right = x
        x.parent = y

    def splay(self, n: Node):
        # node is not root
        while n.parent is not None:
            # node is child of root, one rotation
            if n.parent == self.root:
                if n == n.parent.left:
                    self.right_rotate(n.parent)
                else:
                    self.left_rotate(n.parent)

            else:
                p = n.parent
                g = p.parent  # grandparent

                if n.parent.left == n and p.parent.left == p:  # both are left children
                    self.right_rotate(g)
                    self.right_rotate(p)

                elif n.parent.right == n and p.parent.right == p:  # both are right children
                    self.left_rotate(g)
                    self.left_rotate(p)

                elif n.parent.right == n and p.parent.left == p:
                    self.left_rotate(p)
                    self.right_rotate(g)

                elif n.parent.left == n and p.parent.right == p:
                    self.right_rotate(p)
                    self.left_rotate(g)

    def insert(self, n: Node):
        y = None
        temp = self.root
        while temp is not None:
            y = temp
            if n.data < temp.data:
                temp = temp.left
            else:
                temp = temp.right

        n.parent = y

        if y is None:  # newly added node is root
            self.root = n
        elif n.data < y.data:
            y.left = n
        else:
            y.right = n

        self.splay(n)

    def search(self, n, x):
        if x == n.data:
            self.splay(n)
            return n
        elif x < n.data:
            return self.search(n.left, x)
        elif x > n.data:
            return self.search(n.right, x)
        else:
            return None

    def in_order(self, n):
        if n is not None:
            self.in_order(n.left)
            print(n.data, end=' ')
            self.in_order(n.right)
