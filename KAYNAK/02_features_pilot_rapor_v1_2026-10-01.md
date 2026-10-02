# Öznitelik pilotu: 3 denek (2026-10-01)

Pipeline 3 denekte hatasız çalıştı. Tam çalıştırmadan önce sizin karar vermeniz gereken iki sorun var: kas artefaktı ve tek parametreli FOOOF modelinin yetersiz kaldığı bir denek. Bir de IAF yöntemi değişmeli.

**Okunan:** 3 deneğin `desc-preprocessed_eeg.set` dosyası. Ham veriye yazılmadı. `specparam` kurulu değil; aynı algoritmanın önceki sürümü `fooof` 1.1 kurulu olduğu için onu kullandım.

**Yazılan (hepsi `analysis/` altında):**
- `02_features_v1_2026-10-01.py`: pipeline. Ayarlar dosyanın başında.
- `02_features_pilot_v1_2026-10-01.csv`: her denek için 128 kanal ve 4 ROI satırı.
- `02_features_pilot_v1_2026-10-01_psd.npz`: spektrumlar.
- `02_features_qcfig_v1_2026-10-01.py` ve `02_features_pilot_qc_v1_2026-10-01.png`: QC figürü.

## Ayarlar
- **Kesit:** 3. göz kapalı işaretinden 5 s sonra başlayan sabit 465 s. Üç denekte de Welch penceresi sayısı aynı (231).
  - Kesiti sabitledim çünkü cg'nin uzun bloğu 500 s'ye kadar çıkıyor; sabit kesit bu süre farkını öznitelikten çıkarıyor.
  - 480 değil 465 s seçtim, çünkü sub-2019cg'nin bloğu yalnızca 474 s.
- **Welch:** 4 s Hann penceresi, %50 örtüşme, 0,25 Hz çözünürlük.
- **Göreli bantlar:** delta 1–4, teta 4–8, alfa 8–13, beta 13–30, gama 30–40 Hz. Payda toplam 1–40 Hz gücü.
- **FOOOF:** 2–40 Hz aralığında fit, aperiodik mod `fixed`.
- **IAF:** FOOOF'un 7–14 Hz aralığındaki en güçlü tepesi.
- **ROI ve kanal eşlemesi:** Hesaplar kanal başına ve 4 ROI için yapılıyor: posterior, central, frontal, global. Biosemi kanallarını 10-20 sistemine channels.tsv'deki açıklamalarla eşledim.

## Posterior ROI sonuçları
| Denek | Göreli alfa | Göreli gama | Aperiodik üs | IAF (FOOOF) | R² |
|---|---|---|---|---|---|
| sub-1005sg | 0,20 | 0,077 | 0,79 | 11,6 Hz | 0,987 |
| sub-1108sg2 | 0,52 | 0,005 | 1,99 | 10,1 Hz | 0,992 |
| sub-2019cg | 0,54 | 0,013 | 1,52 | 9,3 Hz | 0,996 |

## Dikkat edilmesi gerekenler
1. **Kas artefaktı.**
   - sub-1005sg'nin inion çevresindeki 4 kanalında (A13, A14, A26, A27) R² 0,34–0,59 ve üs 0,14–0,35. sub-2019cg'nin temporal kanallarında da R² 0,75–0,90.
   - Kas aktivitesi spektrumu düzleştirir ve üssü düşürür. 1005sg'nin düşük üssü (0,79) ve yüksek gaması (0,077) büyük olasılıkla bundan kaynaklanıyor.
   - Kas gerginliği gruba (ıslah kurumu ile okul) bağlı olabilir; o zaman üs farkı sahte bir bulgu olur. Bu durumda üs, kanal düzeyinde ham haliyle kullanılamaz.
   - Önerim: deneğe ve kanala göre bir EMG indeksi hesaplamak (ör. 30–40 Hz eğimi ya da gama oranı), R² < 0,9 olan kanalları dışlamak, ROI ortalamasını kalan kanallarla almak ve EMG indeksini grup analizinde ortak değişken olarak kullanmak.
2. **PSD argmax ile hesaplanan IAF güvenilmez.** 382 kanalın 164'ünde FOOOF tepesinden 0,5 Hz'den fazla sapıyor. Alfanın zayıf olduğu kanallarda 7 Hz'e, yani arama sınırına yapışıyor. Önerim: argmax'ı çıkarmak, yerine aperiodik bileşeni çıkarılmış spektrumda alfa ağırlık merkezini (CoG) koymak.
3. **sub-1108sg2'de model yetersiz.** 2–5 Hz arası düz (plato) seyrediyor, `fixed` model bunu yakalayamıyor. Bu yüzden üs (1,99) şişmiş olabilir. Seçenekler: `knee` modunu denemek ya da fit aralığını 3–40 Hz'e çekmek. Hangisinin daha iyi olduğunu tüm örneklemde R² ve hata karşılaştırmasıyla seçmek gerekir.
4. **Uyanıklık düşüşü.** 8 dakika göz kapalı kalmak uyuklamaya yol açabilir; alfa düşer, teta artar. 1005sg'nin çok tepeli, zayıf alfası buna uyuyor. Uyanıklık gruplar arasında farklıysa bu da bir confound olur. Önerim: öznitelikleri ilk ve ikinci yarı (2 × ~230 s) için ayrı ayrı da hesaplamak ve bunu duyarlılık analizi olarak kullanmak.

## Tam çalıştırmadan (135 denek) önce kararınız gereken noktalar
- **EMG:** R² eşiği ve EMG ortak değişkeni yaklaşımını onaylıyor musunuz?
- **FOOOF:** `knee` modu mu, 3–40 Hz `fixed` mı? İkisini de 135 denekte koşup karşılaştırmayı öneriyorum.
- **IAF:** argmax'ı çıkarıp yerine CoG koymamı onaylıyor musunuz?
- **Uyanıklık:** blok yarıları ayrı ayrı hesaplansın mı?
- **specparam:** `specparam` kurulsun mu, yoksa `fooof` 1.1 ile mi devam edelim? fooof 1.1 tam çalışıyor ama artık güncellenmiyor.
