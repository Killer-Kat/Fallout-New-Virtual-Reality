# Proje Yol Haritası

Bu doküman, FNVR (Fallout: New Virtual Reality) modunun geliştirme sürecini aşamalara ayırarak detaylı bir yol haritası sunar.

---

### 🏗️ AŞAMA 1: Temelleri Sağlamlaştırma ve Kullanıcı Deneyimi (UX) ✅ [TAMAMLANDI]

Bu aşamanın temel amacı, modu teknik bilgisi olmayan son kullanıcılar için bile kolayca kurulabilir, yapılandırılabilir ve stabil bir hale getirmektir.

-   **1.1. Harici Yapılandırma Dosyası (`config.ini`) Oluşturma:** ✅
    -   Tüm sert kodlanmış değerler config.ini dosyasına taşındı
    -   Kullanıcılar artık kod düzenlemeden ayarları yapabilir

-   **1.2. Basit Grafiksel Kullanıcı Arayüzü (GUI) Ekleme:** ✅
    -   Tkinter tabanlı modern GUI implement edildi
    -   Başlat/Durdur kontrolleri
    -   Gerçek zamanlı durum göstergeleri
    -   Dosya yönetimi ve tercih kayıt sistemi

-   **1.3. Güçlü Hata Yönetimi ve Günlükleme (Logging):** ✅
    -   Kapsamlı try-except blokları
    -   Detaylı log dosyası (fnvr_tracker.log)
    -   GUI'de anlaşılır hata mesajları

---

### 🎮 AŞAMA 2: Çekirdek Mekanikleri İyileştirme ✅ [TAMAMLANDI]

Bu aşama, modun temel çalışma prensiplerini daha performanslı ve "native" hissettirecek şekilde yeniden yapılandırmaya odaklanır.

-   **2.1. Süreçler Arası İletişimi (IPC) Güçlendirme:** ✅
    -   Memory-Mapped Files (MMAP) implement edildi
    -   <1ms gecikme sağlandı (INI'nin 10-20x katı hız)
    -   Otomatik fallback mekanizması eklendi
    -   Performans benchmark sistemi entegre edildi

-   **2.2. Kontrolcü Verilerini Yumuşatma (Data Smoothing):** ✅
    -   Üç farklı filtre implement edildi: Moving Average, Exponential, One Euro
    -   One Euro Filter önerilen seçenek (adaptif yumuşatma)
    -   GUI'de yumuşatma kontrolleri eklendi
    -   Pozisyon ve rotasyon için ayrı yumuşatma

-   **2.3. Gelişmiş Hareket (Gesture) Tanıma:** ✅
    -   Velocity tracking sistemi eklendi
    -   Dwell time gerekliliği implement edildi (0.5 saniye varsayılan)
    -   Cooldown mekanizması eklendi (1 saniye)
    -   Yanlışlıkla tetiklenme önlendi

---

### ✨ AŞAMA 3: Yeni Özellikler ve Derinlik [🔄 DEVAM EDİYOR]

Sağlam bir temel atıldıktan sonra, VR deneyimini zenginleştirecek yeni ve heyecan verici özellikler eklenebilir.

#### Tamamlanan Özellikler:

-   **3.2. Sol El Desteği:** ✅
    -   İki kontrolcü algılama ve takibi implement edildi
    -   Sol/sağ el rolü otomatik belirleme eklendi
    -   GUI'de el seçim kontrolleri eklendi
    -   İki el silah modu (çift elle tutma mekaniği) eklendi
    -   Config dosyasına dual_hand bölümü eklendi

#### Devam Eden Özellikler:

-   **3.1. Gerçekçi Yakın Dövüş (Melee) Sistemi:** 🔄
    -   **Görev:** Kontrolcünün anlık hızını (velocity) takip etmek. Hız, belirlenen bir eşiği geçtiğinde oyuna melee saldırı komutu göndermek.
    -   **Faydası:** VR'da dövüş hissini kökten değiştirerek tuşa basmak yerine gerçekçi savurma hareketleriyle saldırı yapmayı mümkün kılar.

#### Gelecek Özellikler:

-   **3.3. Haptik Geri Bildirim (Haptic Feedback):** 📅
    -   **Görev:** Oyundan "ateş edildi", "hasar alındı" gibi olayları dinleyerek, bu olaylara karşılık gelen titreşim komutlarını kontrolcüye göndermek.
    -   **Faydası:** Oyuncunun dünyayla etkileşimini fiziksel olarak hissetmesini sağlar.

-   **3.4. Fiziksel Şarjör Değiştirme:** 📅
    -   **Görev:** Reload tuşuna basmak yerine, kontrolcüyle belirli bir hareket yaparak şarjör değiştirme.
    -   **Faydası:** Daha gerçekçi ve sürükleyici bir deneyim.

## Mevcut Durum (Ocak 2025)

### ✅ Tamamlanan Özellikler
- Yapılandırma sistemi (config.ini)
- Grafiksel kullanıcı arayüzü (Tkinter)
- Hata yönetimi ve loglama
- Memory-mapped file iletişimi (<1ms gecikme)
- Veri yumuşatma (One Euro Filter)
- Gelişmiş hareket tanıma
- İki el desteği ve kontrolcü algılama
- İki el silah modu

### 🔄 Aktif Geliştirmeler
- Melee sistemi (hız bazlı hasar)
- Dokümantasyon güncellemeleri

### 📅 Yakın Gelecek
- Haptik geri bildirim
- Fiziksel şarjör değiştirme
- Sol el etkileşimleri (kapı, eşya vb.)

## Teknik Detaylar

### Performans İyileştirmeleri
- **INI Yazma**: ~10-20ms → **MMAP Yazma**: <1ms
- **Ham Veri**: Titremeli → **One Euro Filter**: Akıcı ve hassas
- **Basit Jestler**: Yanlış tetikleme → **Velocity + Dwell**: Güvenilir

### Mimari Geliştirmeler
- Modüler yapı (tracker_logic, app_gui, mmap_communication vb.)
- Thread-safe GUI güncellemeleri
- Otomatik fallback mekanizmaları
- Kapsamlı hata yakalama ve loglama

## Kullanıcı Deneyimi

### Kolay Kurulum
1. Python kur
2. `pip install -r requirements.txt`
3. `python FNVR_Tracker.py`
4. GUI'den INI dosyasını seç
5. Başlat!

### GUI Özellikleri
- Gerçek zamanlı durum göstergeleri
- El seçimi kontrolleri
- Yumuşatma ayarları
- Detaylı log penceresi
- Tercih kaydetme sistemi 