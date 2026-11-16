import app
import net
import player
import ui
import uiToolTip
import grpText
import uiSkillColor
import mouseModule
import localeInfo
import constInfo
import item
import skill
import chat
import uicompanionmount

COMPANION_PATH = "d:/ymir work/ui/game/companion{}"

PET_WIDTH = 280
PET_HEIGHT = 415

TAB_PET = 0
TAB_HORSE = 1
TAB_BUFFI = 2

BUFFI_SEAL_VNUM = 57100
BUFFI_ORE_VNUM = 57101
BUFFI_ORE_PERM_VNUM = 57103
BUFF_SKILL_INDEX = (94, 95, 96, 110, 111)
BUFFI_INT_STAGES = (120, 140, 160, 180)
BUFFI_DURATION_MAX = 30 * 24 * 60 * 60

# (name, name G, name P, description, condition 1, condition 2, value line)
BUFFI_SKILL_TOOLTIP = (
	(localeInfo.BUFFI_SKILL_1_NAME, localeInfo.BUFFI_SKILL_1_NAME_G, localeInfo.BUFFI_SKILL_1_NAME_P, localeInfo.BUFFI_SKILL_1_DESC, localeInfo.BUFFI_SKILL_COND_SELF_BUFF, localeInfo.BUFFI_SKILL_1_COND, localeInfo.BUFFI_SKILL_1_VALUE),
	(localeInfo.BUFFI_SKILL_2_NAME, localeInfo.BUFFI_SKILL_2_NAME_G, localeInfo.BUFFI_SKILL_2_NAME_P, localeInfo.BUFFI_SKILL_2_DESC, localeInfo.BUFFI_SKILL_COND_SELF_BUFF, localeInfo.BUFFI_SKILL_2_COND, localeInfo.BUFFI_SKILL_2_VALUE),
	(localeInfo.BUFFI_SKILL_3_NAME, localeInfo.BUFFI_SKILL_3_NAME_G, localeInfo.BUFFI_SKILL_3_NAME_P, localeInfo.BUFFI_SKILL_3_DESC, localeInfo.BUFFI_SKILL_COND_SELF_BUFF, localeInfo.BUFFI_SKILL_3_COND, localeInfo.BUFFI_SKILL_3_VALUE),
	(localeInfo.BUFFI_SKILL_4_NAME, localeInfo.BUFFI_SKILL_4_NAME_G, localeInfo.BUFFI_SKILL_4_NAME_P, localeInfo.BUFFI_SKILL_4_DESC, localeInfo.BUFFI_SKILL_4_COND, localeInfo.BUFFI_SKILL_4_COND_SELF, localeInfo.BUFFI_SKILL_4_VALUE),
	(localeInfo.BUFFI_SKILL_5_NAME, localeInfo.BUFFI_SKILL_5_NAME_G, localeInfo.BUFFI_SKILL_5_NAME_P, localeInfo.BUFFI_SKILL_5_DESC, localeInfo.BUFFI_SKILL_5_COND, localeInfo.BUFFI_SKILL_5_COND_PARTY, localeInfo.BUFFI_SKILL_5_VALUE),
)
BUFFI_INT_POWERED = localeInfo.BUFFI_INT_POWERED
BUFFI_GRADE_SUFFIX = ("", localeInfo.BUFFI_GRADE_MASTER, localeInfo.BUFFI_GRADE_GRAND_MASTER, localeInfo.BUFFI_GRADE_PERFECT_MASTER)
BUFFI_SKILL_VALUE = (
	(localeInfo.BUFFI_SKILL_1_VALUE,),
	(localeInfo.BUFFI_SKILL_2_VALUE,),
	(localeInfo.BUFFI_SKILL_3_VALUE_TOOLTIP,),
	(localeInfo.BUFFI_SKILL_4_VALUE_TOOLTIP, localeInfo.BUFFI_SKILL_4_CAST_VALUE_TOOLTIP,),
	(localeInfo.BUFFI_SKILL_5_VALUE,),
)
BUFFI_TT_WHITE = 0xffffffff
BUFFI_TT_GREEN = 0xff8cf07a
BUFFI_TT_YELLOW = 0xfff0d878

g_buffiState = {"level": 0, "duration": 0, "time": 0.0, "skills": [0] * 5, "points": 0}

BONUS_ROW_HEIGHT = 27
BONUS_VISIBLE_ROWS = 2




def _SkillGrade(level):
	if level >= 40:
		return 3, 1
	if level >= 30:
		return 2, level - 29
	if level >= 20:
		return 1, level - 19
	return 0, level


def _FormatTime(sec):
	d = sec / 86400
	h = (sec % 86400) / 3600
	m = (sec % 3600) / 60
	if d > 0:
		return localeInfo.PET_SEAL_TIME_DHM % (d, h, m)
	if h > 0:
		return localeInfo.AUTO_SA_DK % (h, m)
	return "%ddk." % m


class ThinScrollBar(ui.Window):
	WIDTH = 5

	def __init__(self):
		ui.Window.__init__(self)
		self.eventScroll = None
		self.pos = 0.0
		self.height = 0
		self.barHeight = 10

		frame = ui.Bar()
		frame.SetParent(self)
		frame.SetColor(0xff464646)
		frame.AddFlag("not_pick")
		frame.Show()
		self.frame = frame

		track = ui.Bar()
		track.SetParent(self)
		track.SetPosition(1, 1)
		track.SetColor(0xff000000)
		track.AddFlag("not_pick")
		track.Show()
		self.track = track

		bar = ui.Bar()
		bar.SetParent(self)
		bar.SetColor(0xff6a6a6a)
		bar.AddFlag("not_pick")
		bar.Show()
		self.bar = bar

	def __del__(self):
		ui.Window.__del__(self)

	def SetScrollBarSize(self, height):
		self.height = height
		self.SetSize(self.WIDTH, height)
		self.frame.SetSize(self.WIDTH, height)
		self.track.SetSize(self.WIDTH - 2, height - 2)
		self.__Refresh()

	def SetMiddleBarSize(self, scale):
		self.barHeight = max(8, int((self.height - 2) * min(1.0, scale)))
		self.bar.SetSize(self.WIDTH - 2, self.barHeight)
		self.__Refresh()

	def SetScrollEvent(self, event):
		self.eventScroll = event

	def GetPos(self):
		return self.pos

	def SetPos(self, pos):
		self.pos = max(0.0, min(1.0, pos))
		self.__Refresh()
		if self.eventScroll:
			self.eventScroll()

	def __Refresh(self):
		self.bar.SetPosition(1, 1 + int((self.height - 2 - self.barHeight) * self.pos))

	def OnMouseLeftButtonDown(self):
		x, y = self.GetMouseLocalPosition()
		span = max(1, self.height - 2 - self.barHeight)
		self.SetPos(float(y - 1 - self.barHeight / 2) / span)


class HoverArea(ui.Window):
	def __init__(self, overIn, overOut):
		ui.Window.__init__(self)
		self.overIn = overIn
		self.overOut = overOut

	def __del__(self):
		ui.Window.__del__(self)

	def OnMouseOverIn(self):
		if self.overIn:
			self.overIn()

	def OnMouseOverOut(self):
		if self.overOut:
			self.overOut()


class BuffiSkillColorWindow(uiSkillColor.SkillColorWindow):

	def __init__(self, owner, buffiSlot, skillIndex):
		self.owner = owner
		self.buffiSlot = buffiSlot
		uiSkillColor.SkillColorWindow.__init__(self, buffiSlot, skillIndex)

	def GetSkillColorData(self, skillSlot):
		return list(self.owner.GetBuffiSkillColor(self.buffiSlot))

	def SetSkillColorData(self, skillSlot, c0, c1, c2, c3, c4):
		net.SendChatPacket("/buffi_skill_color %d %d %d %d %d %d" % (self.buffiSlot, c0, c1, c2, c3, c4))


BUFFI_EVOLVE_REQUIREMENTS = {
	0: ((40912, 5), (40812, 5), (40714, 10), (50628, 10), (40914, 3), (26002, 10000000)),
	1: ((40942, 5), (40914, 3), (50632, 10), (40718, 3), (40820, 5), (26002, 50000000)),
	2: ((40917, 10), (40919, 5), (40920, 5), (40718, 5), (40821, 5), (26002, 100000000)),
}
BUFFI_EVOLVE_LEVEL = (55, 75, 90)
BUFFI_MAX_EVOLUTION = 3
EVOLVE_PATH = "d:/ymir work/ui/game/companion/evolve/{}"
EVOLVE_YANG_VNUM = 26002
EVOLVE_COLOR_OK = 0xff8cf07a
EVOLVE_COLOR_LACK = 0xffff5050


class BuffiEvolutionWindow(ui.BoardWithTitleBar):
	WIDTH = 218
	HEIGHT = 334
	SLOT_CENTER = ((41, 14), (101, 14), (161, 14), (71, 82), (131, 82))

	def __init__(self, owner):
		ui.BoardWithTitleBar.__init__(self)
		self.owner = owner
		self.evolution = 0
		self.items = ()
		self.price = 0
		self.keep = []
		self.counts = []
		self.questionDialog = None
		self.updateTime = 0.0
		self.toolTipItem = uiToolTip.ItemToolTip()
		self.toolTipItem.HideToolTip()
		self.__CreateWindow()

	def __del__(self):
		ui.BoardWithTitleBar.__del__(self)

	def Destroy(self):
		self.Close()
		self.keep = []
		self.counts = []
		self.owner = None
		self.toolTipItem = None

	def __Image(self, parent, name, x, y):
		img = ui.ImageBox()
		img.SetParent(parent)
		img.LoadImage(name if name.startswith("d:/") else EVOLVE_PATH.format(name))
		img.SetPosition(x, y)
		img.AddFlag("not_pick")
		img.Show()
		self.keep.append(img)
		return img

	def __Text(self, parent, text, x, y):
		line = ui.TextLine()
		line.SetParent(parent)
		line.SetPosition(x, y)
		line.SetHorizontalAlignCenter()
		line.SetOutline()
		line.SetText(text)
		line.Show()
		self.keep.append(line)
		return line

	def __CreateWindow(self):
		self.SetSize(self.WIDTH, self.HEIGHT)
		self.AddFlag("movable")
		self.AddFlag("float")
		self.SetTitleName(localeInfo.SUPPORT_TITLE_EVOLVE)
		self.SetCloseEvent(ui.__mem_func__(self.Close))

		header = self.__Image(self, "header_bg.png", 8, 32)
		self.evoText = self.__Text(header, "", 101, 4)
		self.levelText = self.__Text(header, "", 101, 18)

		bg = self.__Image(self, "background.png", 8, 68)
		for cx, cy in self.SLOT_CENTER:
			self.__Image(bg, "d:/ymir work/ui/public/slot_base.sub", cx - 16, cy)
			cnt = self.__Image(bg, "count_bg.png", cx - 20, cy + 36)
			self.counts.append(self.__Text(cnt, "", 20, 4))

		slot = ui.SlotWindow()
		slot.SetParent(bg)
		slot.SetPosition(0, 0)
		slot.SetSize(202, 156)
		for i, (cx, cy) in enumerate(self.SLOT_CENTER):
			slot.AppendSlot(i, cx - 16, cy, 32, 32)
		slot.SetOverInItemEvent(ui.__mem_func__(self.__OnSlotOverIn))
		slot.SetOverOutItemEvent(ui.__mem_func__(self.__OnSlotOverOut))
		slot.Show()
		self.slot = slot

		costTitle = self.__Image(self, "cost_title_bg.png", 17, 230)
		self.__Text(costTitle, localeInfo.COMPANION_UPGRADE_PRICE, 92, 3)
		cost = self.__Image(self, "cost_bg.png", 17, 252)
		self.priceText = self.__Text(cost, "", 92, 1)
		chance = self.__Image(self, "bg_chance_success.png", 17, 272)
		self.__Text(chance, localeInfo.COMPANION_EVOLUTION_CANNOT_FAIL, 92, 3)

		btn = ui.Button()
		btn.SetParent(self)
		btn.SetUpVisual("d:/ymir work/ui/public/large_button_01.sub")
		btn.SetOverVisual("d:/ymir work/ui/public/large_button_02.sub")
		btn.SetDownVisual("d:/ymir work/ui/public/large_button_03.sub")
		btn.SetPosition((self.WIDTH - 88) / 2, 300)
		btn.SetText(localeInfo.PET_BTN_EVOLVE)
		btn.SetEvent(ui.__mem_func__(self.__OnClickEvolve))
		btn.Show()
		self.evolveButton = btn

	def Open(self, evolution):
		self.evolution = evolution
		reqs = BUFFI_EVOLVE_REQUIREMENTS.get(evolution, ())
		self.items = tuple(r for r in reqs if r[0] != EVOLVE_YANG_VNUM)
		self.price = sum(r[1] for r in reqs if r[0] == EVOLVE_YANG_VNUM)
		self.evoText.SetText(localeInfo.AUTO_EVRIM % (evolution, evolution + 1))
		self.levelText.SetText(localeInfo.AUTO_GEREKEN_SEVIYE % BUFFI_EVOLVE_LEVEL[evolution])
		for i in xrange(len(self.SLOT_CENTER)):
			if i < len(self.items):
				self.slot.SetItemSlot(i, self.items[i][0], 0)
			else:
				self.slot.ClearSlot(i)
		self.slot.RefreshSlot()
		self.RefreshItemCounts()
		if not self.IsShow() and self.owner:
			x, y = self.owner.GetGlobalPosition()
			self.SetPosition(x + self.owner.GetWidth(), y)
		self.Show()
		self.SetTop()

	def Close(self):
		self.CloseQuestionDialog()
		if self.toolTipItem:
			self.toolTipItem.HideToolTip()
		self.Hide()

	def OnPressEscapeKey(self):
		self.Close()
		return True

	def RefreshItemCounts(self):
		for i, line in enumerate(self.counts):
			if i < len(self.items):
				vnum, need = self.items[i]
				have = player.GetItemCountByVnum(vnum)
				line.SetText("%d/%d" % (min(have, need), need))
				line.SetPackedFontColor(EVOLVE_COLOR_OK if have >= need else EVOLVE_COLOR_LACK)
			else:
				line.SetText("")
		self.priceText.SetText(localeInfo.NumberToMoneyString(self.price))
		self.priceText.SetPackedFontColor(EVOLVE_COLOR_OK if player.GetElk() >= self.price else EVOLVE_COLOR_LACK)

	def OnUpdate(self):
		if app.GetTime() > self.updateTime:
			self.updateTime = app.GetTime() + 0.5
			self.RefreshItemCounts()

	def __OnSlotOverIn(self, index):
		if index < len(self.items) and self.toolTipItem:
			self.toolTipItem.SetItemToolTip(self.items[index][0])

	def __OnSlotOverOut(self):
		if self.toolTipItem:
			self.toolTipItem.HideToolTip()

	def __OnClickEvolve(self):
		import uiCommon
		self.CloseQuestionDialog()
		dlg = uiCommon.QuestionDialog2()
		dlg.SetText1(localeInfo.MOUNT_EVOLVE_CONFIRMATION_1)
		dlg.SetText2(localeInfo.MOUNT_EVOLVE_CONFIRMATION_2)
		dlg.SetAcceptEvent(ui.__mem_func__(self.__SendUpgradeEvolution))
		dlg.SetCancelEvent(ui.__mem_func__(self.CloseQuestionDialog))
		dlg.Open()
		self.questionDialog = dlg

	def __SendUpgradeEvolution(self):
		self.CloseQuestionDialog()
		net.SendChatPacket("/support_set_evolution")

	def CloseQuestionDialog(self):
		if self.questionDialog:
			self.questionDialog.Close()
			self.questionDialog = None


# Requirements = uiCompanion.REFINE_TYPE_REQUIREMENTS (key = current type), must match CGrowthPet::UpgradeType.
PET_TYPE_REQUIREMENTS = {
	1: ((40214, 5), (50628, 10), (27987, 25), (26002, 10000000)),
	2: ((40214, 10), (50632, 10), (40718, 5), (26002, 50000000)),
	3: ((40214, 15), (50634, 10), (40718, 10), (26002, 100000000)),
	4: ((40214, 20), (50635, 10), (40718, 15), (26002, 250000000)),
	5: ((40214, 25), (50602, 5), (40718, 20), (26002, 500000000)),
}
PET_TYPE_MAX = 6
PET_TYPE_PITY_MAX = 3
PET_EVOLVE_REQUIREMENTS = {
	1: (55, ((55005, 10), (40214, 10), (40812, 10), (40912, 5), (40914, 10)), 25000000),
	2: (75, ((55006, 10), (40214, 15), (40718, 10), (40942, 5), (40820, 10)), 100000000),
	3: (90, ((55007, 10), (40214, 20), (40718, 25), (40919, 10), (40920, 10)), 500000000),
}
PET_EVOLUTION_MAX = 4
COMPANION_LABEL_COLOR = 0xffcabdab
COMPANION_VALUE_COLOR = 0xffd1b183


class PetUpgradeTypeWindow(ui.BoardWithTitleBar):
	WIDTH = 215
	HEIGHT = 237
	SLOT_COUNT = 5

	def __init__(self, owner, evolveMode = False):
		self.confirmDialog = None
		ui.BoardWithTitleBar.__init__(self)
		self.owner = owner
		self.mode = evolveMode if isinstance(evolveMode, str) else ("evolve" if evolveMode else "type")
		self.evolveMode = self.mode in ("evolve", "mount")
		self.runeIndex = 0
		self.keep = []
		self.items = ()
		self.price = 0
		self.pity = 0
		self.pityMax = PET_TYPE_PITY_MAX
		self.updateTime = 0.0
		self.toolTipItem = uiToolTip.ItemToolTip()
		self.toolTipItem.HideToolTip()
		self.__CreateWindow()

	def __del__(self):
		ui.BoardWithTitleBar.__del__(self)

	def Destroy(self):
		self.Close()
		self.keep = []
		self.owner = None
		self.toolTipItem = None

	def __Image(self, parent, path, x, y):
		img = ui.ImageBox()
		img.SetParent(parent)
		img.LoadImage(path)
		img.SetPosition(x, y)
		img.AddFlag("not_pick")
		img.Show()
		self.keep.append(img)
		return img

	def __Text(self, parent, text, x, y, font = None):
		line = ui.TextLine()
		line.SetParent(parent)
		if font:
			line.SetFontName(font)
		line.SetPosition(x, y)
		line.SetHorizontalAlignCenter()
		line.SetPackedFontColor(COMPANION_LABEL_COLOR)
		line.SetText(text)
		line.Show()
		self.keep.append(line)
		return line

	def __CreateWindow(self):
		C = COMPANION_PATH.format("/%s")
		self.SetSize(self.WIDTH, self.HEIGHT)
		self.AddFlag("movable")
		self.AddFlag("float")
		titles = {"type": localeInfo.COMPANION_UPGRADE_TITLE, "evolve": localeInfo.PET_EVOLUTION_TITLE, "mount": localeInfo.MOUNT_EVOLVE_TITLE, "rune": localeInfo.MOUNT_RUNE_UPGRADE_TITLE}
		self.SetTitleName(titles.get(self.mode, localeInfo.COMPANION_UPGRADE_TITLE))
		self.SetCloseEvent(ui.__mem_func__(self.Close))

		header = self.__Image(self, C % "evolve/header_bg.png", 6, 28)
		self.__Text(header, localeInfo.COMPANION_REQUIREMENTS, 101, 9, "Tahoma:12b")

		bg = self.__Image(self, C % "evolve/background.png", 6, 56)
		self.slotIcons = []
		self.slotNone = []
		self.slotOk = []
		self.counts = []
		for i in xrange(self.SLOT_COUNT):
			slotBg = self.__Image(bg, C % "slot_skill.png", 7 + 37 * i, 7)
			icon = ui.ImageBox()
			icon.SetParent(slotBg)
			icon.SetPosition(4, 6)
			icon.SetStringEvent("MOUSE_OVER_IN", lambda s = i: self.__OnSlotOverIn(s))
			icon.SetStringEvent("MOUSE_OVER_OUT", ui.__mem_func__(self.__OnSlotOverOut))
			self.keep.append(icon)
			self.slotIcons.append(icon)
			self.slotNone.append(self.__Image(slotBg, C % "slot_locked.png", 4, 6))
			ok = self.__Image(slotBg, "d:/ymir work/ui/game/common/slots/bg_cases_check.png", 1, 6)
			ok.Hide()
			self.slotOk.append(ok)
			cnt = self.__Image(bg, C % "evolve/count_bg.png", 7 + 37 * i, 47)
			self.counts.append(self.__Text(cnt, "", 20, 4))


		chance = self.__Image(self, C % "evolve/bg_chance_success.png", 15, 127)
		self.chanceText = self.__Text(chance, localeInfo.COMPANION_EVOLUTION_CANNOT_FAIL if self.evolveMode else "", 92, 3)
		cost = self.__Image(self, C % "evolve/cost_title_bg.png", 15, 150)
		self.priceText = self.__Text(cost, "", 92, 3)

		btn = ui.Button()
		btn.SetParent(self)
		btn.SetUpVisual(C % "btn_norm.png")
		btn.SetOverVisual(C % "btn_hover.png")
		btn.SetDownVisual(C % "btn_select.png")
		btn.SetPosition((self.WIDTH - 133) / 2, 176)
		btn.SetText(localeInfo.COMPANION_CONFIRM)
		btn.SetTextColor(COMPANION_LABEL_COLOR)
		btn.SetEvent(ui.__mem_func__(self.__OnClickConfirm))
		btn.Show()
		self.confirmButton = btn

		pity = self.__Image(self, C % "evolve/cost_title_bg.png", 15, 209)
		self.pityText = self.__Text(pity, "", 92, 3)
		if self.evolveMode:
			pity.Hide()
			self.SetSize(self.WIDTH, self.HEIGHT - 26)

	def Open(self, petType, mountInfo = None):
		if self.mode == "mount":
			import uicompanionmount
			if petType >= uicompanionmount.MOUNT_MAX_EVOLUTION or not uicompanionmount.MOUNT_EVOLVE_REQUIREMENTS.has_key(petType):
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.COMPANION_EVOLVE_MAX)
				self.Close()
				return
			(level, reqItems, gold) = uicompanionmount.MOUNT_EVOLVE_REQUIREMENTS[petType]
			self.items = reqItems
			self.price = gold
		elif self.mode == "rune":
			import uicompanionmount
			data = uicompanionmount.RuneData()
			self.runeIndex = petType
			rank = mountInfo["rune"][petType] if mountInfo else 0
			if petType >= len(data) or rank >= uicompanionmount.MOUNT_RUNE_MAX_RANK:
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.MOUNT_RUNE_MAX)
				self.Close()
				return
			(mats, cost, prob, blessing, value) = data[petType][rank]
			self.items = mats[:self.SLOT_COUNT]
			self.price = cost
			self.chanceText.SetText(localeInfo.MOUNT_RUNE_CHANCE_FMT % prob)
			self.pity = mountInfo["bless"][petType] if mountInfo else 0
			self.pityMax = blessing
		elif self.evolveMode:
			# petType = current evolution 1..4
			if petType >= PET_EVOLUTION_MAX or not PET_EVOLVE_REQUIREMENTS.has_key(max(1, petType)):
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.COMPANION_EVOLVE_MAX)
				return
			(level, reqItems, gold) = PET_EVOLVE_REQUIREMENTS[max(1, petType)]
			self.items = reqItems
			self.price = gold
		else:
			if petType >= PET_TYPE_MAX or not PET_TYPE_REQUIREMENTS.has_key(max(1, petType)):
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.COMPANION_TYPE_UP_MAX)
				return
			reqs = PET_TYPE_REQUIREMENTS[max(1, petType)]
			self.items = tuple(r for r in reqs if r[0] != EVOLVE_YANG_VNUM)
			self.price = sum(r[1] for r in reqs if r[0] == EVOLVE_YANG_VNUM)
		for i in xrange(self.SLOT_COUNT):
			if i < len(self.items):
				item.SelectItem(self.items[i][0])
				self.slotIcons[i].LoadImage(item.GetIconImageFileName())
				self.slotIcons[i].Show()
				self.slotNone[i].Hide()
			else:
				self.slotIcons[i].Hide()
				self.slotNone[i].Show()
		self.RefreshItemCounts()
		self.SetPity(self.pity, self.pityMax)
		if not self.IsShow() and self.owner:
			x, y = self.owner.GetGlobalPosition()
			self.SetPosition(x + self.owner.GetWidth(), y + 149)
		self.Show()
		self.SetTop()
		if self.mode == "type":
			net.SendChatPacket("/pet_upgrade_type info")

	def Close(self):
		self.__CloseConfirmDialog()
		if self.toolTipItem:
			self.toolTipItem.HideToolTip()
		self.Hide()

	def OnPressEscapeKey(self):
		self.Close()
		return True

	def SetPity(self, pity, pityMax):
		self.pity = pity
		self.pityMax = pityMax
		if self.mode == "rune":
			self.pityText.SetText(localeInfo.MOUNT_RUNE_BLESSING_FMT % (pity, pityMax))
		else:
			self.pityText.SetText(localeInfo.COMPANION_PET_PITY % (pity, pityMax))

	def RefreshItemCounts(self):
		for i in xrange(self.SLOT_COUNT):
			if i < len(self.items):
				vnum, need = self.items[i]
				self.counts[i].SetText(str(need))
				if player.GetItemCountByVnum(vnum) >= need:
					self.slotOk[i].Show()
				else:
					self.slotOk[i].Hide()
			else:
				self.counts[i].SetText("")
				self.slotOk[i].Hide()
		self.priceText.SetText((localeInfo.COMPANION_EVOLVE_PRICE if self.mode in ("evolve", "mount") else localeInfo.COMPANION_UPGRADE_TYPE_PRICE) % self.__Dots(self.price))

	def __Dots(self, n):
		s = str(n)
		out = ""
		while len(s) > 3:
			out = "." + s[-3:] + out
			s = s[:-3]
		return s + out

	def OnUpdate(self):
		if app.GetTime() > self.updateTime:
			self.updateTime = app.GetTime() + 0.5
			self.RefreshItemCounts()

	def __OnSlotOverIn(self, index):
		if index < len(self.items) and self.toolTipItem:
			self.toolTipItem.SetItemToolTip(self.items[index][0], 310)
			self.toolTipItem.AppendCompanionShortcutTable()

	def __OnSlotOverOut(self):
		if self.toolTipItem:
			self.toolTipItem.HideToolTip()

	def __OnClickConfirm(self):
		import uiCommon
		self.__CloseConfirmDialog()
		dlg = uiCommon.QuestionDialog2()
		dlg.SetText1(localeInfo.MOUNT_EVOLVE_CONFIRMATION_1)
		dlg.SetText2(localeInfo.MOUNT_EVOLVE_CONFIRMATION_2)
		dlg.SetAcceptEvent(ui.__mem_func__(self.__SendConfirm))
		dlg.SetCancelEvent(ui.__mem_func__(self.__CloseConfirmDialog))
		dlg.Open()
		self.confirmDialog = dlg

	def __CloseConfirmDialog(self):
		if self.confirmDialog:
			self.confirmDialog.Close()
			self.confirmDialog = None

	def __SendConfirm(self):
		self.__CloseConfirmDialog()
		commands = {"type": "/pet_upgrade_type", "evolve": "/pet_evolve", "mount": "/mountx evolve", "rune": "/mountx rune_up %d" % self.runeIndex}
		net.SendChatPacket(commands.get(self.mode, "/pet_upgrade_type"))


class CompanionWindow(ui.Window):

	def __init__(self):
		self.petEvolveWnd = None
		self.mountPage = None
		self.defaultTextColor = None
		self.petExpInfo = None
		self.petSkillInfo = None
		self.petSkillOpenCount = 0
		self.petType = 1
		self.runeCheckTime = 0
		self.runeActive = None
		self.mountRefreshTime = 0
		self.petChildren = None
		self.petBonusValues = (0.0, 0.0, 0.0)
		ui.Window.__init__(self)
		self.interface = None
		self.tab = TAB_BUFFI
		self.children = {}
		self.toolTip = uiToolTip.ToolTip()
		self.toolTip.HideToolTip()

		self.buffiSummoned = False
		self.buffiName = "Buffi"
		self.buffiInfo = [1, 120, 0, 0, 0, 0, 0, 0, 0]
		self.buffiSkillPts = 0
		self.buffiSkillAmount = [0] * 6
		self.buffiSkillColor = [[0] * 5 for i in xrange(5)]
		self.skillColorWnd = None
		self.evolutionWnd = None
		self.petUpgradeTypeWnd = None
		self.buffiSkillPower = [0] * 5
		self.buffiSkillBook = [0] * 5
		self.buffiSkillCooldown = [0] * 5
		self.buffiInfoTime = app.GetTime()
		self.bonusPos = 0
		self.keep = []

		self.__LoadWindow()
		self.__SendBuffiOptions()

	def __SendBuffiOptions(self):
		try:
			import advanced_options_runtime
			pvp = bool(advanced_options_runtime.Get("auto_unequip_buffi_pvp", False))
			pvm = bool(advanced_options_runtime.Get("auto_equip_buffi_pvm", True))
			net.SendChatPacket("/buffi_option %d %d" % (pvp, pvm))
		except Exception:
			pass

	def __del__(self):
		ui.Window.__del__(self)

	def Destroy(self):
		self.Hide()
		if self.evolutionWnd:
			self.evolutionWnd.Destroy()
			self.evolutionWnd = None
		if self.petUpgradeTypeWnd:
			self.petUpgradeTypeWnd.Destroy()
			self.petUpgradeTypeWnd = None
		if self.petEvolveWnd:
			self.petEvolveWnd.Destroy()
			self.petEvolveWnd = None
		if self.mountPage:
			self.mountPage.Destroy()
			self.mountPage = None
		self.children = {}
		self.keep = []
		self.interface = None
		self.toolTip = None

	def BindInterface(self, interface):
		self.interface = interface

	# ------------------------------------------------------------------ helpers
	def __Image(self, parent, path, x, y, expanded = False):
		img = ui.ExpandedImageBox() if expanded else ui.ImageBox()
		img.SetParent(parent)
		img.LoadImage(path)
		img.SetPosition(x, y)
		img.AddFlag("not_pick")
		img.Show()
		self.keep.append(img)
		return img

	def __Text(self, parent, text, x, y, center = True):
		line = ui.TextLine()
		line.SetParent(parent)
		line.SetPosition(x, y)
		if center:
			line.SetHorizontalAlignCenter()
		if self.defaultTextColor:
			line.SetPackedFontColor(self.defaultTextColor)
		line.SetOutline()
		line.SetText(text)
		line.Show()
		self.keep.append(line)
		return line

	def __Button(self, parent, name, x, y, text, event):
		btn = ui.Button()
		btn.SetParent(parent)
		btn.SetPosition(x, y)
		btn.SetUpVisual(COMPANION_PATH.format("/btn_%s_norm.png" % name))
		btn.SetOverVisual(COMPANION_PATH.format("/btn_%s_hover.png" % name))
		btn.SetDownVisual(COMPANION_PATH.format("/btn_%s_select.png" % name))
		btn.SetText(text)
		if self.defaultTextColor:
			btn.SetTextColor(self.defaultTextColor)
		btn.Show()
		btn.SetEvent(event)
		return btn

	def __Subheader(self, parent, text, x, y):
		bg = self.__Image(parent, COMPANION_PATH.format("/subheader_bg.png"), x, y)
		self.__Text(bg, text, 66, 6)
		return bg

	# ------------------------------------------------------------------ layout
	def __LoadWindow(self):
		self.SetSize(PET_WIDTH + 30, PET_HEIGHT)
		self.AddFlag("movable")
		self.AddFlag("float")
		self.SetPosition(300, 120)

		tabs = []
		for i, name in enumerate(("pet", "horse", "buffi")):
			btn = ui.RadioButton()
			btn.SetParent(self)
			btn.SetPosition(0, 30 + 34 * i)
			btn.SetUpVisual(COMPANION_PATH.format("/btn_%s_norm.png" % name))
			btn.SetOverVisual(COMPANION_PATH.format("/btn_%s_hover.png" % name))
			btn.SetDownVisual(COMPANION_PATH.format("/btn_%s_select.png" % name))
			btn.SetEvent(ui.__mem_func__(self.__OnClickTab), i)
			btn.Show()
			tabs.append(btn)
		self.tabButtons = tabs

		board = ui.BoardWithTitleBar()
		board.SetParent(self)
		board.SetSize(PET_WIDTH, PET_HEIGHT)
		board.SetPosition(30, 0)
		board.AddFlag("attach")
		board.SetCloseEvent(ui.__mem_func__(self.Close))
		board.SetTitleName(localeInfo.PET_INFORMATION_TITLE)
		board.Show()
		self.board = board

		if app.ENABLE_WIKI_SYSTEM:
			wiki = ui.Button()
			wiki.SetParent(board.titleBar)
			wiki.SetUpVisual("d:/ymir work/ui/game/wiki/layout/button_wiki_small_norm.png")
			wiki.SetOverVisual("d:/ymir work/ui/game/wiki/layout/button_wiki_small_hover.png")
			wiki.SetDownVisual("d:/ymir work/ui/game/wiki/layout/button_wiki_small_down.png")
			(cx, cy) = board.titleBar.btnClose.GetLocalPosition()
			wiki.SetPosition(cx - 20, cy - 3)
			wiki.SetEvent(ui.__mem_func__(self.__OnClickWiki))
			wiki.Show()
			self.wikiButton = wiki

		self.__LoadBuffiWindow()
		self.__LoadPetWindow()
		self.mountPage = uicompanionmount.MountPage(self.board, self)
		self.__SelectTab(TAB_PET)

	def __OnClickWiki(self):
		if self.interface and app.ENABLE_WIKI_SYSTEM:
			self.interface.OpenWikiWindow()

	# ------------------------------------------------------------------ pet page
	# board-local. Data: growth pet (player.GetPetItem / GetPetExpPoints / GetPetLifeTime / GetPetSkillSlots).
	PET_BONUS_ITEMS = ((55038, 55041, 55044), (55039, 55042, 55045), (55040, 55043, 55046))	# uiCompanion.PET_BONUS_ITEM_VNUMS (K / O / B)
	PET_BONUS_GAUGES = ("red", "blue", "green")
	PET_BONUS_GAUGE_MAX = 15.0						# uiCompanion.PET_BONUS_GAUGE_MAX_PERCENT
	PET_SKILL_SLOT_COUNT = 6

	def __LoadPetWindow(self):
		c = {}
		P = COMPANION_PATH.format("/%s")
		win = ui.Window()
		win.SetParent(self.board)
		win.SetPosition(0, 0)
		win.SetSize(PET_WIDTH, PET_HEIGHT)
		win.AddFlag("not_pick")
		win.Hide()
		c["pet_window"] = win

		bg = self.__Image(win, P % "background.png", 7, 30)
		c["backgound"] = bg

		# portrait
		c["slot_bg"] = self.__Image(bg, P % "bg_slot.png", 4, 4)
		c["slot_img"] = self.__Image(c["slot_bg"], P % "slot_new.png", 13, 13)
		icon = ui.ImageBox()
		icon.SetParent(c["slot_img"])
		icon.SetPosition(2, 2)
		icon.SetStringEvent("MOUSE_OVER_IN", ui.__mem_func__(self.__OverInPetSeal))
		icon.SetStringEvent("MOUSE_OVER_OUT", ui.__mem_func__(self.__OverOutPetItem))
		icon.Show()
		c["pet_icon"] = icon

		# Isim / Tip / Seviye
		titles = (localeInfo.COMPANION_PET_NAME, localeInfo.COMPANION_PET_TYPE, localeInfo.COMPANION_PET_LEVEL)
		for i in xrange(3):
			c["bg_desc_%d" % i] = self.__Image(bg, P % "detail_title.png", 70, 4 + 22 * i)
			c["desc_%d" % i] = self.__Text(c["bg_desc_%d" % i], titles[i], 45, 4)
			c["desc_%d" % i].SetPackedFontColor(COMPANION_LABEL_COLOR)
			c["bg_value_%d" % i] = self.__Image(bg, P % "detail_value.png", 162, 3 + 22 * i)
			c["value_%d" % i] = self.__Text(c["bg_value_%d" % i], "", 49, 4)
			c["value_%d" % i].SetPackedFontColor(COMPANION_VALUE_COLOR)

		# EXP / Sure headers
		c["subheader_bg_1"] = self.__Image(bg, P % "subheader_bg.png", 2, 68)
		c["subheader_txt_1"] = self.__Text(c["subheader_bg_1"], localeInfo.COMPANION_EXP, 66, 5)
		c["subheader_txt_1"].SetPackedFontColor(COMPANION_LABEL_COLOR)
		c["subheader_bg_2"] = self.__Image(bg, P % "subheader_bg.png", 131, 68)
		c["subheader_txt_2"] = self.__Text(c["subheader_bg_2"], localeInfo.COMPANION_DURATION, 66, 5)
		c["subheader_txt_2"].SetPackedFontColor(COMPANION_LABEL_COLOR)

		# exp balls
		c["exp_bg"] = self.__Image(bg, P % "details_bg.png", 3, 92)
		expWin = ui.Window()
		expWin.SetParent(c["exp_bg"])
		expWin.SetPosition(11, 7)
		expWin.SetSize(126, 32)
		expWin.Show()
		c["exp_empty"] = expWin
		self.petExpArea = HoverArea(ui.__mem_func__(self.__OverInPetExp), ui.__mem_func__(self.__OverOut))
		self.petExpArea.SetParent(c["exp_bg"])
		self.petExpArea.SetPosition(0, 0)
		self.petExpArea.SetSize(130, 47)
		self.petExpArea.Show()
		for k in xrange(4):
			c["exp_empty_%d" % (k + 1)] = self.__Image(expWin, P % "progress_empty.png", 4 + 25 * k, 4)
			c["exp_full_%d" % (k + 1)] = self.__Image(expWin, P % "progress.png", 4 + 25 * k, 4)

		# duration gauge
		c["duration_bg"] = self.__Image(bg, P % "details_bg.png", 132, 92)
		c["duration_empty"] = self.__Image(c["duration_bg"], P % "gauge_empty.png", 6, 5)
		c["duration_full"] = self.__Image(c["duration_bg"], P % "gauge_full.png", 8, 7, True)
		c["duration_text"] = self.__Text(c["duration_bg"], "", 65, 28)
		c["duration_text"].SetPackedFontColor(COMPANION_LABEL_COLOR)

		# Evrim / Yukseltme Turu
		c["evolve_btn"] = self.__CompanionButton(bg, "btn_evolve", 2, 138, localeInfo.COMPANION_EVOLVE, ui.__mem_func__(self.__OnClickPetEvolve))
		c["up_type_btn"] = self.__CompanionButton(bg, "btn_refine", 132, 138, localeInfo.COMPANION_UPGRADE_TYPE, ui.__mem_func__(self.__OnClickPetUpgradeType))

		# 3 bonuses: item icon, name, gauge, value
		bonusNames = (localeInfo.PET_TOOLTIP_HP, localeInfo.PET_TOOLTIP_SP, localeInfo.PET_TOOLTIP_DEF)
		for i in xrange(3):
			row = self.__Image(bg, P % "pet_bonus_value.png", 4, 171 + 44 * i)
			c["bg_bonus_%d" % i] = row
			bonusIcon = ui.ImageBox()
			bonusIcon.SetParent(row)
			bonusIcon.SetPosition(7, 5)
			item.SelectItem(self.PET_BONUS_ITEMS[i][0])
			bonusIcon.LoadImage(item.GetIconImageFileName())
			bonusIcon.SetStringEvent("MOUSE_OVER_IN", lambda s = i: self.__OverInPetBonusItem(s))
			bonusIcon.SetStringEvent("MOUSE_OVER_OUT", ui.__mem_func__(self.__OverOutPetItem))
			bonusIcon.Show()
			c["bonus_item_slot_%d" % i] = bonusIcon
			c["bonus_desc_%d" % i] = self.__Text(row, bonusNames[i], 45, 7, False)
			c["bonus_desc_%d" % i].SetPackedFontColor(COMPANION_LABEL_COLOR)
			c["bonus_gauge_bg_%d" % i] = self.__Image(row, P % "pet_gauge_bg.png", 43, 24)
			c["bonus_gauge_full_%d" % i] = self.__Image(c["bonus_gauge_bg_%d" % i], P % ("pet_gauge_full_%s.png" % self.PET_BONUS_GAUGES[i]), 3, 3, True)
			c["bonus_value_%d" % i] = self.__Text(row, "", 225, 14)
			c["bonus_value_%d" % i].SetPackedFontColor(COMPANION_VALUE_COLOR)

		# skills
		c["header_bg_3"] = self.__Image(bg, P % "header_title.png", 2, 301)
		c["header_3"] = self.__Text(c["header_bg_3"], localeInfo.COMPANION_SKILLS, 130, 8)
		c["header_3"].SetPackedFontColor(COMPANION_LABEL_COLOR)
		c["skill_bg"] = self.__Image(bg, P % "skill_pet_bg.png", 3, 328)
		self.petSkillLocked = []
		self.petSkillSlots = []
		for k in xrange(self.PET_SKILL_SLOT_COUNT):
			lock = self.__Image(c["skill_bg"], P % "slot_locked.png", 11 + 41 * k, 6)
			self.petSkillLocked.append(lock)
			slot = ui.SlotWindow()
			slot.SetParent(c["skill_bg"])
			slot.SetPosition(11 + 41 * k, 6)
			slot.SetSize(32, 32)
			slot.AppendSlot(0, 0, 0, 32, 32)
			slot.SetOverInItemEvent(lambda slotIndex, s = k: self.__OverInPetSkill(s))
			slot.SetOverInEmptySlotEvent(lambda slotIndex, s = k: self.__OverInPetSkill(s))
			slot.SetOverOutItemEvent(ui.__mem_func__(self.__OverOut))
			slot.SetSelectEmptySlotEvent(lambda slotIndex, s = k: self.__OnSelectPetSkillSlot(s))
			slot.SetSelectItemSlotEvent(lambda slotIndex, s = k: self.__OnSelectPetSkillSlot(s))
			slot.Show()
			self.petSkillSlots.append(slot)

		# nothing summoned
		notPet = ui.ThinBoardCircle()
		notPet.SetParent(win)
		notPet.SetPosition(9, 30)
		notPet.SetSize(262, 375)
		notPet.Hide()
		c["not_pet"] = notPet
		c["not_pet_text"] = self.__Text(notPet, localeInfo.COMPANION_NO_PET, 131, 187)

		self.petChildren = c
		self.petRefreshTime = 0

	def __CompanionButton(self, parent, name, x, y, text, event):
		btn = ui.Button()
		btn.SetParent(parent)
		btn.SetPosition(x, y)
		btn.SetUpVisual(COMPANION_PATH.format("/%s_norm.png" % name))
		btn.SetOverVisual(COMPANION_PATH.format("/%s_hover.png" % name))
		btn.SetDownVisual(COMPANION_PATH.format("/%s_select.png" % name))
		btn.SetEvent(event)
		btn.Show()
		label = ui.TextLine()
		label.SetParent(btn)
		label.AddFlag("not_pick")
		label.SetPosition(41, 10)
		label.SetPackedFontColor(COMPANION_LABEL_COLOR)
		label.SetText(text)
		label.Show()
		self.keep.append(label)
		return btn

	def __GetPetID(self):
		try:
			return player.GetActivePetItemId()
		except:
			return 0

	def RefreshPetPage(self):
		if not self.petChildren:
			return
		c = self.petChildren
		petID = self.__GetPetID()
		if not petID:
			c["not_pet"].Show()
			c["backgound"].Hide()
			return
		c["not_pet"].Hide()
		c["backgound"].Show()

		(level, evol, birthday, name, hp, defence, sp) = player.GetPetItem(petID)
		vnum = player.GetActivePetItemVNum()
		if vnum:
			item.SelectItem(vnum)
			c["pet_icon"].LoadImage(item.GetIconImageFileName())
			c["pet_icon"].Show()
		c["value_0"].SetText(name)
		petType = player.GetPetType(petID) if app.ENABLE_GROWTH_PET_RENEWAL else 0
		self.petType = petType
		c["value_1"].SetText("%d / %d" % (petType, PET_TYPE_MAX))
		c["value_2"].SetText(str(level))

		(curEXP, nextEXP, itemEXP, itemMaxEXP) = player.GetPetExpPoints(petID)
		ratio = 0.0
		if nextEXP > 0:
			ratio = min(1.0, float(curEXP) / float(nextEXP))
		filled = min(4, int(ratio * 4))
		for k in xrange(4):
			if k < filled:
				c["exp_full_%d" % (k + 1)].Show()
			else:
				c["exp_full_%d" % (k + 1)].Hide()
		self.petExpInfo = (curEXP, nextEXP, itemEXP, itemMaxEXP)

		# duration
		(endTime, maxTime) = player.GetPetLifeTime(petID)
		remain = max(0, endTime - app.GetGlobalTimeStamp())
		if maxTime > 0:
			pct = min(1.0, float(remain) / float(maxTime))
		else:
			pct = 0.0
		c["duration_full"].SetRenderingRect(0.0, 0.0, pct - 1.0, 0.0)
		c["duration_text"].SetText("%s  / %s  (%d%%)" % (self.__PetDay(remain), self.__PetDay(maxTime), int(pct * 100)))

		# bonuses (hp, attack = sp slot, elemental = def slot)
		values = (hp, sp, defence)
		self.petBonusValues = values
		for i in xrange(3):
			c["bonus_value_%d" % i].SetText("%0.1f%%" % values[i])
			item.SelectItem(self.__GetPetBonusItemVnum(i, values[i]))
			c["bonus_item_slot_%d" % i].LoadImage(item.GetIconImageFileName())
			g = min(1.0, values[i] / self.PET_BONUS_GAUGE_MAX)
			c["bonus_gauge_full_%d" % i].SetRenderingRect(0.0, 0.0, g - 1.0, 0.0)

		# skills: open slots first, the rest locked
		self.petSkillInfo = [(0, 0, 0)] * self.PET_SKILL_SLOT_COUNT
		openCount = 0
		if app.ENABLE_GROWTH_PET_RENEWAL:
			(openCount, slots) = player.GetPetSkillSlots(petID)
			self.petSkillInfo = list(slots)
		else:
			t = player.GetPetSkill(petID)
			openCount = t[0]
			self.petSkillInfo = [(t[1], t[2], t[3]), (t[4], t[5], t[6]), (t[7], t[8], t[9]), (0, 0, 0), (0, 0, 0), (0, 0, 0)]
		self.petSkillOpenCount = openCount
		for k in xrange(self.PET_SKILL_SLOT_COUNT):
			slot = self.petSkillSlots[k]
			vnum = self.petSkillInfo[k][0] if k < len(self.petSkillInfo) else 0
			self.petSkillLocked[k].Show()
			if k >= openCount:
				slot.ClearSlot(0)
			else:
				if vnum:
					slot.SetPetSkillSlotNew(0, vnum)
				else:
					slot.ClearSlot(0)
			slot.RefreshSlot()

	def __PetDay(self, seconds):
		days = int(seconds) / 86400
		if days > 0:
			return "%d%s" % (days, localeInfo.COMPANION_DAY_SHORT)
		return "%d%s" % (max(0, int(seconds) / 3600), localeInfo.COMPANION_HOUR_SHORT)

	def __GetPetBonusItemVnum(self, index, value):
		# uiCompanion.GetPetBonusItemVnum (probed): below 5 % small, below 10 % medium, else large
		raw = int(round(value * 10))
		if raw < 50:
			return self.PET_BONUS_ITEMS[index][0]
		if raw < 100:
			return self.PET_BONUS_ITEMS[index][1]
		return self.PET_BONUS_ITEMS[index][2]

	def __GetItemToolTip(self):
		if self.interface and self.interface.tooltipItem:
			return self.interface.tooltipItem
		return None

	def __OverInPetBonusItem(self, index):
		tip = self.__GetItemToolTip()
		if not tip:
			return
		values = self.petBonusValues
		tip.SetItemToolTip(self.__GetPetBonusItemVnum(index, values[index]), 310)
		tip.AppendCompanionShortcutTable()

	def __OverInPetSeal(self):
		tip = self.__GetItemToolTip()
		if not tip:
			return
		cell = player.EQUIPMENT_SLOT_START + 38	# WEAR_GROWTH_PET
		if player.GetItemIndex(player.INVENTORY, cell):
			tip.SetInventoryItem(cell)

	def __OverOutPetItem(self):
		tip = self.__GetItemToolTip()
		if tip:
			tip.HideToolTip()

	def OnPetPotionResult(self, code, value):
		if code == 0:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.COMPANION_POTION_NO_PET)
		elif code == 1:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.PET_POTION_REQUIRED_TYPE % value)
		elif code == 2:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.COMPANION_POTION_MAX % (value / 10))
		elif code == 3:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.COMPANION_POTION_FAIL)
		elif code == 4:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.COMPANION_POTION_SUCCESS % (value / 10.0))
		self.petRefreshTime = 0

	def OnPetTypeUpgradeResult(self, code, pity, pityMax):
		messages = {
			1: localeInfo.COMPANION_POTION_NO_PET,
			2: localeInfo.COMPANION_TYPE_UP_MAX,
			3: localeInfo.COMPANION_TYPE_UP_ITEM,
			4: localeInfo.COMPANION_TYPE_UP_GOLD,
			5: localeInfo.COMPANION_TYPE_UP_FAIL,
			6: localeInfo.COMPANION_TYPE_UP_SUCCESS,
		}
		if messages.has_key(code):
			chat.AppendChat(chat.CHAT_TYPE_INFO, messages[code])
		wnd = self.petUpgradeTypeWnd
		if wnd:
			wnd.SetPity(pity, pityMax)
			if code == 6:
				newType = self.petType + 1
				if newType >= PET_TYPE_MAX:
					wnd.Close()
				else:
					wnd.Open(newType)
		self.petRefreshTime = 0

	def __OverInPetExp(self):
		info = self.petExpInfo
		if not info:
			return
		(curEXP, nextEXP, itemEXP, itemMaxEXP) = info
		self.__ShowExpToolTip(curEXP, nextEXP)

	def __OverInPetSkill(self, slot):
		info = self.petSkillInfo
		(vnum, level, cool) = info[slot] if info and slot < len(info) else (0, 0, 0)
		if slot >= self.petSkillOpenCount:
			if slot < 3:
				self.__ShowLines([localeInfo.PET_AUTO_LOCKED_SKILL_TOOLTIP], 256)
			else:
				self.__ShowLines([localeInfo.PET_LOCKED_SKILL_TOOLTIP], 316)
			return
		if not vnum:
			return
		(name, desc, useType, coolTime) = skill.GetPetSkillInfo(vnum)
		self.__ShowLines([localeInfo.PET_TOOLTUP_SKILL % (name, level), desc])

	def __OnSelectPetSkillSlot(self, slot):
		if not mouseModule.mouseController.isAttached():
			return
		if slot >= self.petSkillOpenCount:
			mouseModule.mouseController.DeattachObject()
			return
		attachedSlotPos = mouseModule.mouseController.GetAttachedSlotNumber()
		mouseModule.mouseController.DeattachObject()
		net.SendPetLearnSkill(slot, attachedSlotPos)

	def __GetOldPetWindow(self):
		if app.ENABLE_GROWTH_PET_SYSTEM and self.interface and self.interface.wndPetInfoWindow:
			return self.interface.wndPetInfoWindow
		return None

	def __OnClickPetEvolve(self):
		petID = self.__GetPetID()
		if not petID:
			return
		if not self.petEvolveWnd:
			self.petEvolveWnd = PetUpgradeTypeWindow(self, True)
		if self.petEvolveWnd.IsShow():
			self.petEvolveWnd.Close()
			return
		(level, evol, birthday, name, hp, defence, sp) = player.GetPetItem(petID)
		self.petEvolveWnd.Open(evol)

	def OnPetEvolveResult(self, code, value):
		messages = {
			0: localeInfo.COMPANION_POTION_NO_PET,
			1: localeInfo.COMPANION_EVOLVE_MAX,
			3: localeInfo.COMPANION_TYPE_UP_ITEM,
			4: localeInfo.COMPANION_TYPE_UP_GOLD,
			5: localeInfo.COMPANION_EVOLVE_SUCCESS,
		}
		if code == 2:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.COMPANION_EVOLVE_LEVEL % value)
		elif messages.has_key(code):
			chat.AppendChat(chat.CHAT_TYPE_INFO, messages[code])
		wnd = self.petEvolveWnd
		if wnd and code == 5:
			if value >= PET_EVOLUTION_MAX:
				wnd.Close()
			else:
				wnd.Open(value)
		self.petRefreshTime = 0

	def OnMountInfo(self, args):
		if self.mountPage:
			self.mountPage.SetInfo(args)

	def OnMountResult(self, code, value):
		if self.mountPage:
			self.mountPage.OnResult(code, value)

	def OnPetSkillSlotResult(self, code, value):
		if code == 0:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.COMPANION_POTION_NO_PET)
		elif code == 1:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.PET_LOCKED_SKILL_TOOLTIP)
		elif code == 2:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.PET_AUTO_LOCKED_SKILL_TOOLTIP)
		elif code == 3:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.COMPANION_SKILL_SLOT_MAX)
		elif code == 4:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.COMPANION_SKILL_SLOT_OPENED % value)
		self.petRefreshTime = 0

	def __OnClickPetUpgradeType(self):
		if not self.__GetPetID():
			return
		if not self.petUpgradeTypeWnd:
			self.petUpgradeTypeWnd = PetUpgradeTypeWindow(self)
		if self.petUpgradeTypeWnd.IsShow():
			self.petUpgradeTypeWnd.Close()
			return
		self.petUpgradeTypeWnd.Open(self.petType)

	def __LoadBuffiWindow(self):
		self.defaultTextColor = COMPANION_LABEL_COLOR
		c = {}
		win = ui.Window()
		win.SetParent(self.board)
		win.SetPosition(3, 2)
		win.SetSize(PET_WIDTH, PET_HEIGHT)
		win.AddFlag("not_pick")
		win.Show()
		c["buffi_window"] = win

		# Left column x=5 (130 wide), right column x=136. Content frame = background.png.
		c["backgound"] = self.__Image(win, COMPANION_PATH.format("/background.png"), 4, 28)

		# portrait + Name / Level / Intelligence
		c["slot_bg"] = self.__Image(win, COMPANION_PATH.format("/buffi_bg.png"), 8, 29)
		titles = ("Name", "Level", "Intelligence")
		for i in xrange(3):
			y = 31 + 22 * i
			c["bg_desc_%d" % i] = self.__Image(win, COMPANION_PATH.format("/detail_title.png"), 74, y)
			c["desc_%d" % i] = self.__Text(c["bg_desc_%d" % i], titles[i], 8, 3, False)
			c["bg_value_%d" % i] = self.__Image(win, COMPANION_PATH.format("/detail_value.png"), 166, y)
			c["value_%d" % i] = self.__Text(c["bg_value_%d" % i], "-", 49, 3)

		info = ui.Button()
		info.SetParent(c["bg_desc_2"])
		info.SetPosition(72, 2)
		info.SetUpVisual("d:/ymir work/ui/pattern/q_mark_01.tga")
		info.SetOverVisual("d:/ymir work/ui/pattern/q_mark_02.tga")
		info.SetDownVisual("d:/ymir work/ui/pattern/q_mark_01.tga")
		info.SetOverEvent(ui.__mem_func__(self.__OverInIntInfo))
		info.SetOverOutEvent(ui.__mem_func__(self.__OverOut))
		info.Show()
		c["int_info_btn"] = info

		# EXP header + orb box | Evolve / Duration buttons
		c["subheader_bg_1"] = self.__Subheader(win, "EXP", 4, 96)
		c["exp_bg"] = self.__Image(win, COMPANION_PATH.format("/detail_exp_bg.png"), 5, 120)
		balls = []
		for i in xrange(4):
			x = 20 + 25 * i
			self.__Image(win, COMPANION_PATH.format("/progress_empty.png"), x, 127)
			balls.append(self.__Image(win, COMPANION_PATH.format("/progress.png"), x, 127, True))
		c["exp_balls"] = balls

		expHover = HoverArea(ui.__mem_func__(self.__OverInExp), ui.__mem_func__(self.__OverOut))
		expHover.SetParent(win)
		expHover.SetPosition(5, 120)
		expHover.SetSize(c["exp_bg"].GetWidth(), c["exp_bg"].GetHeight())
		expHover.Show()
		self.keep.append(expHover)

		c["evolve_btn"] = self.__Button(win, "evolve", 135, 95, localeInfo.PET_BTN_EVOLVE, ui.__mem_func__(self.OnClickEvolutionBuffi))
		c["duration_btn"] = self.__Button(win, "duration", 135, 126, localeInfo.SUPPORT_DURATION_BUTTON, ui.__mem_func__(self.OnClickDurationBuffi))

		# Ore header + slots | Duration header + gauge
		c["subheader_bg_2"] = self.__Subheader(win, localeInfo.ORE_NAME, 4, 156)
		c["subheader_bg_3"] = self.__Subheader(win, localeInfo.PET_INFORMATION_DURATION, 135, 156)
		c["runes_bg"] = self.__Image(win, COMPANION_PATH.format("/details_bg.png"), 5, 180)
		c["duration_bg"] = self.__Image(win, COMPANION_PATH.format("/details_bg.png"), 136, 180)

		for i in xrange(3):
			self.__Image(win, "d:/ymir work/ui/game/common/slots/slot_runes.png", 9 + 41 * i, 185)
		runes = ui.SlotWindow()
		runes.SetParent(win)
		runes.SetPosition(9, 185)
		runes.SetSize(118, 36)
		for i in xrange(3):
			runes.AppendSlot(i, 41 * i + 2, 2, 32, 32)
		runes.SetOverInItemEvent(ui.__mem_func__(self.__OverInRune))
		runes.SetOverOutItemEvent(ui.__mem_func__(self.__OverOut))
		runes.SetSelectEmptySlotEvent(ui.__mem_func__(self.__OnSelectEmptyRune))
		runes.SetSelectItemSlotEvent(ui.__mem_func__(self.__OnRemoveRune))
		runes.SetUnselectItemSlotEvent(ui.__mem_func__(self.__OnRemoveRune))
		runes.Show()
		c["runes"] = runes

		c["duration_empty"] = self.__Image(win, COMPANION_PATH.format("/gauge_empty.png"), 141, 186)
		c["duration_full"] = self.__Image(c["duration_empty"], COMPANION_PATH.format("/gauge_full.png"), 2, 2, True)
		c["duration_text"] = self.__Text(win, "", 201, 207)

		# Skills header + row
		c["header_bg_3"] = self.__Image(win, COMPANION_PATH.format("/header_title.png"), 4, 227)
		c["header_3"] = self.__Text(c["header_bg_3"], "", 130, 7)
		c["skill_bg"] = self.__Image(win, COMPANION_PATH.format("/skill_background.png"), 5, 254)

		grid = ui.GridSlotWindow()
		grid.SetParent(win)
		grid.SetPosition(29, 262)
		grid.ArrangeSlot(0, 5, 1, 32, 32, 13, 0)
		grid.SetOverInItemEvent(ui.__mem_func__(self.__OverInItemSkill))
		grid.SetOverOutItemEvent(ui.__mem_func__(self.__OverOut))
		grid.Show()
		c["buffi_skill"] = grid

		plus = []
		colors = []
		for i in xrange(5):
			x = 29 + 45 * i
			btn = ui.Button()
			btn.SetParent(win)
			btn.SetPosition(x, 262)
			btn.SetUpVisual("d:/ymir work/ui/game/windows/btn_plus_up.sub")
			btn.SetOverVisual("d:/ymir work/ui/game/windows/btn_plus_over.sub")
			btn.SetDownVisual("d:/ymir work/ui/game/windows/btn_plus_down.sub")
			btn.SetEvent(ui.__mem_func__(self.__OnPressedSlotButton), i)
			btn.Hide()
			plus.append(btn)

			# skill colour: only offered once the skill reached Perfect Master
			col = ui.Button()
			col.SetParent(win)
			col.SetPosition(x + 27, 261)
			col.SetUpVisual("d:/ymir work/ui/game/skillcolor/skill_color_button_default.tga")
			col.SetOverVisual("d:/ymir work/ui/game/skillcolor/skill_color_button_over.tga")
			col.SetDownVisual("d:/ymir work/ui/game/skillcolor/skill_color_button_down.tga")
			col.SetEvent(ui.__mem_func__(self.__OnPressBuffiSkillColorButton), i)
			col.Hide()
			colors.append(col)
		c["skill_plus"] = plus
		c["skill_color"] = colors

		self.bonusDesc = (
			(0, localeInfo.SUPPORT_SKILL_AMOUNT_DESC_94, "%d%%"),
			(1, localeInfo.SUPPORT_SKILL_AMOUNT_DESC_95, "%d%%"),
			(2, localeInfo.SUPPORT_SKILL_AMOUNT_DESC_96, "%d%%"),
			(3, localeInfo.SUPPORT_SKILL_AMOUNT_DESC_110, "%d%%"),
			(4, localeInfo.SUPPORT_SKILL_AMOUNT_DESC_111, "+%d"),
			(5, localeInfo.SUPPORT_SKILL_AMOUNT_DESC_110_B, "%d%%"),
		)
		listWin = ui.Window()
		listWin.SetParent(win)
		listWin.SetPosition(8, 300)
		listWin.SetSize(250, BONUS_ROW_HEIGHT * BONUS_VISIBLE_ROWS)
		listWin.SetOnRunMouseWheelEvent(ui.__mem_func__(self.__OnWheelBonus))
		listWin.Show()
		c["bonus_list"] = listWin
		rows = []
		for i in xrange(BONUS_VISIBLE_ROWS):
			bg = self.__Image(listWin, COMPANION_PATH.format("/bonus_bg.png"), 0, BONUS_ROW_HEIGHT * i, True)
			bg.SetRenderingRect(0.0, 0.0, -0.027, 0.0)
			desc = self.__Text(bg, "", 7, 6, False)
			value = self.__Text(bg, "", 207, 6)
			rows.append((desc, value))
		c["bonus_rows"] = rows

		scroll = ThinScrollBar()
		scroll.SetParent(win)
		scroll.SetPosition(261, 300)
		scroll.SetScrollBarSize(BONUS_ROW_HEIGHT * BONUS_VISIBLE_ROWS)
		scroll.SetMiddleBarSize(float(BONUS_VISIBLE_ROWS) / len(self.bonusDesc))
		scroll.SetScrollEvent(ui.__mem_func__(self.__OnScrollBonus))
		scroll.SetOnRunMouseWheelEvent(ui.__mem_func__(self.__OnWheelBonus))
		scroll.Show()
		c["bonus_scroll"] = scroll

		# Costume visibility toggles (body / hair / weapon / sash)
		names = ((localeInfo.COMPANION_COSTUME_BODY, 0), (localeInfo.COMPANION_COSTUME_HAIR, 1), (localeInfo.COMPANION_COSTUME_WEAPON, 2), (localeInfo.COMPANION_COSTUME_SASH, 3))
		c["costume_visibility"] = []
		hidden = constInfo.BUFFI_COSTUME_HIDDEN_STATES
		for label, idx in names:
			x = 8 + 130 * (idx % 2)
			y = 361 + 22 * (idx / 2)
			btn = ui.ToggleButton()
			btn.SetParent(win)
			btn.SetPosition(x, y + 2)
			btn.SetUpVisual("d:/ymir work/ui/game/common/eye_normal_01.tga")
			btn.SetOverVisual("d:/ymir work/ui/game/common/eye_normal_02.tga")
			btn.SetDownVisual("d:/ymir work/ui/game/common/eye_closed_01.tga")
			btn.SetToggleDownEvent(lambda i = idx, f = ui.__mem_func__(self.SetBuffiCostumeVisibility): f(i, False))
			btn.SetToggleUpEvent(lambda i = idx, f = ui.__mem_func__(self.SetBuffiCostumeVisibility): f(i, True))
			if idx < len(hidden) and hidden[idx]:
				btn.Down()
			btn.Show()
			c["costume_visibility"].append(btn)
			self.__Text(win, label, x + 19, y, False)

		notb = ui.ThinBoardCircle()
		notb.SetParent(win)
		notb.SetPosition(8, 96)
		notb.SetSize(PET_WIDTH - 16, PET_HEIGHT - 104)
		notb.Hide()
		c["not_buffi"] = notb
		c["not_buffi_text"] = self.__Text(notb, localeInfo.BUFFI_NO_SPAWN, (PET_WIDTH - 16) / 2, (PET_HEIGHT - 104) / 2 - 6)

		self.children["buffi"] = c
		self.defaultTextColor = None
		for i in xrange(3):
			if c.has_key("value_%d" % i):
				c["value_%d" % i].SetPackedFontColor(COMPANION_VALUE_COLOR)	# Name / Level / Intelligence values
		self.__RefreshBonusList()
		self.UnsummonBuffi()

	# ------------------------------------------------------------------ tabs
	def __OnClickTab(self, tab):
		self.__SelectTab(tab)

	def __SelectTab(self, tab):
		self.tab = tab
		if self.petChildren:
			if tab == TAB_PET:
				self.petChildren["pet_window"].Show()
				self.children["buffi"]["buffi_window"].Hide()
				self.RefreshPetPage()
			elif tab == TAB_HORSE:
				self.petChildren["pet_window"].Hide()
				self.children["buffi"]["buffi_window"].Hide()
			else:
				self.petChildren["pet_window"].Hide()
				self.children["buffi"]["buffi_window"].Show()
		if self.mountPage:
			if tab == TAB_HORSE:
				self.mountPage.Show()
			else:
				self.mountPage.Hide()
		for i, btn in enumerate(self.tabButtons):
			if i == tab:
				btn.Down()
			else:
				btn.SetUp()

	def Open(self, tab = None):
		if tab is not None:
			self.__SelectTab(tab)
		self.Show()
		self.SetTop()
		net.SendChatPacket("/buffi_info")
		if self.tab == TAB_PET:
			self.RefreshPetPage()

	def Close(self):
		self.toolTip.HideToolTip()
		self.Hide()

	def Toggle(self):
		if self.IsShow():
			self.Close()
		else:
			self.Open()

	def OnPressEscapeKey(self):
		self.Close()
		return True

	def SetBuffiName(self, name):
		self.buffiName = name
		self.children["buffi"]["value_0"].SetText(name)

	def SetBuffiInformation(self, level, intel, exp, exp_total, evo, duration, runes_1, runes_2, runes_3):
		self.buffiInfo = [level, intel, exp, exp_total, evo, duration, runes_1, runes_2, runes_3]
		self.buffiInfoTime = app.GetTime()
		g_buffiState["level"] = level
		g_buffiState["duration"] = duration
		g_buffiState["time"] = self.buffiInfoTime
		if not self.buffiSummoned:
			self.buffiSummoned = True
			self.children["buffi"]["not_buffi"].Hide()
		self.UpdateBuffiInformation()
		self.__RefreshGameButton()

	def SetBuffiSkills(self, pts, *amountPower):
		self.buffiSkillPts = pts
		for i in xrange(5):
			self.buffiSkillAmount[i] = amountPower[i * 2]
			self.buffiSkillPower[i] = amountPower[i * 2 + 1]
		g_buffiState["skills"] = list(self.buffiSkillPower)
		g_buffiState["points"] = pts
		self.UpdateBuffiSkill()
		self.__RefreshGameButton()

	def SetBuffiSkillsBook(self, *books):
		self.buffiSkillBook = list(books[:5])

	def SetBuffiSkillsCooldown(self, *cooldowns):
		self.buffiSkillCooldown = list(cooldowns[:5])

	def GetBuffiSkillPts(self):
		return self.buffiSkillPts if self.buffiSummoned else 0

	def GetBuffiSkillsPower(self):
		return self.buffiSkillPower

	def GetBuffiSkillsBook(self):
		return self.buffiSkillBook

	def GetBuffiSkillsCooldown(self):
		return self.buffiSkillCooldown

	def __RefreshGameButton(self):
		if self.interface:
			self.interface.CheckGameButton()

	def UnsummonBuffi(self):
		self.buffiSummoned = False
		self.children["buffi"]["not_buffi"].Show()
		self.__RefreshGameButton()

	def UpdateBuffiInformation(self):
		c = self.children["buffi"]
		level, intel, exp, exp_total, evo, duration = self.buffiInfo[:6]

		c["value_0"].SetText(self.buffiName)
		c["value_1"].SetText("%d" % level)
		expired = 0
		for i in xrange(3):
			if self.buffiInfo[6 + i] > 0 and self.__GetRuneRemain(i) == 0:
				expired += 1
		c["value_2"].SetText("%d" % (intel - 3 * expired))

		ratio = float(exp) / float(exp_total) if exp_total > 0 else 1.0
		for i, ball in enumerate(c["exp_balls"]):
			part = min(1.0, max(0.0, ratio * 4 - i))
			ball.SetRenderingRect(0.0, part - 1.0, 0.0, 0.0)

		self.__UpdateDuration()

		runes = c["runes"]
		for i in xrange(3):
			v = self.__GetRuneRemain(i)
			if v == 0:
				runes.ClearSlot(i)
			else:
				runes.SetItemSlot(i, BUFFI_ORE_PERM_VNUM if v < 0 else BUFFI_ORE_VNUM, 0)
		runes.RefreshSlot()

	def __GetRuneRemain(self, idx):
		v = self.buffiInfo[6 + idx]
		if v <= 0:
			return v
		return max(0, v - int(app.GetTime() - self.buffiInfoTime))

	def __GetRemainDuration(self):
		duration = self.buffiInfo[5]
		if duration < 0:
			return -1
		return max(0, duration - int(app.GetTime() - self.buffiInfoTime))

	def __UpdateDuration(self):
		c = self.children["buffi"]
		remain = self.__GetRemainDuration()
		if remain < 0:
			c["duration_full"].SetPercentage(1, 1)
			c["duration_text"].SetText(localeInfo.BUFFI_DURATION_PERM)
			return
		c["duration_full"].SetPercentage(min(remain, BUFFI_DURATION_MAX), BUFFI_DURATION_MAX)
		c["duration_text"].SetText("%s / 30g (%d%%)" % (_FormatTime(remain), remain * 100 / BUFFI_DURATION_MAX))

	def UpdateBuffiSkill(self):
		c = self.children["buffi"]
		c["header_3"].SetText("%s [%d]" % (localeInfo.SUPPORT_TITLE_SKILL, self.buffiSkillPts))
		grid = c["buffi_skill"]
		for i in xrange(5):
			level = self.buffiSkillPower[i]
			grade, shown = _SkillGrade(level)
			grid.ClearSlot(i)
			grid.SetSkillSlotNew(i, BUFF_SKILL_INDEX[i], grade, max(1, shown))
			grid.SetSlotCountNew(i, grade, shown)
			bookMax = 40 if app.ENABLE_BUFFI_SKILL_BOOK else 30
			if (level < 20 and self.buffiSkillPts > 0) or 20 <= level < bookMax:
				c["skill_plus"][i].Show()
			else:
				c["skill_plus"][i].Hide()
			c["skill_color"][i].Show()
		grid.RefreshSlot()
		self.__RefreshBonusList()

	def __RefreshBonusList(self):
		c = self.children["buffi"]
		total = len(self.bonusDesc)
		for row, (desc, value) in enumerate(c["bonus_rows"]):
			idx = self.bonusPos + row
			if idx >= total:
				desc.SetText("")
				value.SetText("")
				continue
			skill, text, fmt = self.bonusDesc[idx]
			label = text.replace("%s", "").replace("+", "").rstrip(": ").strip()
			if len(label) > 30:
				label = label[:28] + ".."
			desc.SetText(label)
			value.SetText(fmt % self.buffiSkillAmount[skill])

	def __OnWheelBonus(self, down):
		maxPos = max(0, len(self.bonusDesc) - BONUS_VISIBLE_ROWS)
		if maxPos <= 0:
			return
		pos = min(maxPos, max(0, self.bonusPos + (1 if down else -1)))
		self.children["buffi"]["bonus_scroll"].SetPos(float(pos) / maxPos)

	def __OnScrollBonus(self):
		maxPos = max(0, len(self.bonusDesc) - BONUS_VISIBLE_ROWS)
		self.bonusPos = int(round(self.children["buffi"]["bonus_scroll"].GetPos() * maxPos))
		self.__RefreshBonusList()

	def OnUpdate(self):
		if not self.IsShow():
			return
		if self.tab == TAB_PET:
			now = app.GetTime()
			if now - self.petRefreshTime >= 0.5:
				self.petRefreshTime = now
				self.RefreshPetPage()
		elif self.tab == TAB_HORSE and self.mountPage:
			now = app.GetTime()
			if now - self.mountRefreshTime >= 1.0:
				self.mountRefreshTime = now
				self.mountPage.Refresh()	# food gauge
		self.__UpdateDuration()
		now = app.GetTime()
		if now - self.runeCheckTime >= 1.0:
			self.runeCheckTime = now
			active = tuple(self.__GetRuneRemain(i) != 0 for i in xrange(3))
			if self.runeActive is not None and active != self.runeActive:
				self.UpdateBuffiInformation()
			self.runeActive = active

	# ------------------------------------------------------------------ actions
	def __OnSelectEmptyRune(self, slot):
		if not mouseModule.mouseController.isAttached():
			return
		if mouseModule.mouseController.GetAttachedType() != player.SLOT_TYPE_INVENTORY:
			return
		vnum = mouseModule.mouseController.GetAttachedItemIndex()
		cell = mouseModule.mouseController.GetAttachedSlotNumber()
		mouseModule.mouseController.DeattachObject()
		if vnum in (BUFFI_ORE_VNUM, BUFFI_ORE_PERM_VNUM):
			self.SendAddOreBuffiPacket(cell)

	def __OnRemoveRune(self, slot):
		if self.__GetRuneRemain(slot) != 0:
			self.toolTip.HideToolTip()
			net.SendChatPacket("/support_remove_ore %d" % slot)

	def SendAddOreBuffiPacket(self, cell):
		net.SendChatPacket("/support_add_ore %d" % cell)

	def SendBuffiDurationPacket(self):
		net.SendChatPacket("/support_full_duration")

	def OnClickDurationBuffi(self):
		self.SendBuffiDurationPacket()

	def OnClickEvolutionBuffi(self):
		import chat
		if not app.ENABLE_BUFFI_EVOLUTION:
			return
		if not self.buffiSummoned:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.BUFFI_SUMMON_FIRST)
			return
		evo = self.buffiInfo[4]
		if evo >= BUFFI_MAX_EVOLUTION:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.BUFFI_MAX_EVOLUTION_REACHED)
			return
		if not self.evolutionWnd:
			self.evolutionWnd = BuffiEvolutionWindow(self)
		self.evolutionWnd.Open(evo)

	def OnBuffiEvolutionResult(self, success):
		if self.evolutionWnd:
			self.evolutionWnd.Close()

	def __OnPressBuffiSkillColorButton(self, slot):
		if self.skillColorWnd:
			self.skillColorWnd.Close()
			self.skillColorWnd = None
		wnd = BuffiSkillColorWindow(self, slot, BUFF_SKILL_INDEX[slot])
		wnd.Show()
		self.skillColorWnd = wnd

	def SetBuffiSkillColor(self, idx, colors):
		if 0 <= idx < 5:
			self.buffiSkillColor[idx] = list(colors[:5])

	def GetBuffiSkillColor(self, idx):
		return self.buffiSkillColor[idx]

	def SetBuffiCastSpeed(self, value):
		self.buffiSkillAmount[5] = value
		self.__RefreshBonusList()

	def __OnPressedSlotButton(self, slot):
		if app.ENABLE_SKILL_UPGRADE and self.buffiSkillPower[slot] >= 20 and self.interface:
			self.interface.OpenSkillUpgrade(2, BUFF_SKILL_INDEX[slot])
			return
		net.SendChatPacket("/support_skill_power %d" % slot)

	def SetBuffiCostumeVisibility(self, idx, visible):
		states = list(constInfo.BUFFI_COSTUME_HIDDEN_STATES)
		while len(states) < 4:
			states.append(0)
		states[idx] = 0 if visible else 1
		constInfo.BUFFI_COSTUME_HIDDEN_STATES = tuple(states)

	def RefreshBuffiCostumeVisibility(self):
		hidden = constInfo.BUFFI_COSTUME_HIDDEN_STATES
		for idx, btn in enumerate(self.children["buffi"]["costume_visibility"]):
			if idx < len(hidden) and hidden[idx]:
				btn.Down()
			else:
				btn.SetUp()

	# ------------------------------------------------------------------ tooltips
	def __ShowLines(self, lines, width = 0):
		self.toolTip.ClearToolTip()
		self.toolTip.toolTipWidth = width or self.toolTip.TOOL_TIP_WIDTH
		for text in lines:
			self.toolTip.AppendTextLine(text)
		self.toolTip.ShowToolTip()

	def __OverOut(self):
		self.toolTip.HideToolTip()

	def ShowBuffiSkillToolTip(self, slot):
		if 0 <= slot < len(BUFF_SKILL_INDEX):
			self.__OverInItemSkill(slot)

	def HideBuffiSkillToolTip(self):
		if self.toolTip:
			self.toolTip.HideToolTip()

	def __OverInRune(self, slot):
		v = self.__GetRuneRemain(slot)
		if v == 0:
			return
		self.__ShowLines(("%s +3 %s" % (localeInfo.ORE_NAME, localeInfo.BUFFI_INT_TABLE_INTELLIGENCE), localeInfo.BUFFI_DURATION_PERM if v < 0 else _FormatTime(v), localeInfo.BUFFI_ORE_REMOVE_HINT))

	def __OverInIntInfo(self):
		t = self.toolTip
		t.ClearToolTip()
		t.toolTipWidth = 240
		t.AppendTextLine(localeInfo.BUFFI_INT_TOOLTIP)
		t.AppendSpace(4)
		stages = (localeInfo.BUFFI_INT_STAGE_DEFAULT, localeInfo.BUFFI_INT_STAGE_1,
			localeInfo.BUFFI_INT_STAGE_2, localeInfo.BUFFI_INT_STAGE_3)
		rows = [(localeInfo.BUFFI_INT_TABLE_EVOLUTION, localeInfo.BUFFI_INT_TABLE_INTELLIGENCE)]
		for i in xrange(4):
			rows.append((stages[i], str(BUFFI_INT_STAGES[i])))

		left, width, rowH, split = 10, t.toolTipWidth - 20, 22, 150
		top = t.toolTipHeight
		for r, (col1, col2) in enumerate(rows):
			y = top + r * rowH
			bar = ui.Bar()
			bar.SetParent(t)
			bar.SetPosition(left, y)
			bar.SetSize(width, rowH)
			bar.SetColor(0xff2a2018 if r == 0 else (0x40000000 if r % 2 else 0x20000000))
			bar.AddFlag("not_pick")
			bar.Show()
			t.childrenList.append(bar)
			for x, text in ((left + split / 2, col1), (left + split + (width - split) / 2, col2)):
				line = ui.TextLine()
				line.SetParent(t)
				line.SetPosition(x, y + 4)
				line.SetHorizontalAlignCenter()
				line.SetOutline()
				line.SetPackedFontColor(t.TITLE_COLOR if r == 0 else t.FONT_COLOR)
				line.SetText(text)
				line.Show()
				t.childrenList.append(line)
		# grid lines
		for x, y, w, h in [(left, top + r * rowH, width, 1) for r in xrange(len(rows) + 1)] + \
				[(left, top, 1, rowH * len(rows)), (left + split, top, 1, rowH * len(rows)), (left + width, top, 1, rowH * len(rows))]:
			ln = ui.Bar()
			ln.SetParent(t)
			ln.SetPosition(x, y)
			ln.SetSize(w, h)
			ln.SetColor(0xff5a4a3a)
			ln.AddFlag("not_pick")
			ln.Show()
			t.childrenList.append(ln)
		t.toolTipHeight = top + rowH * len(rows) + 8
		t.ResizeToolTip()
		t.ShowToolTip()

	def __ShowExpToolTip(self, exp, total):
		t = self.toolTip
		t.ClearToolTip()
		t.toolTipWidth = 212
		t.AppendTextLine(localeInfo.COMPANION_EXP, COMPANION_LABEL_COLOR)
		t.AppendTextLine("%d / %d" % (exp, total), COMPANION_LABEL_COLOR)
		t.ShowToolTip()

	def __OverInExp(self):
		self.__ShowExpToolTip(self.buffiInfo[2], self.buffiInfo[3])

	def __OverInItemSkill(self, slot):
		name, nameG, nameP, desc, cond1, cond2, valueFmt = BUFFI_SKILL_TOOLTIP[slot]
		level = self.buffiSkillPower[slot]
		grade, shown = _SkillGrade(level)

		t = self.toolTip
		t.ClearToolTip()
		t.toolTipWidth = 200
		if grade:
			nextName = (nameG, nameG, nameP, "")[grade]
			if nextName:
				t.AppendTextLine(nextName, BUFFI_TT_WHITE)
			t.AppendTextLine((name, name, nameG, nameP)[grade] + BUFFI_GRADE_SUFFIX[grade], BUFFI_TT_GREEN)
		else:
			t.AppendTextLine(name, BUFFI_TT_WHITE)
		t.AppendSpace(5)
		for i in xrange(grpText.GetSplitingTextLineCount(desc, 30)):
			t.AppendTextLine(grpText.GetSplitingTextLine(desc, 30, i), BUFFI_TT_WHITE)
		t.AppendSpace(5)
		t.AppendTextLine(cond1, BUFFI_TT_YELLOW)
		t.AppendTextLine(cond2, BUFFI_TT_YELLOW)
		t.AppendTextLine(BUFFI_INT_POWERED, BUFFI_TT_YELLOW)
		t.AppendSpace(5)
		lines = BUFFI_SKILL_VALUE[slot]
		t.AppendTextLine(lines[0] % self.buffiSkillAmount[slot], BUFFI_TT_WHITE)
		if len(lines) > 1:
			t.AppendTextLine(lines[1] % self.buffiSkillAmount[5], BUFFI_TT_WHITE)
		t.ShowToolTip()
