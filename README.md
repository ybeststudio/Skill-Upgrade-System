# Skill Upgrade System

Beceri Yükseltici. Beceri kitabı, ruh taşı ve yardımcı eşyaları tek pencereden toplu okuma; okuma animasyonu ve ilerleme çubuğu.

![Önizleme](preview.png)

![preview2](preview2.png)

![preview3](preview3.png)

---

## Ne var?

- Beceri Yükseltici penceresi (`uiskillupgrade.py`), `/upgrade_skill` komutu
- Kitap / ruh taşı okuma, yardımcı eşyalar (71001, 71094 vb.)
- Buffi becerileri için de çalışır *(Buffi sistemi varsa)*
- Sunucu tarafı `skill_upgrade.cpp`

## Paket yapısı

```
01. Svn/          → Client & Game source (Ara / Altına ekle / Bul / Değiştir patch dosyaları + yeni dosyalar)
02. Client/       → root, uiscript, locale, d_/ymir work assetleri
Added/            → Değişikliklerin uygulanmış hali (tam dosyalar, karşılaştırma için)
```

## Flagler

**Client** (`Locale_inc.h`):
- `ENABLE_SKILL_UPGRADE`

**Game** (`service.h`):
- `ENABLE_SKILL_UPGRADE`

Client ve game tarafında aynı isimli flagler birlikte açık olmalı; tek taraf açıkken paket / komut uyumsuzluğu olur.

## Kurulum (kısaca)

1. `01. Svn` altındaki patch dosyalarını kendi source ağacına uygula. Her blokta `// Ara:` satırlarını bul, `// Altına ekle:` kısmını altına ekle; `// Bul:` / `// Degistir:` bloklarında bulduğun satırları verilen blokla değiştir.
2. Yeni dosyaları (`skill_upgrade.cpp`) ilgili klasöre kopyala; game için `Makefile`, client için `vcxproj.txt` notuna göre projeye ekle.
3. `02. Client/root` ve `02. Client/uiscript` içindeki tam dosyaları pack'e kopyala, patch dosyalarını (`# Ara:` / `# Altına ekle:`) kendi dosyalarına uygula.
4. `02. Client/locale/<dil>/` satırlarını kendi locale dosyalarının sonuna ekle.
5. Client + game + db rebuild, pack güncelle.

## Bağımlılıklar

- `uicompanion.py` patch'i yalnızca **Companion System (Pet - Buffi - Mount)** paketi kuruluysa gerekli.

## Notlar

- Locale dosyalarında yalnızca bu sisteme ait anahtarlar var; `new_locale_*` kendi eklediğimiz, `locale_game` / `locale_interface` resmi istemcide olmayan anahtarlar. Türkçe dosyalar cp1254.
- Patch'lerde başka sistemlere ait satırlar görürsen (farklı `#ifdef`), o sistem sende yoksa yok say.
- Fork farklıysa paket header / struct sıralamasını kontrol et.

---

## İletişim

Sorular için Discord'dan yazabilirsin.

| | |
|---|---|
| GitHub | [github.com/ybeststudio](https://github.com/ybeststudio) |
| Discord | [discord.gg/NXmc6JrwYr](https://discord.gg/NXmc6JrwYr) |
| Discord ID | `beststudio` |
| Web | [bestpro.dev](https://bestpro.dev) |
| TurkMMO | [Best Studio](https://forum.turkmmo.com/uye/2104546-best-studio/) |
| YouTube | [@ybeststudio](https://www.youtube.com/@ybeststudiotr) |
| Instagram | [@ybeststudio](https://www.instagram.com/ybeststudio) |
| Facebook | [ybeststudio](https://www.facebook.com/ybeststudio/) |
| Twitter | [@ybeststudio](https://twitter.com/ybeststudio) |
| TikTok | [@ybeststudio](https://tiktok.com/@ybeststudio) |

---

**Best Studio** — Metin2 private server çözümleri
