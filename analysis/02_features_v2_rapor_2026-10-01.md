# 02 Öznitelik çıkarma v2: 135 denek (2026-10-01)

Yalnızca betimsel. Sınıflandırma ve grup farkı testi yapılmadı.

## Ne yapıldı
- **CLAUDE.md:** "Önceden belirlenmiş birincil analiz" bölümü eklendi. Kesit, PSD, göreli güç, FOOOF (birincil: fixed 3–30 Hz; duyarlılık: knee 2–30 Hz), IAF, EMG ve kanal dışlama kuralı ile uyanıklık ölçütleri orada kilitlendi.
- **Betik:** `02_features_v2_2026-10-01.py`. Önce 4 denekle test edildi (test çıktıları scratchpad'de kaldı), sonra 140 dizinin tamamında çalıştırıldı.
- **Denekler:** 135 denek işlendi (cg 66, sg 45, sg2 24). Atlanan 5 denek beklenen listeyle aynı: 1009sg, 1013sg, 1020sg, 1021sg (uzun blok yok) ve 1084sg2 (.fdt dosyası yok).
- **Fit:** FOOOF hiçbir kanalda başarısız olmadı. Posterior ROI'de birincil fit R² medyanı 0,990, en düşüğü 0,949.

## Çıktılar (`analysis/`)
| Dosya | İçerik |
|---|---|
| `02_features_v2_2026-10-01_channels.csv` | denek × segment (full/H1/H2) × model (primary/knee) × 128 kanal |
| `02_features_v2_2026-10-01_roi.csv` | denek × segment × model × ROI (posterior/central/frontal/global; yalnız kalan kanallar) |
| `02_features_v2_2026-10-01_ta_timeseries.csv` | denek × ROI × 15 adet 30 s pencere, teta/alfa oranı |
| `02_features_v2_2026-10-01_subject_qc.csv` | denek başına QC özeti |
| `02_features_v2_2026-10-01_psd_full.npz` | tam kesit kanal PSD'leri (135 × 128 × 257) |
| `02_features_v2_2026-10-01_skipped.csv` | atlanan 5 denek ve nedeni |
| `02_descriptive_by_group_v2_2026-10-01.md / .csv` | grup bazında betimsel tablo (ortalama, SD, medyan, IQR, min–maks) |

## Betimsel tablo: medyan [Q1–Q3] (min–maks)
| Metrik | sg (n=45) | sg2 (n=24) | cg (n=66) |
|---|---|---|---|
| EMG indeksi (30–40 Hz log-log eğim, kanal medyanı) | −1,88 [−2,37; −1,38] (−5,27…0,22) | −2,56 [−3,04; −1,71] (−5,19…−0,66) | −2,04 [−2,52; −1,41] (−6,02…−0,25) |
| Dışlanan kanal (toplam) | 3 [1–7] (0–16) | 3,5 [1–8] (0–88) | 3 [1–6] (0–21) |
|   ...R² < 0,9 nedeniyle | 0 [0–3] | 0 [0–4,25] | 0 [0–1] |
|   ...EMG z > 3 nedeniyle | 2 [0–3] | 1 [0–4] | 1 [0–4] |
| FOOOF R², kanal medyanı | 0,989 [0,987–0,990] | 0,985 [0,983–0,990] | 0,990 [0,986–0,992] |
| FOOOF R², posterior ROI | 0,991 [0,988–0,994] | 0,983 [0,976–0,992] | 0,990 [0,984–0,994] |
| Teta/alfa eğimi, global (log10 oran/dk) | 0,014 [−0,006; 0,037] | 0,020 [0,008; 0,029] | 0,026 [0,005; 0,059] |
| Teta/alfa eğimi, posterior | 0,009 [−0,007; 0,024] | 0,017 [0,010; 0,032] | 0,029 [0,007; 0,070] |

EMG indeksinde değer ne kadar yüksekse (sıfıra ya da pozitife yakın), kas aktivitesi o kadar fazla.
Teta/alfa eğiminin pozitif olması, 8 dakika boyunca teta/alfa oranının arttığını gösterir; bu uyanıklığın düştüğüne işaret eder.

## Dikkat: kanal dışlama kuralı iki denekte yanlış hedefi vuruyor
- **sub-1105sg2: 128 kanalın 88'i dışlandı.** **sub-1114sg2: 57'si dışlandı.** İkisinde de dışlamanın nedeni R² < 0,9; EMG indeksleri ise düşük (kas yok).
- Spektrumları incelendi:
  - **1105sg2:** alfa tepesi yok. Tüm kanallarda 20–28 Hz'te dar bir beta tepesi var.
  - **1114sg2:** 15–25 Hz'te geniş bir beta tümseği var, üs çok düşük (~0,5).
- Yani sorun tek tek kanallarda değil, deneğin bütün spektrumunda. Kural bu iki denekte "bozuk kanal" yerine "atipik denek" yakalıyor.
- Sonuç olarak kalan kanallar keyfi bir alt küme oluyor. 1105sg2'nin global ROI'si 40 kanaldan, posterior ROI'si 9 yerine 6 kanaldan hesaplandı.
- Benzer ama daha hafif durumdakiler: 1096sg2 (19 kanal dışlandı), 1083sg2 (18).
- **Bu dört deneğin dördü de sg2 grubunda ve hem esrar hem kokain kullanıcısı** (participants.tsv). Beta fazlası madde ya da ilaç etkisiyle (ör. benzodiazepin) uyumlu, ama bu veriyle ayırt edilemez.
- Bunlar dışlanırsa ya da kanal kuralıyla budanırsa, "madde etkisi" sinyali tam da analizden çıkarılmış olur.
- Kuralı değiştirmedim, çünkü önceden belirlenmişti.
- **Karar gerekiyor:** denek düzeyinde bir QC kuralı eklenecek mi? Örnek kural: kanalların %25'inden fazlası dışlanırsa denek "atipik spektrum" olarak işaretlenir, ROI tüm kanallarla hesaplanır ve sonuçlar bu denekler hariç tutularak da tekrarlanır.

## Diğer notlar
1. **EMG indeksi filtre etkisi içeriyor.** Ön işlemedeki alçak geçiren filtre (45 tap FIR, 128 Hz) geçiş bandı geniş; 30–40 Hz eğimine filtrenin kendi düşüşü de giriyor. Bu tüm denekler için aynı olduğundan göreli bir indeks olarak geçerli, ama mutlak değeri yorumlanmamalı.
2. **Posterior ROI'de bazı deneklerde 9'dan az kanal kaldı:** 11 denek, en az 6 kanal.
3. **IAF eksikleri:** Birincil fit tam kesitte yalnızca 1 denekte posterior alfa tepesi bulamadı. CoG IAF'ın hiç eksiği yok.
4. **Knee modelinde aşırı değerler var:** sub-1108sg2'de üs 3,4, knee parametresi yaklaşık 1500. Bu sonuçlar duyarlılık analizi için saklanıyor, birincil analize girmiyor.
5. **CLAUDE.md'de iki küçük düzeltme gerekebilir:**
   - sg2 ile cg'nin zamanca örtüştüğü ay aralığı "Nisan–Haziran" yazıyor. Nisan 2022'de cg kaydı yok; gerçek örtüşme Mayıs–Haziran 2022.
   - Genlik satırındaki değerler audit sonuçlarımla birebir tutmuyor. Audit'te kanal SD medyanları preprocessed dosyada cg 7,1, sg 6,7, sg2 7,2 µV; p yaklaşık 0,14.
