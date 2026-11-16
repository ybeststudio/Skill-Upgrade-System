# GameWindow.OnUpdate icinde ara:
	def OnUpdate(self):

# Altina ekle:
		if app.ENABLE_SKILL_UPGRADE:
			import uiSkillUpgrade
			uiSkillUpgrade.CheckAlerts(self.interface)


# GameWindow icinde ara:
		if self.interface and self.interface.wndCompanion:
			self.interface.wndCompanion.SetBuffiSkillColor(int(idx), map(long, (c0, c1, c2, c3, c4)))

# Altina ekle:
	def SkillUpgradeInfo(self, upgradeType, skillIndex, bookVnum, count, progress, need, remain, maxed):
		if self.interface:
			self.interface.SetSkillUpgradeInfo(*map(int, (upgradeType, skillIndex, bookVnum, count, progress, need, remain, maxed)))

	def SkillUpgradeResult(self, result):
		if self.interface:
			self.interface.SendSkillUpgradeResult(int(result))

	def SkillUpgradeNegativeGradeConfirm(self):
		if self.interface:
			self.interface.SkillUpgradeNegativeGradeConfirm()


# GameWindow.__ServerCommand_Build icinde ara:
			"SetSupportCastSpeed"							: self.SetSupportCastSpeed,
			"SupportEvolutionResult"						: self.SupportEvolutionResult,

# Altina ekle:
			"SkillUpgradeInfo"								: self.SkillUpgradeInfo,
			"SkillUpgradeResult"							: self.SkillUpgradeResult,
			"SkillUpgradeNegativeGradeConfirm"				: self.SkillUpgradeNegativeGradeConfirm,

