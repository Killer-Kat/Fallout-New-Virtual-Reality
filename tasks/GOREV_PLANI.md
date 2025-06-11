# Görev Planı ve Takip Listesi

Bu doküman, Yol Haritası'nda belirtilen hedefleri gerçekleştirmek için gereken somut görevleri bir kontrol listesi formatında sunar.

---

### ✅ AŞAMA 1: Temelleri Sağlamlaştırma ve Kullanıcı Deneyimi (UX)

-   [x] **1.1. Yapılandırma (`config.ini`)**
    -   [x] Proje kök dizinine `config.ini` adında bir dosya oluştur.
    -   [x] `FNVR_Tracker.py` içine `configparser` kütüphanesini import et.
    -   [x] `file_path` değişkenini `config.ini`'den okuyacak bir fonksiyon yaz.
    -   [x] `update_ini` fonksiyonundaki tüm "sihirli sayıları" (pozisyon/rotasyon için ölçek ve ofset değerleri) `config.ini`'ye taşı.
    -   [x] Betiğin bu değerleri başlangıçta okuyup değişkenlere atamasını sağla.
    -   [x] `README.md` dosyasını `config.ini` kullanımı hakkında bilgilendirecek şekilde güncelle.

-   [x] **1.2. Grafiksel Kullanıcı Arayüzü (GUI)**
    -   [x] `FNVR_Tracker.py`'nin mantığını bir sınıf (`TrackerLogic`) içine al, GUI'den ayır.
    -   [x] `tkinter` kullanarak basit bir ana pencere oluştur (`app_gui.py` adında yeni bir betik olabilir).
    -   [x] Pencereye "Başlat" ve "Durdur" butonları ekle.
    -   [x] Butonların `TrackerLogic` sınıfının ilgili metodlarını çağırmasını sağla (takip işlemini ayrı bir thread'de başlatmak gerekebilir).
    -   [x] Pencereye "Durum:", "SteamVR:", "Kontrolcü:" etiketleri ve yanlarına güncellenecek durum metinleri (örn: "Bekliyor", "Bağlı", "Takip Ediliyor") ekle.
    -   [x] `TrackerLogic` sınıfının durum değişikliklerini GUI'ye bildirmesi için bir mekanizma kur (örn: callback fonksiyonları veya queue).

-   [x] **1.3. Hata Yönetimi ve Günlükleme (Logging)**
    -   [x] Python'un `logging` modülünü projeye dahil et.
    -   [x] `fnvr_tracker.log` adında bir dosyaya, seviyeli (INFO, WARNING, ERROR) ve zaman damgalı loglar yazacak şekilde yapılandır.
    -   [x] OpenVR başlatma (`openvr.init`) kısmını `try-except` bloğuna al ve başarısız olursa `logging.error` ile kaydet ve GUI'de göster.
    -   [x] Ana takip döngüsündeki `getDeviceToAbsoluteTrackingPose` kısmını `try-except` içine al, olası hataları yakala ve logla.
    -   [x] `config.ini` okuma hatası durumunda varsayılan değerler kullan ve bir uyarı (`logging.warning`) logla.

---

### ✅ AŞAMA 2: Çekirdek Mekanikleri İyileştirme

-   [x] **2.1. IPC Güçlendirmesi (`mmap`)**
    -   [x] Memory-mapped file iletişim modülü oluştur
    -   [x] INI dosya yazımlarını mmap ile değiştir
    -   [x] Performans karşılaştırması yap (10-20x hızlanma)
    -   [x] Otomatik fallback mekanizması ekle

-   [x] **2.2. Veri Yumuşatma (Smoothing)**
    -   [x] Moving average, exponential ve One Euro filtreleri implement et
    -   [x] Pozisyon ve rotasyon yumuşatma ekle
    -   [x] GUI'de yumuşatma kontrolü ekle
    -   [x] Config'e yumuşatma ayarları ekle

-   [x] **2.3. Gelişmiş Hareket Tanıma**
    -   [x] Velocity tracking ekle
    -   [x] Dwell time gerekliliği implement et
    -   [x] Cooldown sistemi ekle
    -   [x] Yanlışlıkla tetiklenmeleri önle

---

### 🔲 AŞAMA 3: Yeni Özellikler ve Derinlik

-   [ ] **3.1. Gerçekçi Melee**
    -   [ ] Kontrolcü hızını hesaplama
    -   [ ] Hız eşiği bazlı hasar hesaplama
    -   [ ] Savurma yönü algılama
    -   [ ] Melee silahı aktif olduğunda hız takibi

-   [x] **3.2. Sol El Desteği**
    -   [x] İkinci kontrolcü algılama
    -   [x] Sol/sağ el rolü belirleme
    -   [x] GUI'de el seçim kontrolleri
    -   [x] İki el silah modu
    -   [x] Config dosyasına sol el ayarları

-   [ ] **3.3. Haptik Geri Bildirim**
    -   [ ] OpenVR haptic API entegrasyonu
    -   [ ] Ateş etme titreşimi
    -   [ ] Hasar alma geri bildirimi
    -   [ ] Melee darbe hissiyatı

-   [ ] **3.4. Fiziksel Şarjör Değiştirme**
    -   [ ] Reload hareketi tanıma
    -   [ ] Şarjör çıkarma/takma animasyonu
    -   [ ] Farklı silah tipleri için özel hareketler 