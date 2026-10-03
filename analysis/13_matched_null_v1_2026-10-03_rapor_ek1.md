# K3 eşleşik sıfır dağılımı: ek 1 (2026-10-03)

Ana rapor (13_matched_null_v1_2026-10-03_rapor.md) ve results.csv değiştirilmedi. Bu ek yalnız süre bilgisini düzeltir; yeni hesap yok.

- Ana rapordaki "duvar saati toplamı 1.85 saat" ve results.csv'deki wall_hours_total yalnız SON oturumun süresidir. Çalışma üç oturumda
  tamamlandı, çünkü arka plan işi 2 saatlik üst sınırda iki kez kesildi ve checkpoint'ten sürdürüldü:
  oturum 1: 2026-10-03 17:49–19:49 (1003 iş), oturum 2: 19:5x–21:5x (981 iş), oturum 3: 21:5x–23:43 (1216 iş).
  Toplam duvar saati yaklaşık 5,8 saat (15 işçi); önceden tahmin 4,40 saatti; sınır 12 saat.
- Her (permütasyon i, tekrar r) kendi tohumuyla hesaplandığı için kesinti ve yeniden başlatma sonucu etkilemez; her iş checkpoint'e
  bir kez yazıldı (3200 satır = 1000 + 11 × 200).
- Test başına işlemci süresi (cpu_seconds) üç oturumun toplamıdır ve doğrudur.
