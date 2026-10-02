# 04-A Excel öznitelik bütünlük denetimi: rapor (2026-10-01)

**Betik:** `04a_excel_audit_v1_2026-10-01.py`. Ham veriye yazılmadı.
**Okunanlar:**
- 2048 adet `v1.0.0/code/*.xlsx` ve `CAR_FREC_DATS.mat`
- `participants.tsv`
- 140 adet `acq-epochs .set` (yalnızca kimlik doğrulaması için)

**Çıktılar:** `04a_excel_audit_v1_2026-10-01_{structure,columns,n_points,mat_vs_excel,ids,id_match}.csv`

## 1. Yapı
- **Dosyalar:** 2048 dosya = 4 bant (DELTA, THETA, ALFA, BETA) × 4 koşul-epok (C_1, O_1, C_2, O_2) × 128 kanal.
- **İçerik:** her dosyada 112 satır ve 9 sütun: `Subject`, Power, RMS, Standarddesv, Minimun, Maximun, Symetry, Kurtosis, `Label`. Toplam 16 × 128 × 7 = 14.336 öznitelik.
- **Tutarlılık:** denek sırası ve Label bütün dosyalarda aynı. Yinelenen denek ya da satır yok.
- **Etiketler:** Label = 0 olan 66 denek var, hepsi cg. Label = 1 olan 46 denek var, hepsi sg.
- **Boş dosya:** `FR_Dats_band_THETA_EP_C_2_can_B12.xlsx` 0 bayt. Yayımlanan `v1.0.0.zip` içinde de 0 bayt, yani açarken bozulmadı; yayımlanan verinin bir kusuru. Aynı değerler `.mat` dosyasında mevcut.

## 2. Sütun kalitesi
- Okunabilen 14.329 sütunun hiçbirinde NaN yok. Tamamen sabit sütun da yok.
- **Kurtosis sütunlarının hepsi (2047) neredeyse sabit.** Değerler 1,49999 ile 1,50001 arasında; bu fark yalnızca float32 yuvarlama gürültüsü. Diğer 6 istatistikte sorun yok.

## 3. Kurtosis neden 1,5? İstatistikler tam 3 değer üzerinden hesaplanmış
- Aralarında fark olan 3 sayının popülasyon kurtosis'i matematiksel olarak her zaman 1,5'tir. Bu kanıtlanmış bir özdeşlik.

  > **İspat notu.**
  > - Üç sayının ortalamadan sapmaları d₁, d₂, d₃ olsun; tanım gereği d₁ + d₂ + d₃ = 0.
  > - p = d₁d₂ + d₁d₃ + d₂d₃ tanımlansın.
  > - İkinci kuvvetlerin toplamı: Σdᵢ² = (Σdᵢ)² − 2p = −2p.
  > - Dördüncü kuvvetlerin toplamı: Σdᵢ⁴ = (Σdᵢ²)² − 2Σ(dᵢdⱼ)².
  >   - Burada Σ(dᵢdⱼ)² = p² − 2·d₁d₂d₃·Σdᵢ = p².
  >   - Dolayısıyla Σdᵢ⁴ = 4p² − 2p² = 2p².
  > - Momentler: m₂ = −2p/3 ve m₄ = 2p²/3.
  > - Sonuç: m₄ / m₂² = (2p²/3) / (4p²/9) = **1,5**. Bu değer sayıların ne olduğundan bağımsızdır; tek koşul p ≠ 0, yani sayıların hepsinin eşit olmaması.
  > - Benzer şekilde, 3 değerin çarpıklığı |γ₁| ≤ 1/√2 ile sınırlıdır.
- **Doğrulama:**
  - |Symetry| değerlerinin hepsi ≤ 1/√2 ≈ 0,7071. Bu, 3 değer için çarpıklığın teorik üst sınırı; gözlenen en büyük değer tam olarak bu sınır (0,707107).
  - Ortalama = √(RMS² − SD²·2/3), yani SD örneklem SD'si (n − 1). Bundan ortanca değer = 3·ortalama − Min − Max olarak hesaplanır.
  - Bu yolla geri kurulan 3 değer, Symetry'yi tam olarak üretiyor (medyan hata 0; %99'luk dilimde 1e-6) ve SD'yi de tam olarak üretiyor. Ortanca değer %100 durumda [Min, Max] aralığında kalıyor.
  - SD popülasyon SD'si olarak alınırsa bu tutarlılık bozuluyor (%48).
- **Sonuç:** RMS, Standarddesv, Minimun, Maximun, Symetry ve Kurtosis, her bant × epok × kanal hücresi için yalnızca 3 sayıdan hesaplanmış. Kurtosis tanım gereği bilgi taşımıyor. Diğer 5 istatistik de aynı 3 sayının farklı özetleri, birbirinden bağımsız değil.
- **Bu 3 sayı frekans noktası mı?** Bu, aşağıdaki nedenlerle kesin değil.
  - Değerlerin hepsi pozitif (en küçüğü 0,109); bu spektral büyüklüklerle uyumlu.
  - Ama 3 Hz genişliğindeki deltada da 17 Hz genişliğindeki betada da sayı 3. Tek bir eşit aralıklı frekans ızgarası bunu açıklayamaz. Ya her bant için ayrı bir ızgara kullanılmış, ya da bu 3 sayı frekans noktası değil (örneğin epoğun 3 zaman alt-penceresi).
  - Hangisi olduğu ancak ham hesaplama yeniden üretilerek belirlenebilir. Bu ek bir çalışma ve şimdilik açık bir soru.
- **Power ayrı hesaplanmış:** Power/RMS² oranı sabit değil (medyan 0,58, IQR 1,0). log Power ile log RMS arasındaki korelasyon r = 0,61. Yani Power aynı 3 sayıdan türetilmemiş, başka bir hesaplamadan geliyor.

## 4. CAR_FREC_DATS.mat
- Tek değişkeni `Datos[bant][koşul][kanal]`; her biri 112 deneklik bir struct listesi. scipy'nin dosya listesini okuyamamasının nedeni dosyadaki MATLAB opak nesnesi; `loadmat` ile içerik okunabiliyor.
- **Excel ile birebir aynı:** 2047 dosyada mutlak fark 0; denek listesi ve Label aynı.
- Excel'de boş olan THETA C_2 B12 için tam veri yalnızca `.mat` dosyasında var.
- `.mat` dosyasında ham spektrum ya da sinyal yok, yalnızca aynı özet istatistikler var.

## 5. Bulgu (ayrı): Excel öznitelikleri yayımlanan veri setiyle eşleşmiyor
| | Sayı | Denekler |
|---|---|---|
| Excel'de olup participants.tsv'de ve veri setinde olmayan | **12** | cg: 2013, 2024, 2025, 2027, 2035, 2039, 2041, 2058, 2069, 2073, 2076; sg: 1011 |
| Veri setinde olup Excel'de olmayan | **40** | sg2: tüm 25 denek; sg: 1009, 1013, 1020, 1021 (kısa kayıtlar); cg: 2010, 2016, 2017, 2021, 2022, 2023, 2031, 2051, 2062, 2067, 2077 |
| Her ikisinde de olan | 100 | cg 55 + sg 45 |

**Kimlik doğrulaması.** Bu adım yalnızca kimlik kontrolü içindir; öznitelik değildir.
- **Yöntem:** Her denek için Excel'deki log-Power profili çıkarıldı: 4 bant × 4 epok × 128 kanal. Aynı profil `acq-epochs` dosyalarından Welch log bant gücüyle yeniden hesaplandı. Her öznitelik denekler arasında z-skora çevrildi ve Excel profilleri ile veri seti profilleri Pearson korelasyonuyla karşılaştırıldı.
- **Sonuç 1:** ID'si tutan 100 deneğin 100'ünde en iyi eşleşme deneğin kendisi.
  - Kendisiyle korelasyon: medyan r = 0,915. En yakın ikinci denekle: medyan r = 0,40.
  - Bu iki şeyi doğruluyor: Excel'deki epoklar acq-epochs epoklarıyla aynı sırada (C1, O1, C2, O2) ve Power bant gücünün monoton bir ölçüsü.
- **Sonuç 2:** Bilinmeyen 12 ID'nin hiçbiri yayımlanan bir kayıtla eşleşmedi. Bu 12 deneğin en iyi eşleşme korelasyonu r = 0,25–0,66; ayrıca en iyi eşleşmeler rastgele denekler, sg2 dahil.
  - sub-1011sg en yüksek değeri (r = 0,66) sub-1013sg ile verdi. Ama 1013sg'nin yalnızca 2 epoğu var ve bu değer doğrulanmış eşleşmelerin (≈0,9) çok altında. Eşleşme kabul edilmedi.
- **Yorum:**
  - Excel öznitelikleri, yayımlanan veri setinden kısmen farklı bir kohorttan üretilmiş: 12 deneğin EEG kaydı yayımlanmamış, 11 yayımlanmış cg kaydı ise Excel'de yok.
  - Excel'de sg2 grubu ve kısa kayıtlı 4 sg yok.
  - Bu nedenle Excel öznitelikleriyle elde edilecek herhangi bir sonuç, yayımlanan EEG'den yeniden üretilemez.

## 04-B için sonuçlar
- **Kaynak:** öznitelikler `.mat` dosyasından okunmalı; Excel'den tek farkı boş B12 dosyasının da dolu olması.
- **Kurtosis:** 1,5 sabiti bilgi taşımıyor, ama StandardScaler uygulanınca float gürültüsü birim varyansa büyüyor ve sahte öznitelikler ortaya çıkıyor. 04 planında nasıl ele alınacağı belirtildi.
- **Örneklem:** Excel'in 112 deneği. Duyarlılık analizi kimliği doğrulanmış 100 denekle yapılacak.
