# Fallout: New Virtual Reality (FNVR) Geliştirme Projesi

[![Lisans: MIT](https://img.shields.io/badge/Lisans-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Bu proje, orijinal [Fallout: New Virtual Reality](https://www.github.com/iloveusername/Fallout-New-Virtual-Reality) modunu temel alarak, onu daha stabil, kullanıcı dostu ve "native" bir VR deneyimi sunan bir seviyeye taşımayı hedefler.

## Projenin Amacı

Mevcut mod, VR hareket kontrollerini *Fallout: New Vegas*'a eklemek için dahiyane bir çözüm sunmaktadır. Ancak, teknik bilgi gerektiren kurulum süreci ve bazı mekaniksel sınırlamaları bulunmaktadır. Bu projenin amacı, bu temeli alıp aşağıdaki prensipler doğrultusunda geliştirmektir:

-   **Kullanıcı Dostu:** Modun kurulumu ve kullanımı, teknik bilgisi olmayan bir oyuncu için bile basit ve anlaşılır olmalıdır.
-   **Stabilite:** Oyun içi deneyim akıcı ve hatasız olmalıdır.
-   **Sürükleyicilik:** Mekanikler, oyuncuya gerçekten oyun dünyasının içindeymiş gibi hissettirmelidir.

## Mevcut Fonksiyonellik

-   Sağ el kontrolcüsü ile bağımsız nişan alma
-   **İki el desteği** - Sol ve sağ kontrolcüleri aynı anda kullanma
-   **İki el silah modu** - Gerçekçi iki elle tutma mekaniği
-   Gelişmiş el hareketleri tanıma (dwell time, velocity tracking, cooldown)
-   Grafik kullanıcı arayüzü (GUI) ile kolay kontrol
-   Memory-mapped file desteği ile ultra düşük gecikme (<1ms)
-   Veri yumuşatma ile titremesiz nişan alma (One Euro Filter)
-   Dinamik kontrolcü algılama
-   Detaylı hata yönetimi ve loglama

## Yol Haritası (Roadmap)

Proje, üç ana aşamada geliştirilecektir:

### ✅ Aşama 1: Temelleri Sağlamlaştırma ve Kullanıcı Deneyimi (UX)

-   [x] **Yapılandırma Dosyası:** Ayarların (örn: hassasiyet, dosya yolu) kod dışından yönetilmesi.
-   [x] **Grafiksel Arayüz (GUI):** Betiği tek tıkla çalıştıracak basit bir arayüz.
-   [x] **Hata Yönetimi:** Anlaşılır hata mesajları ve loglama.

### ✅ Aşama 2: Çekirdek Mekanikleri İyileştirme

-   [x] **IPC Güçlendirmesi:** Memory-mapped files ile <1ms gecikme.
-   [x] **Veri Yumuşatma:** One Euro Filter ile titremesiz nişan alma.
-   [x] **Gelişmiş Hareket Tanıma:** Velocity tracking ve dwell time ile güvenilir sistem.

### ✨ Aşama 3: Yeni Özellikler ve Derinlik

-   [ ] **Gerçekçi Melee:** Savurma hızına dayalı yakın dövüş mekaniği.
-   [x] **Sol El Desteği:** Çift el silahlar ve diğer etkileşimler için.
-   [ ] **Haptik Geri Bildirim:** Ateş etme, hasar alma gibi olaylarda titreşim.
-   [ ] **Fiziksel Şarjör Değiştirme:** Sürükleyiciliği artıran manuel doldurma hareketleri.

## Kurulum

### Sistem Gereksinimleri
-   Python >= 3.11
-   SteamVR
-   VR başlık ve kontrolcüler (HTC Vive, Valve Index, Oculus vb.)
-   Fallout: New Vegas (Steam sürümü)
-   VorpX

### Kurulum Adımları

1.  **Python'u yükleyin** (3.11 veya üzeri)
2.  **Bağımlılıkları yükleyin:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **`config.ini` dosyasını yapılandırın:**
    - `ini_file_path` değerini kendi Fallout New Vegas kurulum dizininize göre ayarlayın
    - Örnek: `E:/SteamLibrary/steamapps/common/Fallout New Vegas/Data/Config/Meh.ini`
    - MMAP kullanmak isterseniz `mmap_file_path` değerini de ayarlayın
4.  **SteamVR'ı başlatın**
5.  **Tracker'ı çalıştırın:**
    ```bash
    python FNVR_Tracker.py
    ```
6.  **GUI'de şu adımları izleyin:**
    - INI dosya yolunu kontrol edin (gerekirse "Gözat" ile değiştirin)
    - İsterseniz "El Seçimi" bölümünden ayarları yapın:
      - **Tek el modu:** Varsayılan, sadece seçili el takip edilir
      - **İki el modu:** Her iki kontrolcü de takip edilir
      - **İki el silah modu:** İki el modu aktifken kullanılabilir
    - "Başlat" butonuna tıklayın
7.  **Oyunu VorpX ile başlatın**

### Yapılandırma (config.ini)

Mod artık tüm ayarları `config.ini` dosyasından okumaktadır. Bu dosya şu bölümleri içerir:
- **[paths]**: INI dosya yolu
- **[position_scaling]**: Pozisyon ölçekleme ve ofset değerleri
- **[rotation_scaling]**: Rotasyon ölçekleme ve ofset değerleri
- **[pipboy_position]**: Pipboy için sabit pozisyon değerleri
- **[pipboy_gesture]**: Pipboy açma hareketi ayarları
- **[pause_menu_gesture]**: Pause menüsü açma hareketi ayarları
- **[timing]**: Zamanlama ayarları (döngü gecikmesi, tuş basma süreleri)
- **[communication]**: İletişim yöntemi (mmap/ini) ve MMAP dosya yolu
- **[smoothing]**: Veri yumuşatma ayarları (filtre tipi, güç)
- **[gesture_recognition]**: Gelişmiş hareket tanıma (dwell time, cooldown, velocity)
- **[dual_hand]**: İki el desteği ayarları

### GUI Kullanımı

#### Ana Kontroller
- **Başlat/Durdur**: VR takibini başlatır veya durdurur
- **INI Dosya Yolu**: Oyunun INI dosyasını seçmenizi sağlar

#### El Seçimi
- **İki El Modunu Etkinleştir**: Her iki kontrolcüyü de takip eder
- **Aktif El**: Tek el modunda hangi elin kullanılacağını seçer
- **İki El Silah Modu**: İki elle tutma mekaniğini etkinleştirir (sadece iki el modunda)

#### Yumuşatma Ayarları
- **Veri Yumuşatmayı Etkinleştir**: Titreme azaltma sistemini açar/kapar
- **Yumuşatma Gücü**: Ne kadar yumuşatma uygulanacağını ayarlar (0.1-5.0)

#### Durum Göstergeleri
- **Durum**: Genel sistem durumu
- **SteamVR**: VR bağlantı durumu
- **Kontrolcü**: Kontrolcü bağlantı ve takip durumu
- **Takip**: Aktif takip durumu

### Performans

Memory-mapped file (MMAP) modu etkinleştirildiğinde:
- **INI dosya yazma**: ~10-20ms
- **MMAP yazma**: <1ms
- **Performans artışı**: 10-20x

### İki El Modu Özellikleri

#### Tek El Modu (Varsayılan)
- Sadece seçili el (sağ veya sol) takip edilir
- Diğer el yok sayılır
- Daha az işlemci kullanımı

#### İki El Modu
- Her iki kontrolcü de algılanır ve takip edilir
- Gelecekte iki elle etkileşim özellikleri için altyapı
- İki el silah modu etkinleştirilebilir

#### İki El Silah Modu
- İki kontrolcü arasındaki mesafe hesaplanır
- Eller belirli mesafede olduğunda silah iki elle tutulmuş gibi davranır
- Daha stabil nişan alma sağlar
- Min/max mesafe config'den ayarlanabilir

Detaylı bilgi ve geliştirme planı için `docs` klasörünü inceleyebilirsiniz.

## Katkıda Bulunma

Proje açıktır ve katkılarınızı bekliyoruz. Lütfen bir "issue" açarak veya "pull request" göndererek sürece dahil olun.
