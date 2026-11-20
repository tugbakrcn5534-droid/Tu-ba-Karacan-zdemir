# Link okuma sistemi

Claude'a attığın video linklerini (Instagram Reels, TikTok, YouTube...) Claude'un
okuyabileceği hale getirir. İşi GitHub Actions yapar, çünkü Claude'un çalıştığı
ortam Instagram'a bağlanamıyor.

Her link için `linkler/<tarih>_<site>_<id>/` klasörü oluşur:

| Dosya | İçerik |
|---|---|
| `README.md` | Açıklama metni, hesap adı, beğeni sayısı, konuşma dökümü |
| `kareler.jpg` | Videodan alınmış 4-12 karenin tek görselde özeti |
| `kare_XX.jpg` | Tek tek kareler |
| `bilgi.json` | Ham bilgiler |

## Kullanım

- **En kolayı:** Linki Claude'a at. Claude işlemi başlatır, sonucu okur ve sana anlatır.
- **Telefondan, Claude olmadan:** Bu repoda yeni bir Issue aç ve linki yapıştır.
  Bitince Issue'ya "Hazır" yorumu düşer.
- **Elle:** Actions sekmesi > **Link oku** > Run workflow > linki yapıştır.

## Instagram engellerse

Instagram bazen giriş yapmadan indirmeye izin vermez. O zaman:

1. Bilgisayarda Instagram'a giriş yap, "Get cookies.txt LOCALLY" gibi bir tarayıcı
   eklentisiyle `instagram.com` çerezlerini dışa aktar.
2. Repo > Settings > Secrets and variables > Actions > **New repository secret**
   - Ad: `IG_COOKIES`
   - Değer: cookies.txt dosyasının içeriği

İkinci bir (yan) Instagram hesabı kullanman daha güvenli olur.
