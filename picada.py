import re

num_decisions = 0
tasks=[]
iString=0

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

class Task():
	options=[];
	def searchAndAddOption(self):
		return
	def cleanOptions(self):
		return
	def CalcUtility(self):
		return
	
class Option():
	isPercent = False;
	Observations = None;
	Utility = [];
	Name = ''
	Level = 0
	def changeName(self, name):
		self.Name=name
	def changeIsPercent(self, boolVal):
		self.isPercent=boolVal
	def changeLevel(self, level):
		self.Level=level
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
	def calculateUtility(self):
		if (type(self.Utility) == int):
			return self.Utility * self.Observations/100.0
		elif (type(self.Utility)==list):
			counter=0
			for option in self.Utility:
				counter+=option.calculateUtility()
			return counter
		else:
			return self.Utility.calculateUtility() * self.Observations/100.0
level=0
newString= ''
def evaluateString():
	global level
	global newString
	#falta guardar opçao
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
			print(m.group()[0:len(m.group())])
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
		m=re.compile("\\]").match(newString)
		if(m!=None):
			level-=1
			newString=newString[1:]
			return options	
	
def process(stringArg, tasks):
	global newString
	tasksText=[]
	p=re.compile('T\d+=\\[')
	m= p.finditer(stringArg)
	for match in m:
		tasksText.append(match.span())
	for beginning in range(0, len(tasksText)-1):
		newString=stringArg[tasksText[beginning][1]:(tasksText[beginning+1][0]-1)]
		tasks.append(evaluateString())
	newString=stringArg[tasksText[-1][1]:(len(stringArg)-1)]
	tasks.append(evaluateString())
	return

def getTaskUtility(tasks):
	f = 0
	utilidades=[]
	for i in tasks:
		f = 0
		for option in i:
			print(option.getName())
			f+=option.calculateUtility()
		utilidades.append(f)
	print(utilidades)
		
text=input()
text=text.split()

if text[0] == 'decide-rational':
	num_decisions=text[2]
	process(text[1], tasks)
	getTaskUtility(tasks)

if text[0] == 'decide-risk':
	num_decisions=text[2]
