import random
lstString=['XS','XXS','XAAX','ABBA','LOVE']
n=100
lstOutput=[]
lstOutput.append(str(n))
for i in range(0,(2*n)):
    strItem=random.choice(lstString)
    lstOutput.append(strItem)
fpText='../../../dataPapers/inputParallel.txt'
fff=open(fpText,'w')
fff.write('\n'.join(lstOutput))
fff.close()