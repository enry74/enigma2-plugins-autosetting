########
## HeartBeatService class
## credits @ livewinter
#######

import os,urllib2,sys,json,uuid,time
from Tools.HardwareInfo import HardwareInfo

class HeartBeatService():



	def __init__(self, version):
		self.info = {
			"uid" : 0,
			"stb_model" : 0,
	   		"firmware_version" : 0,
			"vas_installed" : 0,
			"vas_upgraded" : 0,
			"vas_version": 0,
		}
		
		self.vas_version = version

		self.infoLocation = "/home/vas/info"
		
		if not self.infoExists():
			self.createInfo()	
			self.storeInfo()
			self.sendInfo()				
		else:
			self.info = self.loadInfo()
			if (self.vas_version != self.info["vas_version"]):
				self.updateInfo()	
	
	def loadInfo(self):

		infofile = open(self.infoLocation, 'r')
		infofilejson = infofile.read()
		return json.loads(infofilejson)

		
	def createInfo(self):

		uid = self.createUid()
		hw = HardwareInfo()
		stb_model = hw.get_device_name()
		firmware_version = os.popen("cat /etc/issue.net").read()
		
		#testing time bug, restore to
		#vas_installed = int(time.time())
   		self.now = time.time()
		vas_installed = int(self.now)
		

		self.info["uid"] = str(uid)
		self.info["stb_model"] = stb_model
		self.info["firmware_version"] = firmware_version
		self.info["vas_installed"] = vas_installed
		self.info["vas_version"] = self.vas_version

		os.system("mkdir -p /home/vas/");
		
	def createUid(self):

		#creates random code
		return uuid.uuid4()


	def infoExists(self):

		if os.path.exists(self.infoLocation):
			try:
				info = self.loadInfo()
				if info["uid"] != 0:
					return True
			except:
				pass
		return False

	def updateInfo(self):

		self.info["vas_version"] = self.vas_version
		self.info["vas_upgraded"] = int(time.time())
		self.storeInfo()
		


	#def destroyInfo():

	def storeInfo(self):
		
		infofile = open(self.infoLocation, 'w+')
		infofile.write(json.dumps(self.info))
			
		

	def sendInfo(self):
		req = urllib2.Request('http://vas-heartbeat.livewinter.com/api/new-device')
		req.add_header('Content-Type', 'application/json')
		fileinfojson = self.loadInfo()

		#test to check time.time bug (needs to be removed)
		fileinfojson["time_full"] = self.now	
		fileinfojson["python_version"]  = sys.version
		fileinfojson["system_date"]  = os.popen("date").read()

		fileinfojson = json.dumps(fileinfojson)
		response = urllib2.urlopen(req, fileinfojson)


