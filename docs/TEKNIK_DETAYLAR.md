# Teknik Detaylar

Bu doküman, `FNVR_Tracker.py` betiğinin mevcut yapısını, kullanılan temel fonksiyonları ve planlanan iyileştirme alanlarını detaylandırmaktadır.

## `FNVR_Tracker.py` Analizi

### 1. Bağımlılıklar

-   `math`: Standart matematiksel işlemler için.
-   `keyboard`: Oyun içi eylemleri tetiklemek amacıyla tuş basımı simülasyonu için.
-   `openvr`: SteamVR ile iletişim kurarak takip verilerini almak için temel kütüphane.
-   `time`: Döngü zamanlaması ve gecikmeler için.
-   `ctypes`: OpenVR kütüphanesinin C tabanlı veri tipleriyle uyumlu çalışmak için.
-   `numpy`: Vektör ve kuaterniyon (quaternion) gibi 3D matematik işlemlerini verimli bir şekilde gerçekleştirmek için.

### 2. Ana Fonksiyonlar ve Sınıflar

-   **`SimpleTrackingApp` Sınıfı:**
    -   `__init__()`: OpenVR sistemini bir arka plan uygulaması olarak başlatır.
    -   `shutdown()`: Uygulama kapatıldığında OpenVR bağlantısını güvenli bir şekilde sonlandırır.
    -   `run()`: Ana uygulama döngüsünü içerir. Bu döngü sürekli olarak:
        1.  Başlık (HMD) ve kontrolcünün en güncel pozlarını (pose) OpenVR'dan alır.
        2.  Bu pozlardan pozisyon ve rotasyon matrislerini çıkarır.
        3.  Kontrolcünün pozisyonunu ve rotasyonunu başlığa göre hesaplar (`relative_position`, `relative_rotation`).
        4.  Hesaplanan bu göreceli verileri `update_ini` fonksiyonuna gönderir.
        5.  Önceden tanımlanmış noktalara olan mesafeyi ölçerek jestleri (gesture) kontrol eder ve ilgili tuşları tetikler.
        6.  İşlemciyi yormamak adına kısa bir süre bekler.

-   **`update_ini(...)` Fonksiyonu:**
    -   Aldığı pozisyon ve rotasyon verilerini, kod içinde sert kodlanmış (hardcoded) "sihirli sayılarla" (magic numbers) çarparak ve toplayarak ölçeklendirir.
    -   Bu son değerleri, oyun tarafından okunacak olan `.ini` dosyasına yazar.

-   **`get_rotation()`, `get_position()`, `quaternion_*` Fonksiyonları:**
    -   Bunlar, OpenVR'dan gelen 4x4'lük dönüşüm matrislerinden anlamlı 3D pozisyon ve rotasyon verilerini (kuaterniyon olarak) çıkarmak için kullanılan yardımcı matematik fonksiyonlarıdır.

### 3. Mevcut Sorunlar ve İyileştirme Alanları

-   **Sert Kodlanmış Dosya Yolu (`file_path`):**
    -   **Sorun:** Kullanıcıların, betiğin çalışması için kendi oyun yollarını doğrudan Python kodunun içine yazmaları gerekmektedir. Bu, kullanıcı deneyimi açısından çok kötüdür.
    -   **Çözüm (Aşama 1):** Bu dosya yolunu bir dış `config.ini` dosyasına taşımak.

-   **"Sihirli Sayılar" (Magic Numbers):**
    -   **Sorun:** `update_ini` içerisindeki `*50`, `+15` gibi ölçeklendirme faktörleri deneme-yanılma ile bulunmuştur ve her kullanıcı için ideal olmayabilir. Hassasiyeti ayarlamak için kodu değiştirmek gerekir.
    -   **Çözüm (Aşama 1):** Bu değerleri, kullanıcıların kolayca değiştirebileceği bir `config.ini` dosyasına "sensitivity", "offset" gibi isimlerle taşımak.

-   **Basit Jest Tanıma:**
    -   **Sorun:** Jestler, kontrolcünün sabit bir 3D noktasına olan uzaklığına göre tetiklenir. Bu, kazara istenmeyen komutların (örn: yanlışlıkla Pip-Boy'u açma) verilmesine neden olabilir.
    -   **Çözüm (Aşama 2):** Sadece pozisyona değil, aynı zamanda hıza ve bir süre o pozisyonda kalma (dwell time) gibi faktörlere dayalı daha sağlam bir jest tanıma sistemi geliştirmek.

-   **Veri Titremesi:**
    -   **Sorun:** Kontrolcülerden gelen ham verilerdeki çok küçük, istemsiz el titremeleri bile doğrudan oyuna yansıyarak nişangahın titremesine neden olabilir.
    -   **Çözüm (Aşama 2):** Pozisyon verilerini oyuna göndermeden önce basit bir hareketli ortalama (moving average) veya benzeri bir yumuşatma (smoothing) filtresinden geçirmek.

## 4. İletişim Katmanı

### 4.1. Hibrit İletişim Sistemi

Proje artık iki farklı iletişim yöntemi desteklemektedir:

#### 4.1.1. Memory-Mapped File (MMAP) İletişimi
- **Gecikme:** <1ms
- **Veri Formatı:** 7 float değer (28 byte) binary format
- **Struct Format:** `'7f'` (fCanIOpenThis, fiX, fiY, fiZ, fiXr, fiZr, fpZr)
- **Avantajlar:** 
  - Ultra düşük gecikme
  - Yüksek performans (10-20x hızlı)
  - Gerçek zamanlı veri transferi
- **Dezavantajlar:** 
  - Daha karmaşık implementasyon
  - Debug edilmesi zor

#### 4.1.2. INI Dosya Tabanlı İletişim
- **Gecikme:** ~10-20ms
- **Veri Formatı:** Metin tabanlı key-value çiftleri
- **Avantajlar:** 
  - Basit implementasyon
  - Debug edilmesi kolay
  - Evrensel uyumluluk
- **Dezavantajlar:** 
  - Dosya I/O nedeniyle yüksek gecikme
  - Disk aşınması

### 4.2. Otomatik Fallback Mekanizması

Sistem varsayılan olarak MMAP kullanır. MMAP başarısız olursa:
1. Hata loglanır
2. `fallback_to_ini` ayarı kontrol edilir
3. True ise otomatik olarak INI moduna geçilir
4. GUI'de durum güncellenir

### 4.3. Performans Karşılaştırması

Başlangıçta otomatik benchmark çalıştırılır:
- 100 yazma işlemi üzerinden ortalama süre hesaplanır
- Sonuçlar log dosyasına ve GUI'ye yazılır
- Tipik sonuçlar: MMAP ~0.05ms, INI ~1-2ms

## 5. Veri Yumuşatma (Data Smoothing)

### 5.1 Filtre Türleri

#### Moving Average
- Son N örneğin ortalaması
- Basit ama gecikmeli
- Pencere boyutu: 5-10 örnek

#### Exponential Moving Average
- Ağırlıklı ortalama
- Daha az gecikme
- Alpha: 0.1-0.5

#### One Euro Filter (Önerilen)
- Adaptif low-pass filtre
- Düşük hızda yüksek hassasiyet
- Yüksek hızda düşük gecikme
- min_cutoff: 0.1-5.0 Hz
- beta: 0.0001-0.01

## 6. İki El Desteği

### 6.1 Kontrolcü Algılama
```python
# Tüm kontrolcüleri bul
for i in range(openvr.k_unMaxTrackedDeviceCount):
    device_class = vr_system.getTrackedDeviceClass(i)
    if device_class == openvr.TrackedDeviceClass_Controller:
        # Kontrolcü rolünü belirle
        role = vr_system.getControllerRoleForTrackedDeviceIndex(i)
```

### 6.2 El Rolleri
- `TrackedControllerRole_LeftHand`: Sol el
- `TrackedControllerRole_RightHand`: Sağ el
- `TrackedControllerRole_Invalid`: Belirsiz

### 6.3 İki El Silah Modu
```python
# Eller arası mesafe hesaplama
hand_distance = math.sqrt(
    (right_x - left_x)**2 + 
    (right_y - left_y)**2 + 
    (right_z - left_z)**2
)

# Mesafe eşiği kontrolü
if min_dist <= hand_distance <= max_dist:
    # İki elle tutuluyor
    avg_position = (right_pos + left_pos) / 2
```

### 6.4 Konfigrasyon
```ini
[dual_hand]
enabled = true/false
default_hand = right/left
two_handed_weapon_mode = true/false
two_handed_min_distance = 0.2
two_handed_max_distance = 0.8
```

## 7. GUI ve Kullanıcı Deneyimi

### 7.1 Durum Yönetimi
- Thread-safe queue ile GUI güncellemeleri
- Gerçek zamanlı durum göstergeleri
- Otomatik hata yakalama ve gösterimi

### 7.2 Tercih Yönetimi
```python
# preferences.json formatı
{
    "ini_path": "path/to/game.ini",
    "mmap_path": "path/to/mmap",
    "dual_hand_enabled": false,
    "default_hand": "right",
    "smoothing_enabled": true,
    "smoothing_strength": 1.0
}
```

### 7.3 GUI Bileşenleri
- **Ana Kontroller**: Başlat/Durdur
- **Dosya Seçimi**: INI dosya yolu
- **El Kontrolleri**: Tek/çift el, aktif el seçimi
- **Yumuşatma**: Aç/kapa ve güç ayarı
- **Log Penceresi**: Gerçek zamanlı bilgilendirme

## 8. Gelecek Özellikler

### 8.1 Melee Sistemi
- Hız bazlı hasar hesaplama
- Savurma yönü algılama
- Darbe hissiyatı (haptic)

### 8.2 Fiziksel Etkileşimler
- Şarjör değiştirme hareketleri
- Kapı açma/kapama
- Eşya toplama 