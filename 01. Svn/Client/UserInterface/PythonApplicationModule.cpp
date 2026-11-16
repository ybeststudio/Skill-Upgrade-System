// void initapp() icinde:
// Ara:
	PyModule_AddIntConstant(poModule, "ENABLE_BRAVE_CAPE_RENEWAL", 0);

// Altina ekle:
#ifdef ENABLE_SKILL_UPGRADE
	PyModule_AddIntConstant(poModule, "ENABLE_SKILL_UPGRADE", 1);
#else
	PyModule_AddIntConstant(poModule, "ENABLE_SKILL_UPGRADE", 0);
#endif

