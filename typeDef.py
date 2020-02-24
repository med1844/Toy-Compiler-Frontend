class TypeDefinition:

    r"""
    To create type definition, use TypeDefinition.load(fileName).

    For each line, the type definition should contain three elements, 
    divided by space:
        1. name that will be used in program
        2. regular expression
        3. (optional) display name
    
    For example:
        minus \-{1} -
        int_constant \b(-?)(0|[1-9]\d*)\b int_const
        int \bint\b int
    """

    @staticmethod
    def load(fileName):
        """
        Load type definition from given file.
        """
        td = TypeDefinition()
        with open(fileName, "r") as f:
            for line in f.readlines():
                a, b, *rest = line.split()
                assert len(rest) <= 1
                td.addDefinition(a, b, *rest)
        return td

    def __init__(self):
        self.__d = {}  # map name to RE and displayName
        self.__toInt = {}  # map name to integer
        self.__toName = {}  # map integer to name
        self.__displayNameToInt = {}  # map display name to integer
        self.__toDisplayName = {}
        self.re = None
    
    def __str__(self):
        return str(self.__d) + "\n" + str(self.__toInt)
    
    def addDefinition(self, name, expression, displayName=None):
        self.__d[name] = (expression, displayName)

        # in order to take less memory and have faster process speed, 
        # map string to int.
        if name not in self.__toInt:
            self.__toInt[name] = len(self.__toInt)
            self.__toName[len(self.__toInt) - 1] = name
            if displayName is not None:
                self.__displayNameToInt[displayName] = \
                    len(self.__toInt) - 1
                self.__toDisplayName[len(self.__toInt) - 1] = \
                    displayName
    
    def getRE(self):
        if self.re is None:
            self.re = '|'.join('(?P<%s>%s)' % (k, v[0])
                               for k, v in self.__d.items())
        return self.re

    def getID(self, name):
        assert name in self.__toInt
        return self.__toInt[name]
    
    def getIDByDisplayName(self, displayName):
        assert displayName in self.__displayNameToInt
        return self.__displayNameToInt[displayName]
    
    def getName(self, id_):
        assert id_ in self.__toName
        return self.__toName[id_]
    
    def getDisplayName(self, id_):
        assert id_ in self.__toDisplayName
        return self.__toDisplayName[id_]
