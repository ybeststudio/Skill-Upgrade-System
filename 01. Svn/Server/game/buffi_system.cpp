// bool CBuffiActor::ReadSkillBook(BYTE idx) icinde:
// Bul:
	int& lv = m_aiSkillLevel[idx];
	if (lv >= 40)
		return false;

	if (lv < 30)
	{
		if (m_pkOwner->CountSpecifyItem(BUFFI_SKILL_BOOK_VNUM) > 0)
		{
			m_pkOwner->RemoveSpecifyItem(BUFFI_SKILL_BOOK_VNUM, 1);
			const int iNeed = lv - 19;	// M1 -> 1 book ... M10 -> 10 books
			if (++m_aiBookProgress[idx] >= iNeed)
			{
				m_aiBookProgress[idx] = 0;
				++lv;
				m_pkOwner->ChatPacket(CHAT_TYPE_INFO, LC_TEXT("Your Buffi's skill has improved."));
			}
			else
				m_pkOwner->ChatPacket(CHAT_TYPE_INFO, LC_TEXT("You read a Buffi skill book (%d/%d)."), m_aiBookProgress[idx], iNeed);
		}
		else if (m_pkOwner->CountSpecifyItem(BUFFI_MASTER_BOOK_VNUM) > 0)
		{
			m_pkOwner->RemoveSpecifyItem(BUFFI_MASTER_BOOK_VNUM, 1);
			m_aiBookProgress[idx] = 0;
			lv = 30;
			m_pkOwner->ChatPacket(CHAT_TYPE_INFO, LC_TEXT("Your Buffi's skill has improved."));
		}
		else
		{
			m_pkOwner->ChatPacket(CHAT_TYPE_INFO, LC_TEXT("You need a Buffi skill book to train this skill further."));
			return false;
		}
	}
	else
	{
		if (m_pkOwner->CountSpecifyItem(BUFFI_SOUL_STONE_VNUM) > 0)
		{
			m_pkOwner->RemoveSpecifyItem(BUFFI_SOUL_STONE_VNUM, 1);
			++lv;
		}
		else if (m_pkOwner->CountSpecifyItem(BUFFI_MASTER_STONE_VNUM) > 0)
		{
			m_pkOwner->RemoveSpecifyItem(BUFFI_MASTER_STONE_VNUM, 1);
			lv = 40;
		}
		else
		{
			m_pkOwner->ChatPacket(CHAT_TYPE_INFO, LC_TEXT("You need a Soul Stone to train this skill further."));
			return false;
		}
		m_pkOwner->ChatPacket(CHAT_TYPE_INFO, LC_TEXT("Your Buffi's skill has improved."));
	}

	if (m_pkChar)
		m_pkChar->EffectPacket(SE_SUCCESS);
	RequestRecast();
	Save();
	SendSkills();
	return true;

// Degistir:
#ifdef ENABLE_SKILL_UPGRADE
	m_pkOwner->ChatPacket(CHAT_TYPE_INFO, LC_TEXT("Use the Skill Upgrader to train this skill further."));
	return false;
#else
	int& lv = m_aiSkillLevel[idx];
	if (lv >= 40)
		return false;

	if (lv < 30)
	{
		if (m_pkOwner->CountSpecifyItem(BUFFI_SKILL_BOOK_VNUM) > 0)
		{
			m_pkOwner->RemoveSpecifyItem(BUFFI_SKILL_BOOK_VNUM, 1);
			const int iNeed = lv - 19;	// M1 -> 1 book ... M10 -> 10 books
			if (++m_aiBookProgress[idx] >= iNeed)
			{
				m_aiBookProgress[idx] = 0;
				++lv;
				m_pkOwner->ChatPacket(CHAT_TYPE_INFO, LC_TEXT("Your Buffi's skill has improved."));
			}
			else
				m_pkOwner->ChatPacket(CHAT_TYPE_INFO, LC_TEXT("You read a Buffi skill book (%d/%d)."), m_aiBookProgress[idx], iNeed);
		}
		else if (m_pkOwner->CountSpecifyItem(BUFFI_MASTER_BOOK_VNUM) > 0)
		{
			m_pkOwner->RemoveSpecifyItem(BUFFI_MASTER_BOOK_VNUM, 1);
			m_aiBookProgress[idx] = 0;
			lv = 30;
			m_pkOwner->ChatPacket(CHAT_TYPE_INFO, LC_TEXT("Your Buffi's skill has improved."));
		}
		else
		{
			m_pkOwner->ChatPacket(CHAT_TYPE_INFO, LC_TEXT("You need a Buffi skill book to train this skill further."));
			return false;
		}
	}
	else
	{
		if (m_pkOwner->CountSpecifyItem(BUFFI_SOUL_STONE_VNUM) > 0)
		{
			m_pkOwner->RemoveSpecifyItem(BUFFI_SOUL_STONE_VNUM, 1);
			++lv;
		}
		else if (m_pkOwner->CountSpecifyItem(BUFFI_MASTER_STONE_VNUM) > 0)
		{
			m_pkOwner->RemoveSpecifyItem(BUFFI_MASTER_STONE_VNUM, 1);
			lv = 40;
		}
		else
		{
			m_pkOwner->ChatPacket(CHAT_TYPE_INFO, LC_TEXT("You need a Soul Stone to train this skill further."));
			return false;
		}
		m_pkOwner->ChatPacket(CHAT_TYPE_INFO, LC_TEXT("Your Buffi's skill has improved."));
	}

	if (m_pkChar)
		m_pkChar->EffectPacket(SE_SUCCESS);
	RequestRecast();
	Save();
	SendSkills();
	return true;
#endif


// Ara:
}

// Altina ekle:
#if defined(ENABLE_SKILL_UPGRADE) && defined(ENABLE_BUFFI_SKILL_BOOK)
DWORD CBuffiActor::GetSkillVnum(int idx)
{
	return idx >= 0 && idx < BUFFI_SKILL_COUNT ? s_adwBuffiSkill[idx] : 0;
}

void CBuffiActor::SetBookProgress(BYTE idx, int iProgress)
{
	if (idx >= BUFFI_SKILL_COUNT)
		return;
	m_aiBookProgress[idx] = iProgress;
	Save();
}

void CBuffiActor::OnBookLevelUp(BYTE idx)
{
	if (idx >= BUFFI_SKILL_COUNT || m_aiSkillLevel[idx] >= 40)
		return;
	m_aiBookProgress[idx] = 0;
	++m_aiSkillLevel[idx];
	if (m_pkChar)
		m_pkChar->EffectPacket(SE_SUCCESS);
	RequestRecast();
	Save();
	SendSkills();
}

// Buffi Mastery Book (M -> G1) / Mastery Stone (G -> P)
bool CBuffiActor::UseMasterBook(BYTE idx)
{
	if (idx >= BUFFI_SKILL_COUNT)
		return false;
	int& lv = m_aiSkillLevel[idx];
	if (lv < 20 || lv >= 40)
		return false;
	const DWORD dwVnum = lv < 30 ? BUFFI_MASTER_BOOK_VNUM : BUFFI_MASTER_STONE_VNUM;
	if (m_pkOwner->CountSpecifyItem(dwVnum) <= 0)
	{
		m_pkOwner->ChatPacket(CHAT_TYPE_INFO, LC_TEXT("You don't have the required skill book."));
		return false;
	}
	m_pkOwner->RemoveSpecifyItem(dwVnum, 1);
	m_aiBookProgress[idx] = 0;
	lv = lv < 30 ? 30 : 40;
	m_pkOwner->ChatPacket(CHAT_TYPE_INFO, LC_TEXT("Your Buffi's skill has improved."));
	if (m_pkChar)
		m_pkChar->EffectPacket(SE_SUCCESS);
	RequestRecast();
	Save();
	SendSkills();
	return true;
}
#endif

