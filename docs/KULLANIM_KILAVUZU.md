# Fallout: New Virtual Reality Kullanım Kılavuzu

Bu kılavuz, FNVR Tracker'ı nasıl kuracağınızı ve kullanacağınızı adım adım açıklar.

## İçindekiler
1. [Sistem Gereksinimleri](#sistem-gereksinimleri)
2. [Kurulum](#kurulum)
3. [İlk Çalıştırma](#ilk-çalıştırma)
4. [GUI Kullanımı](#gui-kullanımı)
5. [El Modları](#el-modları)
6. [Yapılandırma](#yapılandırma)
7. [Sorun Giderme](#sorun-giderme)

## Sistem Gereksinimleri

### Minimum Gereksinimler
- Windows 10/11
- Python 3.11 veya üzeri
- SteamVR
- VR başlık ve kontrolcüler (HTC Vive, Valve Index, Oculus vb.)
- Fallout: New Vegas (Steam sürümü)
- VorpX

### Önerilen Sistem
- Intel i5-8600K veya AMD Ryzen 5 3600 üzeri işlemci
- 16GB RAM
- GTX 1070 veya RTX 2060 üzeri ekran kartı

## Kurulum

### 1. Python Kurulumu
1. [Python.org](https://python.org) adresinden Python 3.11+ indirin
2. Kurulum sırasında "Add Python to PATH" seçeneğini işaretleyin
3. Kurulum tamamlandıktan sonra komut satırında test edin:
   ```bash
   python --version
   ```

### 2. FNVR Tracker Kurulumu
1. Projeyi GitHub'dan indirin veya klonlayın
2. Proje klasörüne gidin
3. Gerekli paketleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

### 3. Oyun Yapılandırması
1. Fallout: New Vegas'ın kurulu olduğu dizini bulun
2. `Data/Config` klasörü yoksa oluşturun
3. Bu klasörde `Meh.ini` adında boş bir dosya oluşturun

## İlk Çalıştırma

### 1. SteamVR'ı Başlatın
- Steam'i açın
- SteamVR'ı başlatın
- Kontrolcülerinizin bağlı ve yeşil göründüğünden emin olun

### 2. FNVR Tracker'ı Başlatın
```bash
python FNVR_Tracker.py
```

### 3. GUI Açılışı
- Program başladığında GUI penceresi açılacak
- Durum göstergeleri başlangıçta gri olacak

### 4. INI Dosya Yolunu Ayarlayın
1. "Gözat..." butonuna tıklayın
2. Fallout New Vegas kurulum dizinine gidin
3. `Data/Config/Meh.ini` dosyasını seçin
4. Yol otomatik olarak kaydedilecek

## GUI Kullanımı

### Ana Kontroller

#### Başlat/Durdur
- **Başlat**: VR takibini başlatır
- **Durdur**: Takibi durdurur ve VR bağlantısını kapatır

#### Durum Göstergeleri
- **Durum**: Genel sistem durumu (Hazır, Çalışıyor, Hata vb.)
- **SteamVR**: VR bağlantı durumu
- **Kontrolcü**: Kontrolcü bağlantı ve takip durumu
- **Takip**: Aktif takip durumu

### El Seçimi

#### İki El Modu
- **Kapalı (Varsayılan)**: Sadece seçili el takip edilir
- **Açık**: Her iki kontrolcü de algılanır ve takip edilir

#### Aktif El Seçimi
- **Sağ El**: Sağ kontrolcü kullanılır (varsayılan)
- **Sol El**: Sol kontrolcü kullanılır
- Sadece tek el modunda aktiftir

#### İki El Silah Modu
- Sadece iki el modu açıkken kullanılabilir
- Eller belirli mesafede olduğunda silah iki elle tutulmuş gibi davranır
- Daha stabil nişan alma sağlar

### Yumuşatma Ayarları

#### Veri Yumuşatmayı Etkinleştir
- Kontrolcü titremelerini azaltır
- Daha akıcı hareket sağlar

#### Yumuşatma Gücü (0.1-5.0)
- **Düşük değer (0.1-1.0)**: Az yumuşatma, hızlı tepki
- **Orta değer (1.0-3.0)**: Dengeli performans (önerilen)
- **Yüksek değer (3.0-5.0)**: Çok yumuşatma, yavaş tepki

## El Modları

### Tek El Modu
- Basit ve performanslı
- Sadece seçili el takip edilir
- Çoğu oyun için yeterli

### İki El Modu
- Her iki kontrolcü de aktif
- Gelecek güncellemeler için altyapı
- Şu anda sadece sağ el silah kontrolü için kullanılır

### İki El Silah Modu
- Gerçekçi iki elle tutma
- Eller arası mesafe hesaplanır
- Min/max mesafe config'den ayarlanabilir
- Örnek kullanım:
  - Tüfekler için eller 20-80cm arasında
  - Ağır silahlar için daha geniş mesafe

## Yapılandırma

### config.ini Dosyası

#### Temel Ayarlar
```ini
[paths]
ini_file_path = E:/Steam/steamapps/common/Fallout New Vegas/Data/Config/Meh.ini

[communication]
method = mmap  # veya ini
mmap_file_path = path/to/mmap
fallback_to_ini = true
```

#### Pozisyon ve Rotasyon
```ini
[position_scaling]
x_scale = 50
y_scale = -50
z_scale = -50

[rotation_scaling]
xr_scale = -120
yr_scale = 0
zr_scale = 120
```

#### İki El Ayarları
```ini
[dual_hand]
enabled = false
default_hand = right
two_handed_weapon_mode = false
two_handed_min_distance = 0.2
two_handed_max_distance = 0.8
```

#### Yumuşatma
```ini
[smoothing]
enabled = true
filter = one_euro  # one_euro, exponential, moving_average
position_min_cutoff = 1.0
position_beta = 0.007
```

## Sorun Giderme

### SteamVR Bağlanamıyor
- SteamVR'ın açık olduğundan emin olun
- Başlık ve kontrolcülerin yeşil göründüğünü kontrol edin
- Steam'i yönetici olarak çalıştırmayı deneyin

### Kontrolcü Bulunamıyor
- Kontrolcülerin açık ve şarjlı olduğundan emin olun
- SteamVR'da kontrolcüleri yeniden eşleştirin
- USB bağlantılarını kontrol edin

### INI Dosyası Hatası
- Dosya yolunun doğru olduğundan emin olun
- `Data/Config` klasörünün var olduğunu kontrol edin
- Dosya izinlerini kontrol edin (yazma izni)

### Takip Titremesi
- Yumuşatmayı etkinleştirin
- Yumuşatma gücünü artırın (2.0-3.0 arası deneyin)
- Oda aydınlatmasını kontrol edin (base station takibi için)

### Performans Sorunları
- MMAP modunu etkinleştirin (config.ini'de)
- Tek el modunu kullanın
- Arka plan uygulamalarını kapatın

### Log Dosyası
Detaylı hata bilgisi için `fnvr_tracker.log` dosyasını kontrol edin.

## İpuçları

1. **İlk Kullanım**: Varsayılan ayarlarla başlayın, sonra özelleştirin
2. **Hassasiyet**: Oyun içi hassasiyet ayarlarını da düşürün
3. **Jestler**: Pipboy için kontrolcüyü yüzünüze doğru getirin
4. **İki El**: Ağır silahlar için iki el modunu deneyin
5. **Performans**: MMAP modu 10-20x daha hızlıdır

## Gelişmiş Özellikler

### Komut Satırı Kullanımı
```bash
# CLI modu (GUI olmadan)
python FNVR_Tracker.py --cli

# Özel config dosyası
python FNVR_Tracker.py --config my_config.ini
```

### Özel Jestler
config.ini'de jest pozisyonlarını özelleştirebilirsiniz:
```ini
[pipboy_gesture]
gesture_x = 0.12
gesture_y = 0.24
gesture_z = -0.29
```

### Performans İzleme
MMAP modunda otomatik benchmark çalışır ve sonuçlar log'a yazılır.

## Yardım ve Destek

- GitHub Issues: Hata bildirimi ve öneriler
- Discord: Topluluk desteği (yakında)
- Wiki: Detaylı dokümantasyon (yakında)