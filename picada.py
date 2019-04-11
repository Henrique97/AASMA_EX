import re
from linprog import linsolve
import math

num_decisions = 0
tasks=[]
iString=0
level=0
newString= ''

class SingAgent():
	def Choose(self):
		return
	def getTaskUtilityPercentages(self, b1, b2):
		return
	def getTaskUtilityEvidences(self, b1, b2):
		return
	def ChooseAndReadEvidence(self): 
		return
	def PresentResult(self):
		return
	
class Option():
	isPercent = False;
	Observations = None;
	isTask=False;
	Utility = [];
	Name = ''
	Level = 0
	def changeName(self, name):
		self.Name=name
	def changeIsPercent(self, flag):
		self.isPercent=flag
	def changeLevel(self, level):
		self.Level=level
	def changeIsTask(self, flag):
		self.isTask=flag
	def getisTask(self):
		return self.isTask
	def getName(self):
		return (self.Name)
	def getisPercent(self):
		return (self.isPercent)
	def getUtility(self):
		return (self.Utility)
	def getObs(self):
		return (self.Observations)
	def changeUtility(self, utility):
		self.Utility = utility
	def changeObservations(self, obs):
		self.Observations = obs
	def calculateUtility(self, obs=None):
		if (type(self.Utility) == int or type(self.Utility) == float ):
			if (self.isPercent):
				return self.Utility * self.Observations/100.0
			else:
				return self.Utility * self.Observations/obs
		elif (type(self.Utility)==list):
			counter=0
			if(self.Utility[0].getisPercent()):
				for option in self.Utility:
					counter+=option.calculateUtility()
			else:
				childObs=0
				for option in self.Utility:
					childObs+=option.getObs()
				for option in self.Utility:
					counter+=option.calculateUtility(childObs)
			if(self.isTask):
				return counter
			else:
				if (self.isPercent):
					return counter * self.Observations/100.0
				else:
					return counter * self.Observations/obs

def evaluateString():
	global level
	global newString
	#falta guardar opcao
	options = []
	new=Option()
	while True:
		#ve virgula logo nova opcao
		if(newString[0]==","):
			newString=newString[1:]
			new=Option()
		if(newString[0]==")"):
			newString=newString[1:]
			options.append(new)
			new=Option()
		m=re.compile('[A-Z]=|[A-Z]\d=').match(newString)
		if(m!=None):
			new.changeName(m.group()[0:len(m.group())-1])
			new.changeLevel(level)
			newString=newString[m.end()+1:]		
		m=re.compile('\d+%,').match(newString)
		if(m!=None):
			new.changeIsPercent(True)
			new.changeObservations(int(m.group()[0:len(m.group())-2]))
			newString=newString[m.end():]
			#percent
		m=re.compile('\d+,').match(newString)
		if (m!=None):
			new.changeObservations(int(m.group()[0:len(m.group())-1]))
			newString=newString[m.end():]
			#evidence
		m=re.compile("\\[").match(newString)
		if(m!=None):
			newString=newString[1:]
			level+=1
			new.changeUtility(evaluateString())	
		m=re.compile('\d+\\)|-\d+\\)').match(newString)
		if(m!=None):
			new.changeUtility(int(m.group()[0:len(m.group())-1]))
			newString=newString[m.end()-1:]
		m=re.compile('\d+.\d+\\)|-\d+.\d+\\)').match(newString)
		if(m!=None):
			new.changeUtility(float(m.group()[0:len(m.group())-1]))
			newString=newString[m.end()-1:]
		m=re.compile("\\]").match(newString)
		if(m!=None):
			level-=1
			newString=newString[1:]
			return options	

def evaluateObservation(text):
	text=text[1:]
	solution=[]
	m=re.compile('\d+,|-\d+,').match(text)
	if(m!=None):
		solution.append(int(m.group()[0:len(m.group())-1]))
		text=text[m.end():]
	m=re.compile('\d+.\d+,|-\d+.\d+,').match(newString)
	if(m!=None):
		solution.append(float(m.group()[0:len(m.group())-1]))
		text=text[m.end():]
	action=[]
	while(True):
		if(text[0]==")"):
			break
		elif(text[0]=="."):
			text=text[1:]
		m=re.compile('[A-Z]\d+|[A-Z]').match(text)
		if(m!=None):
			action.append((m.group()[0:len(m.group())]))
			text=text[m.end():]
	solution.append(action)
	return solution
	
def process(stringArg, tasks):
	global newString
	tasksText=[]
	p=re.compile('T\d+=\\[|T\d+\|T\d+=\\[')
	m= p.finditer(stringArg)
	for match in m:
		tasksText.append(match.span())
	for beginning in range(0, len(tasksText)-1):
		new=Option()
		new.changeName(stringArg[tasksText[beginning][0]:(tasksText[beginning][1]-2)])
		new.changeIsTask(True)
		newString=stringArg[tasksText[beginning][1]:(tasksText[beginning+1][0]-1)]
		new.changeUtility(evaluateString())
		tasks.append(new)
	new=Option()
	new.changeName(stringArg[tasksText[-1][0]:(tasksText[-1][1]-2)])
	new.changeIsTask(True)
	newString=stringArg[tasksText[-1][1]:(len(stringArg)-1)]
	new.changeUtility(evaluateString())
	tasks.append(new)
	return

def searchNode(node, observation):
	for option in node.getUtility():
		if option.getName() == observation[1][0]:
			return option
	return None

def checkDelete(option,notToDelete):
	if(option.getisPercent()):
		if (type(option.getUtility)==list):
			if (not option.getUtility[0].getisPercent()):
				option.changeObservations(0)
				option.changeIsPercent(False)
				notToDelete.append(option)
				return
		else:
			return
	else:
		notToDelete.append(option)

def processObservation(tasks,observation,choice):
	task=tasks[choice[1]]
	parent_node=task
	son_node=searchNode(task,observation)
	#procura 1 de profundidade
	if(son_node==None):
		notToDelete=[]
		for option in parent_node.getUtility():
			checkDelete(option,notToDelete)
		new=Option()
		new.changeName(observation[1][0])
		new.changeObservations(1)
		nodeToAdd=new
		old=new
		while (len(observation[1])>1):
			observation[1]=observation[1][1:]
			vec = []
			new=Option()
			new.changeName(observation[1][0])
			new.changeObservations(1)
			vec.append(new)
			old.changeUtility(vec)
			old=new
		old.changeUtility(observation[0])
		notToDelete.append(nodeToAdd)
		parent_node.changeUtility(notToDelete)
	#mais do que 1 de profundidade	
	else:
		while (son_node != None and len(observation[1])>1):
			parent_node=son_node
			observation[1]=observation[1][1:]
			if(type(son_node.Utility)!=list):
				son_node=None
				break
			son_node=searchNode(parent_node,observation)
		#chega ao node final que corresponde ao correto
		if (son_node != None and len(observation[1])==1) :
			parent_node=son_node
			if (not son_node.getisPercent()):
				son_node.changeObservations(parent_node.getObs()+1)
			else:
				son_node.changeObservations(1)
			son_node.changeUtility(observation[0])
		#chega a um node e este nao tem/tem subnodes dos quais nenhum e o correto
		elif(son_node == None):
			notToDelete=[]
			#se tiver subnodes
			if(type(parent_node.Utility)==list):
				for option in parent_node.getUtility():
					checkDelete(option,notToDelete)
			new=Option()
			new.changeName(observation[1][0])
			new.changeObservations(1)
			nodeToAdd=new
			old=new
			while (len(observation[1])>1):
				observation[1]=observation[1][1:]
				vec = []
				new=Option()
				new.changeName(observation[1][0])
				new.changeObservations(1)
				vec.append(new)
				old.changeUtility(vec)
				old=new
			old.changeUtility(observation[0])
			notToDelete.append(nodeToAdd)
			parent_node.changeUtility(notToDelete)

def getTaskUtility(tasks):
	f = 0
	utilities=[]
	for task in tasks:
		utilities.append(task.calculateUtility())
	return [tasks[utilities.index(max(utilities))].getName(),utilities.index(max(utilities))]

def getAvgPlusMinTaskUtility(tasks):
	result=[]
	for task in tasks:
		Avg=task.calculateUtility()
		utilities = []
		for option in task.getUtility():
			utilities.append(option.getUtility())
		minVal = min(utilities)
		utilities=[minVal,Avg]
		result.append(utilities)
	flagHasPositive=False
	globalMinMax=-9999
	#globalMinMax=9999
	for task in result:
		if(task[0]>0):
			flagHasPositive=True
			break
		else:
			if(task[0]<0 and globalMinMax<task[0]):
				globalMinMax=task[0]
			'''if(task[0]<globalMinMax):
				globalMinMax=task[0]'''	
	if(not flagHasPositive):
		for task in result:
			task[0]+=(globalMinMax * -1.0 + 0.0000001)
			task[1]+=(globalMinMax * -1.0)
	return result

def getRiskChoicesByMinMax(results,tasks):
	A = [[]]
	C=[]	
	B=[0]
	resultsFiltered=[]
	correspondence=[]
	for i in range(len(results)):
		if len(resultsFiltered)==0:
			resultsFiltered.append(results[i])
			correspondence.append(len(resultsFiltered)-1)
		else:
			for j in range(len(resultsFiltered)):
				if(results[i][1]==resultsFiltered[j][1] and results[i][0]==resultsFiltered[j][0]):
					correspondence.append(j)
					break
				elif(results[i][1]==resultsFiltered[j][1] and results[i][0]>=0):
					correspondence.append(j)
					break
				elif (j==(len(resultsFiltered)-1)):
					resultsFiltered.append(results[i])
					correspondence.append(len(resultsFiltered)-1)
	for task in resultsFiltered:
		A[0].append(task[0]*-1.0)
		C.append(task[1]*-1.0)
	#all bigger than 0
	for i in range(len(resultsFiltered)):
		line=[]
		for j in range(len(resultsFiltered)):
			if(j==i):
				line.append(-1)
			else:
				line.append(0)
		A.append(line)
		B.append(0)
	for i in range(len(resultsFiltered)):
		line=[]
		for j in range(len(resultsFiltered)):
			if(j==i):
				line.append(1)
			else:
				line.append(0)
		A.append(line)
		B.append(1)
	D=[]
	E=[1]
	line=[]
	for i in range(len(resultsFiltered)):
		line.append(1)
	D.append(line)
	'''
	print(correspondence)
	print(results)
	print(A,"\n",B,"\n",C,"\n",D,"\n",E,"\n")
	'''
	resolution, sol = linsolve( C, ineq_left = A, ineq_right = B, eq_left=D, eq_right=E)
	
	#[[percent,task], ...]
	finalResult="("
	num_of_equals=[]
	
	for i in range(len(sol)):
		counter=0
		for j in range(len(correspondence)):
			if (correspondence[j]==i):
				counter+=1
		num_of_equals.append(counter)
	for i in range(len(correspondence)):
		if(round(sol[correspondence[i]],2)!=0.0):
			finalResult+= "{:.2f}".format(round(sol[correspondence[i]]/num_of_equals[correspondence[i]],2)) + ","
			finalResult+=tasks[i].getName() + ";"
		if(i==(len(correspondence)-1)):
			finalResult=finalResult[:len(finalResult)-1]
			finalResult+=")"
	print(finalResult)	
		
def buildNashMatrix(mineTasks,peerTasks):
	line=[]
	matrix=[]
	mineCounter=0
	peerCounter=0
	p=re.compile('T\d+\|')
	taskName=(p.search(mineTasks[0].getName())).group()
	for i in range(len(mineTasks)):
		if(taskName!=p.search(mineTasks[i].getName()).group()):
			break
		else:
			peerCounter+=1
	for i in range(len(peerTasks)):
		if(taskName!=p.search(peerTasks[i].getName()).group()):
			break
		else:
			mineCounter+=1
	for i in range(int(len(mineTasks))):
		line.append([mineTasks[i].calculateUtility()])
		if((i+1)%peerCounter==0):
			matrix.append(line)
			line=[]
	collumn=[]
	for i in range(int(len(peerTasks))):
		collumn.append(peerTasks[i].calculateUtility())
		if((i+1)%mineCounter==0):
			for j in range(mineCounter):
				matrix[j][(i)//mineCounter].append(collumn[j])
			collumn=[]
	return matrix
			
def getNashPositions(matrix):
	nashCells=[]
	maxForEachLine=[]
	maxForEachCollumn=[]
	for i in range((len(matrix))):
		maxValCol=matrix[i][0][1]
		collumnMax=[]
		for j in range((len(matrix[0]))):
			maxValLine=matrix[i][j][0]
			if(matrix[i][j][1]>maxValCol):
				collumnMax=[[i,j]]
				maxValCol=matrix[i][j][1]
			elif(matrix[i][j][1]==maxValCol):
				collumnMax.append([i,j])
		maxForEachCollumn.append(collumnMax)
	for i in range((len(matrix[0]))):
		maxValLine=matrix[0][i][0]
		lineMax=[]
		for j in range((len(matrix))):
			if(matrix[j][i][0]>maxValLine):
				lineMax=[[j,i]]
				maxValLine=matrix[j][i][0]
			elif(matrix[j][i][0]==maxValLine):
				lineMax.append([j,i])
		maxForEachLine.append(lineMax)
	for i in range(len(maxForEachCollumn)): #tamanho colunas
		for j in range(len(maxForEachCollumn[i])): #tamanho linhas
			for k in range(len(maxForEachLine[maxForEachCollumn[i][j][1]])):
				mineAction=maxForEachLine[maxForEachCollumn[i][j][1]]
				if(i==mineAction[k][0] and maxForEachCollumn[i][j][1]==mineAction[k][1]):
					nashCells.append(maxForEachCollumn[i][j])
	return nashCells
	
'''
	for i in range((len(matrix))):
		maxValLine=matrix[i][0][0]
		lineMax=[]
		maxValCol=matrix[0][i][1]
		collumnMax=[]
		for j in range((len(matrix))):
			if(matrix[i][j][0]==maxValLine):
				lineMax.append([i,j])
			elif(matrix[i][j][0]>maxValLine):
				lineMax=[[i,j]]
				maxValLine=matrix[i][j][0]
			if(matrix[j][i][1]==maxValCol):
				collumnMax.append([j,i])
			elif(matrix[j][i][1]>maxValCol):
				collumnMax=[[j,i]]
				maxValCol=matrix[j][i][1]
		maxForEachLine.append(lineMax)
		maxForEachCollumn.append(collumnMax)
	print(maxForEachLine)
	print(maxForEachCollumn)
'''		
		

text=input()
text=text.split()

if text[0] == 'decide-rational':
	num_decisions=int(text[2])
	process(text[1], tasks)
	choice=getTaskUtility(tasks)
	print(choice[0])
	if(num_decisions>1):
		for i in range (1,num_decisions):
			text=input()
			observation=evaluateObservation(text)
			processObservation(tasks,observation,choice)
			choice = getTaskUtility(tasks)
			print(choice[0])
	
if text[0] == 'decide-risk':
	process(text[1], tasks)
	#nao aparentam existir subniveis
	#ver tasks com max utility sem ser negativa e com max utility com negativa retorna vetor com task1=[min max]
	results=getAvgPlusMinTaskUtility(tasks)
	getRiskChoicesByMinMax(results,tasks)
	#choices (0.50,T1;0.50,T2)

if text[0] == 'decide-conditional':
	mineText=text[1][6:]
	mineTasks=[]
	peerTasks=[]
	p=re.compile(',peer=\(')
	m= p.search(mineText)
	peerText=mineText[m.end():]
	mineText=mineText[:m.start()]
	process(mineText, mineTasks)
	process(peerText, peerTasks)
	
	matrix=buildNashMatrix(mineTasks,peerTasks)
	nashPositions=getNashPositions(matrix)
	if(len(nashPositions)==0):
		if( (matrix[0][0][0]-matrix[0][1][0]-matrix[1][0][0]+matrix[1][1][0]) != 0 and (matrix[0][0][1]-matrix[1][0][1]-matrix[0][1][1]+matrix[1][1][1])!=0):
			peerT0prob=(matrix[1][1][0]-matrix[0][1][0])/(matrix[0][0][0]-matrix[0][1][0]-matrix[1][0][0]+matrix[1][1][0])
			mineT0prob=(matrix[1][1][1]-matrix[1][0][1])/(matrix[0][0][1]-matrix[1][0][1]-matrix[0][1][1]+matrix[1][1][1])
			if(peerT0prob>=0 and peerT0prob<=1 and mineT0prob>=0 and mineT0prob<=1):
				print("mine=(" + "{:.2f}".format(round(mineT0prob,2)) +","+"{:.2f}".format(round(1-mineT0prob,2))+")" + ","+ "peer=(" + "{:.2f}".format(round(peerT0prob,2)) +","+"{:.2f}".format(round(1-peerT0prob,2)) +")")
			else:
				print("blank-decision")
		else: 
			print("blank-decision")
	else:
		payoffMaxIndex=0
		payoffMax=matrix[nashPositions[0][0]][nashPositions[0][1]][0] + matrix[nashPositions[0][0]][nashPositions[0][1]][1]
		for i in range(len(nashPositions)):
			xcoord=nashPositions[i][0]
			ycoord=nashPositions[i][1]
			if((matrix[xcoord][ycoord][0]+matrix[xcoord][ycoord][1])>payoffMax or (matrix[xcoord][ycoord][0]+matrix[xcoord][ycoord][1]==payoffMax and xcoord<nashPositions[payoffMaxIndex][0])):
				payoffMax=matrix[xcoord][ycoord][0]+matrix[xcoord][ycoord][1]
				payoffMaxIndex=i
		xcoord=nashPositions[payoffMaxIndex][0]
		ycoord=nashPositions[payoffMaxIndex][1]
		posMine= int((ycoord)* math.sqrt(len(mineTasks)) + xcoord)
		posPeer= int((xcoord)* math.sqrt(len(mineTasks)) + ycoord)
		taskM=mineTasks[posPeer].getName()
		taskP=peerTasks[posMine].getName()
		p=re.compile('T\d+')
		taskM=p.match(taskM)
		taskP=p.match(taskP)
		print("mine=" + taskM.group() + ","+ "peer=" + taskP.group())

if text[0] == 'decide-mixed':
	mineText=text[1][6:]
	mineTasks=[]
	peerTasks=[]
	p=re.compile(',peer=\(')
	m= p.search(mineText)
	peerText=mineText[m.end():]
	mineText=mineText[:m.start()]
	process(mineText, mineTasks)
	process(peerText, peerTasks)
	
	matrix=buildNashMatrix(mineTasks,peerTasks)
	if( (matrix[0][0][0]-matrix[0][1][0]-matrix[1][0][0]+matrix[1][1][0]) != 0 and (matrix[0][0][1]-matrix[1][0][1]-matrix[0][1][1]+matrix[1][1][1])!=0):
		peerT0prob=(matrix[1][1][0]-matrix[0][1][0])/(matrix[0][0][0]-matrix[0][1][0]-matrix[1][0][0]+matrix[1][1][0])
		mineT0prob=(matrix[1][1][1]-matrix[1][0][1])/(matrix[0][0][1]-matrix[1][0][1]-matrix[0][1][1]+matrix[1][1][1])
		
		if(peerT0prob>=0 and peerT0prob<=1 and mineT0prob>=0 and mineT0prob<=1):
			print("mine=(" + "{:.2f}".format(round(mineT0prob,2)) +","+"{:.2f}".format(round(1-mineT0prob,2))+")" + ","+ "peer=(" + "{:.2f}".format(round(peerT0prob,2)) +","+"{:.2f}".format(round(1-peerT0prob,2)) +")")
		else:
			print("blank-decision")
	else: 
		print("blank-decision")
	#x=([1,1]-[1,0])/([0,0]-[1,0]+[1,1]-[0,1])
	
if text[0] == 'decide-nash':
	mineText=text[1][6:]
	mineTasks=[]
	peerTasks=[]
	p=re.compile(',peer=\(')
	m= p.search(mineText)
	peerText=mineText[m.end():]
	mineText=mineText[:m.start()]
	process(mineText, mineTasks)
	process(peerText, peerTasks)
	
	matrix=buildNashMatrix(mineTasks,peerTasks)
	nashPositions=getNashPositions(matrix)
	if(len(nashPositions)==0):
		print("blank-decision")
	else:
		payoffMaxIndex=0
		payoffMax=matrix[nashPositions[0][0]][nashPositions[0][1]][0] + matrix[nashPositions[0][0]][nashPositions[0][1]][1]
		for i in range(len(nashPositions)):
			xcoord=nashPositions[i][0]
			ycoord=nashPositions[i][1]
			if((matrix[xcoord][ycoord][0]+matrix[xcoord][ycoord][1])>payoffMax or (matrix[xcoord][ycoord][0]+matrix[xcoord][ycoord][1]==payoffMax and xcoord<nashPositions[payoffMaxIndex][0])):
				payoffMax=matrix[xcoord][ycoord][0]+matrix[xcoord][ycoord][1]
				payoffMaxIndex=i
		xcoord=nashPositions[payoffMaxIndex][0]
		ycoord=nashPositions[payoffMaxIndex][1]
		posMine= int((ycoord)* math.sqrt(len(mineTasks)) + xcoord)
		posPeer= int((xcoord)* math.sqrt(len(mineTasks)) + ycoord)
		taskM=mineTasks[posPeer].getName()
		taskP=peerTasks[posMine].getName()
		p=re.compile('T\d+')
		taskM=p.match(taskM)
		taskP=p.match(taskP)
		print("mine=" + taskM.group() + ","+ "peer=" + taskP.group())
