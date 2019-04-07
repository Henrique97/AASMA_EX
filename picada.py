import re
from linprog import linsolve

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
'''
class Task():
	Name = ''
	options=[];
	def searchAndAddOption(self):
		return
	def cleanOptions(self):
		return
	def CalcUtility(self):
		return
	def setOptions(self, optionsRec):
		self.options=optionsRec
	def setName(self,NameTask):
		self.Name=NameTask
	def getName(self):
		return self.Name
'''
	
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
	p=re.compile('T\d+=\\[')
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
				if(results[i][1]==resultsFiltered[j][1]):
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
		if(sol[correspondence[i]]!=0.0):
			finalResult+= "{:.2f}".format(round(sol[correspondence[i]]/num_of_equals[correspondence[i]],2)) + ","
			finalResult+=tasks[i].getName() + ";"
		if(i==(len(correspondence)-1)):
			finalResult=finalResult[:len(finalResult)-1]
			finalResult+=")"
	print(finalResult)
			
		
		

'''	
	MaxVal=None
	MaxValNonNeg=None
	MaxIndexes=[]
	MaxNonNegIndexes=[]
	#falta caso em que o maior non neg pode nao balancar um negativo pq o min e treta
	#falta o caso temos A=avg=2 min=1 vs B=avg=2 min=0 devia ser so A mas sao os dois indexes
	for i in range(len(results)):
		if results[i][0]>=0:
			if(MaxValNonNeg==None):
				MaxNonNegIndexes.append(i)
				MaxValNonNeg=results[i][1]
			elif(results[i][1]>MaxValNonNeg):
				MaxNonNegIndexes=[i]
				MaxValNonNeg=results[i][1]
			elif(results[i][1]==MaxValNonNeg):
				MaxNonNegIndexes.append(i)
				MaxValNonNeg=results[i][1]
	for i in range(len(results)):
		if (results[i][0]<0 and results[i][0]+MaxValNonNeg>=0 and results[i][1]>MaxValNonNeg):
			if(MaxVal==None):
				MaxIndexes.append(i)
				MaxVal=results[i][1]
			elif(results[i][1]>MaxVal):
				MaxIndexes=[]
				MaxVal=results[i][1]
			elif(results[i][1]==MaxVal):
				MaxIndexes.append(i)
				MaxVal=results[i][1]
	print("MaxPos")
	for i in MaxNonNegIndexes:
		print(tasks[i].getName())
	print("MaxWithNegs")
	for i in MaxIndexes:
		print(tasks[i].getName())
	return
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
