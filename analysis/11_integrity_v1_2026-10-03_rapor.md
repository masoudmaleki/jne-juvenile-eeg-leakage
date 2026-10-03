# K1 bütünlük denetimi (11 v1, 2026-10-03)

Tanım: CLAUDE.md, "2026-10-03 Gönderim öncesi kontroller". Karar kuralı yok; yalnız rapor. v1.0.0/ yalnız okundu.

- Manifest: 3034 dosya (toplam 8,731,246,606 bayt). Yerel v1.0.0/: 3037 dosya.
- ok: 3031; size_mismatch: 3; hash_mismatch: 0; missing: 0.
- Manifestte olmayan yerel dosya: 3 (.datalad/config; .gitattributes; .nemar/metadata.json).

## Uyuşmayan ya da eksik dosyalar

| Dosya | Durum | Beklenen boyut | Yerel boyut |
|---|---|---|---|
| README.md | size_mismatch | 9136 | 9252 |
| code/FR_Dats_band_THETA_EP_C_2_can_B12.xlsx | size_mismatch | 14215 | 0 |
| dataset_description.json | size_mismatch | 1330 | 1290 |

## Yeniden indirme (_redownload/, v1.0.0 dışında)

- README.md: indirildi, 9252 bayt, SHA256 manifestle FARKLI.
- code/FR_Dats_band_THETA_EP_C_2_can_B12.xlsx: indirildi, 14215 bayt, SHA256 manifestle AYNI. .mat karşılaştırması: 784 değer ((112, 9)), en büyük mutlak fark 0; Subject/Label sırası aynı.
- dataset_description.json: indirildi, 1290 bayt, SHA256 manifestle FARKLI.
