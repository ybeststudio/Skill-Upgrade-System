# Ara:
	import uiPetInfo
import uiCompanion

# Altina ekle:
import uiSkillUpgrade


# Interface.__init__ icinde ara:
		self.wndExpandedTaskBar = None
		self.wndCompanion = None

# Altina ekle:
		self.wndSkillUpgrade = None


# Interface.__MakeWindows icinde ara:
		self.wndCompanion.BindInterface(self)
		self.wndCompanion.Hide()

# Altina ekle:
		if app.ENABLE_SKILL_UPGRADE:
			self.wndSkillUpgrade = uiSkillUpgrade.SkillUpgradeWindow()
			self.wndSkillUpgrade.BindInterface(self)
			self.wndSkillUpgrade.Hide()


# Interface.Close icinde ara:
			self.wndCompanion.Destroy()
			self.wndCompanion = None

# Altina ekle:
		if self.wndSkillUpgrade:
			self.wndSkillUpgrade.Destroy()
			self.wndSkillUpgrade = None


# Interface icinde ara:
				else:
					self.wndPetInfoWindow.Close()

# Altina ekle:
	def OpenSkillUpgrade(self, upgradeType = None, skillIndex = 0):
		if self.wndSkillUpgrade and False == player.IsObserverMode():
			self.wndSkillUpgrade.Open(upgradeType, skillIndex)

	def ToggleSkillUpgrade(self):
		if self.wndSkillUpgrade and False == player.IsObserverMode():
			self.wndSkillUpgrade.Toggle()

	def GetSkillUpgradeWnd(self):
		return self.wndSkillUpgrade


# Interface icinde ara:
		if self.wndBraveCape:
			self.wndBraveCape.OnMapLoaded()

# Altina ekle:
	def SetSkillUpgradeInfo(self, *args):
		if self.wndSkillUpgrade:
			self.wndSkillUpgrade.SetUpgradeInfo(*args)

	def SendSkillUpgradeResult(self, result):
		if self.wndSkillUpgrade:
			self.wndSkillUpgrade.ShowResult(result)

	def SkillUpgradeNegativeGradeConfirm(self):
		if self.wndSkillUpgrade:
			self.wndSkillUpgrade.ShowNegativeGradeConfirmDialog()

	def SkillUpgradeRefresh(self):
		if self.wndSkillUpgrade:
			self.wndSkillUpgrade.Refresh()

