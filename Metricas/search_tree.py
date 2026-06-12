class SearchNode:

    __slots__ = ('move', 'depth', 'children', 'collapsed')

    def __init__(self, move=None, depth=0):
        self.move      = move       # (row, col, digit) or None for root
        self.depth     = depth
        self.children  = []
        self.collapsed = True

    def label(self):
        if self.move is None:
            return "Start"
        r, c, d = self.move
        return f"({r},{c})={d}"


class SearchTree:
    """
    Agents call push/pop during search to record the explored tree.

    Usage (DFS example):
        tree.push(row, col, digit)
        _backtrack(...)
        tree.pop()
    """

    def __init__(self):
        self.root   = SearchNode()
        self._stack = [self.root]

    def push(self, row, col, digit):
        node = SearchNode(move=(row, col, digit), depth=len(self._stack) - 1)
        self._stack[-1].children.append(node)
        self._stack.append(node)
        return node

    def pop(self):
        if len(self._stack) > 1:
            self._stack.pop()
