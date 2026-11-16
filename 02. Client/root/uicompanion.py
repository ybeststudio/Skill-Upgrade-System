# CompanionWindow.__OnPressedSlotButton icinde ara:
	def __OnPressedSlotButton(self, slot):

# Altina ekle:
		if app.ENABLE_SKILL_UPGRADE and self.buffiSkillPower[slot] >= 20 and self.interface:
			self.interface.OpenSkillUpgrade(2, BUFF_SKILL_INDEX[slot])
			return

