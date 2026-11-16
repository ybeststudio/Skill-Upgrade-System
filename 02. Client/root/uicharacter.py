# CharacterWindow.__LoadWindow icinde ara:
			self.__BindObject()
			self.__BindEvent()

# Altina ekle:
			if app.ENABLE_SKILL_UPGRADE:
				self.__CreateSkillUpgradeButton()


# CharacterWindow.__OnClickSkillUpgrade icinde ara:
		interface = constInfo.GetInterfaceInstance()
		if interface:

# Altina ekle:
			interface.ToggleSkillUpgrade()

