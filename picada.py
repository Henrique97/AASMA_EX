import re

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
		#chega a um node e este nao tem/tem subnodes dos quais nenhum é o correto
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
	num_decisions=text[2]
	
'''
#decide-rational (T1=[A=(60%,3),B=(40%,-1)],T2=[A=(30%,0),B=(70%,1)]) 1
#decide-rational (T1=[A=(60%,3),B=(40%,-1)],T2=[A=(4,0),B=(6,1)]) 1
decide-rational (T1=[A=(60%,3),B=(40%,-1)],T2=[A=(30%,0),B=(40%,[B1=(80%,[X=(20%,1),Y=(80%,2)]),B2=(20%,3)]),C=(30%,2)],T3=[A=(100%,1)]) 1


'''
