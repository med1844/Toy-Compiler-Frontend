from typing import List, Tuple


class TreeNode:

    def __init__(self, val: str, split_len = 3):
        self.val = val
        self.childs: List["TreeNode"] = []
        self.split_len = split_len

    def __repr__(self) -> str:
        return repr(self.val)

    def format(self) -> Tuple[List[str], int, int, int]:
        # [str, str, str, ...], width, height, mid of root text
        val = self.val
        if len(self.childs) >= 2:
            c, w, h = [], [], 0
            firstLLen, lastRLen = -1, -1
            secondLine = []
            for child in self.childs:
                tc, tw, th, lLen = child.format()
                c.append(tc)
                w.append(tw)
                rLen = tw - lLen - 1
                secondLine.append("%s|%s" % (" " * lLen, " " * rLen))
                if firstLLen == -1:
                    firstLLen = lLen
                lastRLen = rLen
                h = max(h, th)
            secondLine = (" " * self.split_len).join(secondLine)
            wa = sum(w) + (len(self.childs) - 1) * self.split_len
            rc: List[List[str]] = [list() for _ in range(h)]  # result c
            leftMargin = rightMargin = 0
            if wa < len(val):
                totalMargin = len(val) - wa
                leftMargin = totalMargin >> 1
                rightMargin = totalMargin - leftMargin
                secondLine = " " * leftMargin + secondLine + " " * rightMargin
                wa = len(val)
                firstLLen += leftMargin
                lastRLen += rightMargin
            rc_str: List[str] = []
            for line in range(h):
                for i, cc in enumerate(c):
                    if line < len(cc):
                        rc[line].append(cc[line])
                    else:
                        rc[line].append(" " * w[i])
                rc_str.append(" " * leftMargin + (" " * self.split_len).join(rc[line]) + " " * rightMargin)
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
                        rc_str[i] = " " * (-firstLLen) + rc_str[i]
                    secondLine = " " * (-firstLLen) + secondLine
                    firstLine = " " * (-firstLLen) + firstLine
                    wa -= firstLLen
                    firstLLen = 0
                if lastRLen < 0:
                    for i in range(h):
                        rc_str[i] = rc_str[i] + " " * (-lastRLen)
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
            result.extend(rc_str)
            # print("==%d, %d==\n%s" % (wa, h + 3, '\n'.join(result)))
            return result, wa, h + 3, ret3
        elif len(self.childs) == 1:
            c, w, h, firstLLen = self.childs[0].format()
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
            l_start_col = len(val) >> 1
            r_start_col = len(val) - l_start_col
            if firstLLen < l_start_col:
                lmp = l_start_col - firstLLen
                for i in range(h):
                    c[i] = " " * lmp + c[i]
                w += lmp
                firstLLen = l_start_col
            if lastRLen < r_start_col:
                rmp = r_start_col - lastRLen
                for i in range(h):
                    c[i] = c[i] + " " * rmp
                w += rmp
                lastRLen = r_start_col
            zeroLine = "%s%s%s" % (" " * (firstLLen - l_start_col), val, " " * (lastRLen - r_start_col))
            firstLine = "%s|%s" % (" " * firstLLen, " " * (lastRLen - 1))
            result = [zeroLine, firstLine]
            result.extend(c)
            # print("==%d, %d==\n%s" % (w, h + 2, '\n'.join(result)))
            return result, w, h + 2, firstLLen
        else:
            return [val], len(val), 1, len(val) >> 1


class Tree:
    def __init__(self, root: TreeNode):
        self.root = root

    def __str__(self):
        c, _, _, _ = self.root.format()
        return '\n'.join(c)

