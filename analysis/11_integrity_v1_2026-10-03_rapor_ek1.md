# K1 bütünlük denetimi: ek 1 (2026-10-03)

Ana rapor: 11_integrity_v1_2026-10-03_rapor.md (değiştirilmedi). Bu ek, uyuşmayan üç dosyanın yorumunu verir; yeni hesap yok
(yalnız yerel ve yeniden indirilen dosyaların SHA256'ları karşılaştırıldı).

- code/FR_Dats_band_THETA_EP_C_2_can_B12.xlsx: yerel kopya 0 bayt (indirme kusuru). Yayımlanan dosya 14.215 bayt; yeniden indirilen
  kopyanın SHA256'sı manifestle aynı. İçeriği 112 satır x 9 sütun; 7 istatistik x 112 = 784 değer CAR_FREC_DATS.mat'teki karşılığıyla
  birebir aynı (en büyük mutlak fark 0), Subject/Label sırası aynı. Yani dosya yayımlanan veri setinde boş DEĞİL; "0 bayt" bulgusu
  yalnız yerel kopyaya aittir. CLAUDE.md'deki "THETA_EP_C_2_can_B12.xlsx 0 bayt (yayımlanan zip'te de)" ifadesi bu açıdan düzeltilmelidir.
  04-B analizleri .mat dosyasını kullandığı için hiçbir sonuç etkilenmez.
- README.md (yerel 9.252 bayt, manifest 9.136) ve dataset_description.json (yerel 1.290, manifest 1.330): yerel kopyalar, NEMAR'dan
  (data.nemar.org/on006923/v1.0.0) yeniden indirilen kopyalarla SHA256 düzeyinde AYNI; ikisi de OpenNeuro manifestinden farklı.
  Yani fark bozulma değil: NEMAR aynası bu iki üstveri dosyasının farklı bir sürümünü sunuyor (dataset_description.json'da
  DatasetDOI 10.82901/nemar.on006923). Bunlar git ile tutulan metin dosyaları; EEG verisi ve öznitelikler etkilenmez.
- Manifestte olmayan 3 yerel dosya (.datalad/config, .gitattributes, .nemar/metadata.json) depo/ayna üstverisidir.
- sub-1084sg2'nin .fdt dosyası manifestte yok (yayımlanmamış); beklenen durum, yerelde de yok.
- EEG dosyalarının (.set) tamamı ve 2048 Excel dosyasının 2047'si manifestle birebir aynı (3031/3034 ok).
