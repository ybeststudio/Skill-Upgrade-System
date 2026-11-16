// Ara:
		bool ChangeSex(LPITEM item);

// Altina ekle:
#if defined(ENABLE_SKILL_UPGRADE) && defined(ENABLE_BUFFI_SKILL_BOOK)
		// Skill Upgrader (skill_upgrade.cpp)
		static DWORD GetSkillVnum(int idx);
		int GetSkillLevel(BYTE idx) const { return m_aiSkillLevel[idx]; }
		int GetBookProgress(BYTE idx) const { return m_aiBookProgress[idx]; }
		void SetBookProgress(BYTE idx, int iProgress);
		void OnBookLevelUp(BYTE idx);
		bool UseMasterBook(BYTE idx);
#endif

