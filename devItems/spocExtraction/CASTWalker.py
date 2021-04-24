import sys
import clang.cindex

fpTempFile='/Users/hungphan/git/dataPapers/textInSPOC/temp/0_52A_25268676_code.cpp'

class ForLocation:
    def __init__(self):
        self.lineNumber=-1
        self.funcName=''
        self.listChildrenFor=[]
        self.fatherNode=None

class Walker:
    def __init__(self, filename):
        self.filename = filename
        self.currentFuncDeclName=''
        self.currentFatherFor=None
        self.listForLoops=[]
        self.lineBeginOfMainFunction=-1
        self.lineEndOfMainFunction = -1


    def walk(self, node,index):
        node_in_file =  bool(str(node.location.file) == self.filename)
        if node_in_file:
        #     print(f"node.spelling = {node.spelling:14}, node.kind = {node.kind}")
        #     if node.kind == clang.cindex.CursorKind.TEMPLATE_REF:
        #         print(f"node.get_num_template_arguments = {node.get_num_template_arguments()}")
            lstLine=[]
            for i in range(0,index):
                lstLine.append('\t')
            strNodeType=str(node.location.line).replace('CursorKind','')
            lstLine.append(str(node.location.line))
            lstLine.append(' ')
            lstLine.append(str(node.kind))
            lstLine.append(' ')
            lstLine.append(str(node.spelling))
            strLine=''.join(lstLine)
            print(strLine)
        for child in node.get_children():
            childIndex=index+1
            self.walk(child,childIndex)

    def walkInForLoop(self, node,index,indexOfFor):
        node_in_file =  bool(str(node.location.file) == self.filename)
        strNodeType = str(node.kind).replace('CursorKind.', '')
        print(strNodeType)
        if node_in_file:
        #     print(f"node.spelling = {node.spelling:14}, node.kind = {node.kind}")
        #     if node.kind == clang.cindex.CursorKind.TEMPLATE_REF:
        #         print(f"node.get_num_template_arguments = {node.get_num_template_arguments()}")
            if (strNodeType == 'FUNCTION_DECL'):
                self.currentFuncDeclName=str(node.spelling)
            backupFatherNode=self.currentFatherFor
            if(strNodeType =='FOR_STMT'):
                indexOfFor=indexOfFor+1
                # print('go here')
                if indexOfFor==1:
                    itemFor=ForLocation()
                    itemFor.fatherNode=None
                    itemFor.funcName=self.currentFuncDeclName
                    itemFor.lineNumber=node.location.line
                    self.listForLoops.append(itemFor)
                else:
                    itemFor=ForLocation()
                    itemFor.fatherNode=self.currentFatherFor
                    itemFor.funcName=self.currentFuncDeclName
                    itemFor.lineNumber = node.location.line
                    self.currentFatherFor.listChildrenFor.append(itemFor)

                self.currentFatherFor = itemFor

            lstLine = []
            for i in range(0, index):
                lstLine.append('\t')

            lstLine.append(str(node.location.line))
            lstLine.append(' ')
            lstLine.append(str(node.kind))
            lstLine.append(' ')
            lstLine.append(str(node.spelling))
            strLine=''.join(lstLine)
            print(strLine)
        for child in node.get_children():
            childIndex=index+1
            self.walkInForLoop(child,childIndex,indexOfFor)
            if (strNodeType == 'FOR_STMT'):
                self.fatherForNode = backupFatherNode
                indexOfFor=indexOfFor-1


    def walkInForLoopAndKeepTrackReturnStatement(self, node,index,indexOfFor):
        node_in_file =  bool(str(node.location.file) == self.filename)
        strNodeType = str(node.kind).replace('CursorKind.', '')
        # print(strNodeType)
        if node_in_file:
        #     print(f"node.spelling = {node.spelling:14}, node.kind = {node.kind}")
        #     if node.kind == clang.cindex.CursorKind.TEMPLATE_REF:
        #         print(f"node.get_num_template_arguments = {node.get_num_template_arguments()}")
        #     lstLine=[]
        #     for i in range(0,index):
        #         lstLine.append('\t')
            if (strNodeType == 'FUNCTION_DECL'):
                self.currentFuncDeclName=str(node.spelling)
                if(self.currentFuncDeclName == 'main'):
                    self.lineBeginOfMainFunction=node.location.line
            elif (strNodeType == 'RETURN_STMT'):
                if (self.currentFuncDeclName == 'main'):
                    self.lineEndOfMainFunction = node.location.line

            backupFatherNode=self.currentFatherFor
            if(strNodeType =='FOR_STMT'):
                indexOfFor=indexOfFor+1
                # print('go here')
                if indexOfFor==1:
                    itemFor=ForLocation()
                    itemFor.fatherNode=None
                    itemFor.funcName=self.currentFuncDeclName
                    itemFor.lineNumber=node.location.line
                    self.listForLoops.append(itemFor)
                else:
                    itemFor=ForLocation()
                    itemFor.fatherNode=self.currentFatherFor
                    itemFor.funcName=self.currentFuncDeclName
                    itemFor.lineNumber = node.location.line
                    self.currentFatherFor.listChildrenFor.append(itemFor)

                self.currentFatherFor = itemFor
            # lstLine.append(str(node.location.line))
            # lstLine.append(' ')
            # lstLine.append(str(node.kind))
            # lstLine.append(' ')
            # lstLine.append(str(node.spelling))
            # strLine=''.join(lstLine)
            # print(strLine)
        for child in node.get_children():
            childIndex=index+1
            self.walkInForLoopAndKeepTrackReturnStatement(child,childIndex,indexOfFor)
            if (strNodeType == 'FOR_STMT'):
                self.fatherForNode = backupFatherNode
                indexOfFor=indexOfFor-1

#
index = clang.cindex.Index.create()
tu = index.parse(fpTempFile)
print('{}'.format(tu))
root = tu.cursor
index=0
indexOfForLoop=0
walker = Walker(fpTempFile)
walker.walkInForLoop(root,index,indexOfForLoop)
print('size {} {} '.format(len(walker.listForLoops),walker.listForLoops[0].lineNumber))