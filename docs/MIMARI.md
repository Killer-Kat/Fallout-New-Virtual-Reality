# Proje Mimarisi

Bu doküman, FNVR (Fallout: New Virtual Reality) modunun teknik mimarisini, hem mevcut durumunu hem de planlanan geliştirmeleriyle birlikte açıklamaktadır.

## Mevcut Mimari (Versiyon 1.0)

Mevcut sistem, birbirinden ayrı çalışan iki ana bileşenden oluşur:

1.  **VR Takip Betiği (`FNVR_Tracker.py`):**
    *   **Görevi:** Kullanıcının bilgisayarında arka planda çalışan bir Python betiğidir. SteamVR aracılığıyla VR başlık (HMD) ve sağ el kontrolcüsünün pozisyon ve rotasyon verilerini okur.
    *   **İşlevi:** Kontrolcünün başlığa göre olan göreceli pozisyonunu hesaplar ve bu veriyi belirli aralıklarla bir `.ini` dosyasına yazar.
    *   **Teknolojiler:** Python, OpenVR, NumPy.

2.  **Oyun İçi Mod (Fallout: New Vegas):**
    *   **Görevi:** Oyun içinde çalışan ve NVSE (New Vegas Script Extender) gerektiren bir moddur. (Bu modun kaynak kodları bu projede yer almamaktadır).
    *   **İşlevi:** Her oyun döngüsünde (tick), Python betiğinin yazdığı `.ini` dosyasını okur. Okuduğu verileri, oyuncunun birinci şahıs kamera iskeletini manipüle etmek için kullanır. Bu sayede, oyuncunun elindeki silah, gerçek dünyadaki kontrolcünün hareketlerini takip eder.

### Veri Akışı (Mevcut)

`SteamVR` -> `FNVR_Tracker.py` -> `Meh.ini` (Dosya Yazma) -> `Oyun İçi Mod` (Dosya Okuma) -> `Oyun Motoru`

### Zayıf Yönleri

-   **Dosya Tabanlı İletişim (IPC):** `.ini` dosyası üzerinden iletişim kurmak yavaş, gecikmeye (latency) açık ve senkronizasyon hatalarına neden olabilecek kırılgan bir yöntemdir. "Native" bir hissiyatın önündeki en büyük engel budur.

---

## Planlanan Mimari (Versiyon 2.0)

Gelecek sürüm, daha performanslı ve stabil bir deneyim sunmak için iletişim katmanını yeniden yapılandırmayı hedefler.

1.  **VR Takip Uygulaması (Geliştirilmiş):**
    *   **Görevi:** Arka planda çalışmaya devam edecek, ancak basit bir GUI'ye sahip olacak. Ayarları bir `config.ini` dosyasından okuyacak.
    *   **İşlevi:** Kontrolcü verilerini okuduktan sonra, veriyi yumuşatma (smoothing) algoritmalarından geçirir ve **bellek haritalı dosya (memory-mapped file)** veya **UDP soketi** gibi modern bir IPC yöntemiyle doğrudan belleğe yazar.

2.  **Oyun İçi Mod (Geliştirilmiş):**
    *   **Görevi:** Oyun içinde çalışmaya devam edecek, ancak `.ini` dosyası okumak yerine doğrudan bellekten veri okuyacak şekilde güncellenmesi hedeflenir.
    *   **İşlevi:** Bellekten okunan anlık veriyi kullanarak oyuncu iskeletini günceller. Ayrıca, ateş etme gibi oyun içi olayları (events) takip ederek haptik geri bildirim için Python uygulamasına veri gönderebilir.

### Veri Akışı (Planlanan)

`SteamVR` -> `FNVR Takip Uygulaması` <-> (Bellek Haritalı Dosya / UDP) <-> `Oyun İçi Mod` <-> `Oyun Motoru`

### Güçlü Yönleri

-   **Düşük Gecikmeli İletişim:** Verinin disk yerine doğrudan bellek üzerinden aktarılması, gecikmeyi ortadan kaldırır ve çok daha akıcı bir deneyim sunar.
-   **Çift Yönlü İletişim:** Haptik geri bildirim gibi özellikler için oyunun da Python uygulamasına veri göndermesine olanak tanır.
-   **Stabilite:** Dosya I/O işlemlerinden kaynaklanan hatalar ve senkronizasyon sorunları ortadan kalkar. 