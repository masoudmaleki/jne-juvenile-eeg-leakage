# K2 eşleştirilmiş permütasyon p değerleri (12 v1, 2026-10-03)

Tanım: CLAUDE.md, "2026-10-03 Gönderim öncesi kontroller". Yeni model eğitimi yok; yalnız kayıtlı değerler okundu.

## Kararı değişen testler

Yok: eşleşik p 16 testin HİÇBİRİNDE hesaplanamadı, dolayısıyla karar karşılaştırması da yapılamadı.

## Bulgu

16 testin 16'sinde sıfır dağılımının CV tohumları gözlenen analizin tohumlarıyla AYNI DEĞİL (ortak tohum sayısı: en çok 0). Sıfır dağılımında yalnız etiketler değil, katlama tohumları da farklı:

- Gözlenen: SEED + r (r = 0..19; 04-B N1'de 0..9).
- Sıfır, 07 ailesi ve 04-B P: SEED + 700000 + 50·i + r (i = permütasyon, r = 0..4).
- Sıfır, 04-B N1: SEED + 500000 + i (permütasyon başına 1 tekrar).
- Sıfır, 03(a) / 03(b): SEED + 100000 + 50·i + r / SEED + 200000 + 50·i + r (r = 0..4).
- 03(a) için ayrıca tekrar başına gözlenen AUC kayıtlı değil (yalnız ortalama ve yüzdelikler).

K2 tanımındaki kural gereği ("tohumlar farklıysa hesaplama") eşleşik gözlenen değer ve eşleşik p hesaplanmadı.
Kayıtlı değerlerle "aynı tohumlar" koşulu sağlanamaz; bunu sağlamak gözlenen modelin sıfır tohumlarıyla (ya da sıfırın gözlenen tohumlarıyla) yeniden eğitilmesini gerektirir, bu da K2 tanımının dışındadır (yeni model eğitimi yok).

Okuma doğrulaması: her testte kayıtlı tekrar değerlerinden ve kayıtlı sıfır dağılımından özgün gözlenen değer ve özgün p yeniden üretildi; hepsi results.csv ile aynı (gözlenen |fark| < 1e-9, p |fark| < 1e-12).

## Testler

| Test | N perm. | Tekrar (gözlenen / sıfır) | Tohumlar aynı mı | Gözlenen (özgün) | p (özgün) | Alfa | Gözlenen (eşleşik) | p (eşleşik) | Karar aynı mı |
|---|---|---|---|---|---|---|---|---|---|
| 03(a) sg vs sg2 | 1000 | 20 / 5 | hayır | 0.629 | 0.0529 | 0.025 | – | – | n/a |
| 03(b) transfer | 1000 | 20 / 5 | hayır | 0.436 | 0.7712 | 0.025 | – | – | n/a |
| 04-B N1 RF | 200 | 10 / 1 | hayır | 0.870 | 0.0050 | 0.05 | – | – | n/a |
| 04-B N1 SVM | 200 | 10 / 1 | hayır | 0.855 | 0.0050 | 0.05 | – | – | n/a |
| 04-B P SVM | 200 | 20 / 5 | hayır | 0.658 | 0.0100 | 0.05 | – | – | n/a |
| 07 A | 200 | 20 / 5 | hayır | 0.754 | 0.0050 | 0.05 | – | – | n/a |
| 07 B | 200 | 20 / 5 | hayır | 0.734 | 0.0050 | 0.05 | – | – | n/a |
| 07a closed | 200 | 20 / 5 | hayır | 0.645 | 0.0149 | 0.05 | – | – | n/a |
| 07a open | 200 | 20 / 5 | hayır | 0.709 | 0.0050 | 0.05 | – | – | n/a |
| 07b | 200 | 20 / 5 | hayır | 0.582 | 0.0498 | 0.05 | – | – | n/a |
| 07c | 200 | 20 / 5 | hayır | 0.569 | 0.2637 | 0.05 | – | – | n/a |
| 07d A all | 200 | 20 / 5 | hayır | 0.549 | 0.2239 | 0.05 | – | – | n/a |
| 07d B all | 200 | 20 / 5 | hayır | 0.589 | 0.1940 | 0.05 | – | – | n/a |
| 07d B open | 200 | 20 / 5 | hayır | 0.553 | 0.2886 | 0.05 | – | – | n/a |
| 07e | 200 | 20 / 5 | hayır | 0.746 | 0.0050 | 0.05 | – | – | n/a |
| 07f | 200 | 20 / 5 | hayır | 0.582 | 0.1045 | 0.05 | – | – | n/a |
