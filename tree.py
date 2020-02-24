class TreeNode:

    SPLIT_LENGTH = 3

    def __init__(self, content):
        super().__setattr__("__content", content)
        super().__setattr__("__d", {})
        super().__setattr__("__childs", [])

    def __setattr__(self, key, value):
        self.getAttributes()[key] = value
    
    def __getattr__(self, key):
        return self.getAttributes()[key]

    def __contains__(self, item):
        return item in self.getAttributes()
        
    def __str__(self):
        return str(self.getContent())
    
    def __repr__(self):
        return "'" + str(self) + "'"

    def getAttributes(self) -> dict:
        return super().__getattribute__("__d")
    
    def setAttribute(self, key, value):
        super().__setattr__(key, value)
    
    def getAttribute(self, key):
        return super().__getattribute__(key)
    
    def addChild(self, node):
        assert isinstance(node, TreeNode)
        self.getChilds().append(node)
    
    def getChilds(self) -> list:
        return super().__getattribute__("__childs")

    def getContent(self):
        return super().__getattribute__("__content")

    def apply(self, func):
        for child in self.getChilds():
            child.apply(func)
        func(self, self.getChilds())
    
    def preApply(self, func):
        func(self, self.getChilds())
        for child in self.getChilds():
            child.preApply(func)

    def run(self, func):
        func(self, self.getChilds())

    def format(self) -> (list, int, int):
        # [str, str, str, ...], width, height
        try:
            val = str(self.ns)
        except:
            val = self.getContent()
        # val = self.getContent()
        if len(self.getChilds()) >= 2:
            c, w, h = [], [], 0
            firstLLen, lastRLen = -1, -1
            secondLine = []
            for child in self.getChilds():
                tc, tw, th, lLen = child.format()
                c.append(tc)
                w.append(tw)
                rLen = tw - lLen - 1
                secondLine.append("%s|%s" % (" " * lLen, " " * rLen))
                if firstLLen == -1:
                    firstLLen = lLen
                lastRLen = rLen
                h = max(h, th)
            secondLine = (" " * self.SPLIT_LENGTH).join(secondLine)
            wa = sum(w) + (len(self.getChilds()) - 1) * self.SPLIT_LENGTH
            rc = [list() for _ in range(h)]  # result c
            leftMargin = rightMargin = 0
            if wa < len(val):
                totalMargin = len(val) - wa
                leftMargin = totalMargin >> 1
                rightMargin = totalMargin - leftMargin
                secondLine = " " * leftMargin + secondLine + " " * rightMargin
                wa = len(val)
                firstLLen += leftMargin
                lastRLen += rightMargin
            for line in range(h):
                for i, cc in enumerate(c):
                    if line < len(cc):
                        rc[line].append(cc[line])
                    else:
                        rc[line].append(" " * w[i])
                rc[line] = " " * leftMargin + (" " * self.SPLIT_LENGTH).join(rc[line]) + " " * rightMargin
            tot_slash = (wa - firstLLen - lastRLen)
            lts = (tot_slash - 1) >> 1
            rts = tot_slash - lts - 1
            firstLine = "%s%s|%s%s" % (" " * firstLLen, "_" * lts, "_" * rts, " " * lastRLen)
            ret3 = firstLLen + lts
            if len(val) > tot_slash:
                morePart = len(val) - tot_slash
                lmp = morePart >> 1
                rmp = morePart - lmp
                firstLLen -= lmp
                lastRLen -= rmp
                if firstLLen < 0:
                    for i in range(h):
                        rc[i] = " " * (-firstLLen) + rc[i]
                    secondLine = " " * (-firstLLen) + secondLine
                    firstLine = " " * (-firstLLen) + firstLine
                    wa -= firstLLen
                    firstLLen = 0
                if lastRLen < 0:
                    for i in range(h):
                        rc[i] = rc[i] + " " * (-lastRLen)
                    secondLine += " " * (-lastRLen)
                    firstLine += " " * (-lastRLen)
                    wa -= lastRLen
                    lastRLen = 0
                zeroLine = "%s%s%s" % (" " * firstLLen, val, " " * lastRLen)
            else:
                ltsz = (tot_slash - len(val)) >> 1
                rtsz = tot_slash - ltsz - len(val)
                firstLLen += ltsz
                zeroLine = "%s%s%s" % (" " * firstLLen, val, " " * (rtsz + lastRLen))
            result = [zeroLine, firstLine, secondLine]
            result.extend(rc)
            # print("==%d, %d==\n%s" % (wa, h + 3, '\n'.join(result)))
            return result, wa, h + 3, ret3
        elif len(self.getChilds()) == 1:
            c, w, h, firstLLen = self.getChilds()[0].format()
            lastRLen = w - firstLLen
            if w < len(val):
                totalMargin = len(val) - w
                leftMargin = totalMargin >> 1
                rightMargin = totalMargin - leftMargin
                for i in range(h):
                    c[i] = "%s%s%s" % (" " * leftMargin, c[i], " " * rightMargin)
                w = len(val)
                firstLLen += leftMargin
                lastRLen += rightMargin
            lc = len(val) >> 1
            rc = len(val) - lc
            if firstLLen < lc:
                lmp = lc - firstLLen
                for i in range(h):
                    c[i] = " " * lmp + c[i]
                w += lmp
                firstLLen = lc
            if lastRLen < rc:
                rmp = rc - lastRLen
                for i in range(h):
                    c[i] = c[i] + " " * rmp
                w += rmp
                lastRLen = rc
            zeroLine = "%s%s%s" % (" " * (firstLLen - lc), val, " " * (lastRLen - rc))
            firstLine = "%s|%s" % (" " * firstLLen, " " * (lastRLen - 1))
            result = [zeroLine, firstLine]
            result.extend(c)
            # print("==%d, %d==\n%s" % (w, h + 2, '\n'.join(result)))
            return result, w, h + 2, firstLLen
        else:
            return [val], len(val), 1, len(val) >> 1


class Tree:

    def __init__(self, root):
        assert isinstance(root, TreeNode)
        self.__root = root

    def __str__(self):
        c, _, _, _ = self.__root.format()
        return '\n'.join(c)
    
    def getRoot(self) -> TreeNode:
        return self.__root

    def apply(self, func):
        """
        apply @param func on every TreeNode
        the format of func param should be:
        func(parent, childs)
        parent is a TreeNode, Childs is a list 
        containing TreeNodes
        """
        self.getRoot().apply(func)

    def preApply(self, func):
        self.getRoot().preApply(func)
    
    def run(self, func):
        self.getRoot().run(func)
