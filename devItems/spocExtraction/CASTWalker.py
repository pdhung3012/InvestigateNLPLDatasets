import sys, traceback
import clang.cindex

fpTempFile='/Users/hungphan/git/dataPapers/textInSPOC/temp/code1.cpp'

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
        self.listASTRepresents=[]
        self.lineBeginOfMainFunction=-1
        self.lineEndOfMainFunction = -1


    # def walk(self, node,index):
    #     node_in_file =  bool(str(node.location.file) == self.filename)
    #     if node_in_file:
    #     #     print(f"node.spelling = {node.spelling:14}, node.kind = {node.kind}")
    #     #     if node.kind == clang.cindex.CursorKind.TEMPLATE_REF:
    #     #         print(f"node.get_num_template_arguments = {node.get_num_template_arguments()}")
    #         lstLine=[]
    #         for i in range(0,index):
    #             lstLine.append('\t')
    #         strNodeType=str(node.location.line).replace('CursorKind','')
    #         lstLine.append(str(node.location.line))
    #         lstLine.append(' ')
    #         lstLine.append(str(node.kind))
    #         lstLine.append(' ')
    #         lstLine.append(str(node.spelling))
    #         strLine=''.join(lstLine)
    #         print(strLine)
    #     for child in node.get_children():
    #         childIndex=index+1
    #         self.walk(child,childIndex)

    def walkInForLoop(self, node,index,indexOfFor):
        node_in_file =  bool(str(node.location.file) == self.filename)
        strNodeType = str(node.kind).replace('CursorKind.', '')
        # print(strNodeType)
        if True:
        #     print(f"node.spelling = {node.spelling:14}, node.kind = {node.kind}")
        #     if node.kind == clang.cindex.CursorKind.TEMPLATE_REF:
        #         print(f"node.get_num_template_arguments = {node.get_num_template_arguments()}")
        #     if (strNodeType == 'FUNCTION_DECL'):
        #         self.currentFuncDeclName=str(node.spelling)
        #     # backupFatherNode=self.currentFatherFor
        #     if(strNodeType =='FOR_STMT'):
        #         indexOfFor=indexOfFor+1
        #         # print('go here')
        #         if indexOfFor==1:
        #             itemFor=ForLocation()
        #             itemFor.fatherNode=None
        #             itemFor.funcName=self.currentFuncDeclName
        #             itemFor.lineNumber=node.location.line
        #             self.listForLoops.append(itemFor)
        #         else:
        #             itemFor=ForLocation()
        #             itemFor.fatherNode=self.currentFatherFor
        #             itemFor.funcName=self.currentFuncDeclName
        #             itemFor.lineNumber = node.location.line
        #             self.currentFatherFor.listChildrenFor.append(itemFor)
        #
        #         self.currentFatherFor = itemFor

            lstLine = []
            for i in range(0, index):
                lstLine.append('\t')

            lstLine.append(str(node.location.line))
            lstLine.append('\t')
            lstLine.append(str(node.kind))
            lstLine.append('\t')
            lstLine.append(str(node.spelling))
            strLine=''.join(lstLine)
            # print(strLine)
            self.listASTRepresents.append(strLine)
            # print(strLine)
        for child in node.get_children():
            childIndex=index+1
            self.walkInForLoop(child,childIndex,indexOfFor)
            # if (strNodeType == 'FOR_STMT'):
            #     # self.fatherForNode = backupFatherNode
            #     indexOfFor=indexOfFor-1


    # def walkInForLoopAndKeepTrackReturnStatement(self, node,index,indexOfFor):
    #     node_in_file =  bool(str(node.location.file) == self.filename)
    #     strNodeType = str(node.kind).replace('CursorKind.', '')
    #     # print(strNodeType)
    #     if node_in_file:
    #     #     print(f"node.spelling = {node.spelling:14}, node.kind = {node.kind}")
    #     #     if node.kind == clang.cindex.CursorKind.TEMPLATE_REF:
    #     #         print(f"node.get_num_template_arguments = {node.get_num_template_arguments()}")
    #     #     lstLine=[]
    #     #     for i in range(0,index):
    #     #         lstLine.append('\t')
    #         if (strNodeType == 'FUNCTION_DECL'):
    #             self.currentFuncDeclName=str(node.spelling)
    #             if(self.currentFuncDeclName == 'main'):
    #                 self.lineBeginOfMainFunction=node.location.line
    #         elif (strNodeType == 'RETURN_STMT'):
    #             if (self.currentFuncDeclName == 'main'):
    #                 self.lineEndOfMainFunction = node.location.line
    #
    #         backupFatherNode=self.currentFatherFor
    #         if(strNodeType =='FOR_STMT'):
    #             indexOfFor=indexOfFor+1
    #             # print('go here')
    #             if indexOfFor==1:
    #                 itemFor=ForLocation()
    #                 itemFor.fatherNode=None
    #                 itemFor.funcName=self.currentFuncDeclName
    #                 itemFor.lineNumber=node.location.line
    #                 self.listForLoops.append(itemFor)
    #             else:
    #                 itemFor=ForLocation()
    #                 itemFor.fatherNode=self.currentFatherFor
    #                 itemFor.funcName=self.currentFuncDeclName
    #                 itemFor.lineNumber = node.location.line
    #                 self.currentFatherFor.listChildrenFor.append(itemFor)
    #
    #             self.currentFatherFor = itemFor
    #         # lstLine.append(str(node.location.line))
    #         # lstLine.append(' ')
    #         # lstLine.append(str(node.kind))
    #         # lstLine.append(' ')
    #         # lstLine.append(str(node.spelling))
    #         # strLine=''.join(lstLine)
    #         # print(strLine)
    #     for child in node.get_children():
    #         childIndex=index+1
    #         self.walkInForLoopAndKeepTrackReturnStatement(child,childIndex,indexOfFor)
    #         if (strNodeType == 'FOR_STMT'):
    #             self.fatherForNode = backupFatherNode
    #             indexOfFor=indexOfFor-1

    def getRepresentASTFromFile(self,fp,indexTu):
        strResult=''
        try:
            self.filename=fp
            tu = indexTu.parse(fp, args=['-std=c++17'])
            # print('{}'.format(tu))
            root = tu.cursor
            index = 0
            indexOfForLoop = 0
            self.listASTRepresents=[]
            self.walkInForLoop(root, index, indexOfForLoop)
            strResult='\n'.join(self.listASTRepresents)
            # print('aaaa {}'.format(strResult))
            # for i in tu.get_tokens(extent=tu.cursor.extent):
            #     print(i.kind)
        except:
            strResult= str(sys.exc_info()[0])
            print("Exception in user code:")
            print("-" * 60)
            traceback.print_exc(file=sys.stdout)
            print("-" * 60)
        return strResult



#

indexTu = clang.cindex.Index.create()
tu = indexTu.parse(fpTempFile, args=['-std=c++11','-ast-dump=json'])
print('{}'.format(tu))


root = tu.cursor
index=0
indexOfForLoop=0
walker = Walker(fpTempFile)
strResult=walker.getRepresentASTFromFile(fpTempFile,indexTu)
print(strResult)
# # walker.walkInForLoop(root,index,indexOfForLoop)
# # print('size {} {} '.format(len(walker.listForLoops),walker.listForLoops[0].lineNumber))