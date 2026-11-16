// Ara:
ACMD(do_support_skill_power);

// Altina ekle:
#ifdef ENABLE_SKILL_UPGRADE
ACMD(do_upgrade_skill);
ACMD(do_upgrade_skill_info);
#endif


// Ara:
	{ "buffi_set",						do_buffi_set,					0,						POS_DEAD,			GM_IMPLEMENTOR	},
	{ "support_skill_power",			do_support_skill_power,			0,						POS_DEAD,			GM_PLAYER		},

// Altina ekle:
#ifdef ENABLE_SKILL_UPGRADE
	{ "upgrade_skill",				do_upgrade_skill,				0,						POS_DEAD,			GM_PLAYER		},
	{ "upgrade_skill_info",			do_upgrade_skill_info,			0,						POS_DEAD,			GM_PLAYER		},
#endif

