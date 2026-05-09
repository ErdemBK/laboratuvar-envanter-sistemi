# 🧪 Laboratuvar Envanter Sistemi (Laboratory Inventory System)

Modern, hızlı ve güvenli bir şekilde laboratuvar envanterini, kimyasal stoklarını ve malzeme hareketlerini takip etmek için geliştirilmiş bir masaüstü uygulamasıdır. Python ve CustomTkinter kullanılarak modern UI/UX prensiplerine uygun olarak tasarlanmıştır.

## 🚀 Öne Çıkan Özellikler

* **Modern Arayüz:** CustomTkinter ile geliştirilmiş, kullanıcı dostu ve göz yormayan Karanlık/Aydınlık tema desteği.
* **Çift Dil Desteği:** Tek tuşla Türkçe (TR) ve İngilizce (EN) dilleri arasında anında geçiş.
* **Gelişmiş Geri Al/İleri Al (Undo/Redo):** Nesne tabanlı işlem geçmişi takibi sayesinde hatalı işlemleri kolayca geri alma.
* **Güvenli Veritabanı:** SQLite ile yüksek performanslı veri depolama ve WAL (Write-Ahead Logging) modu ile veri güvenliği.
* **Akıllı İçe/Dışa Aktarma:** Envanter verilerini ve işlem geçmişini Excel (`.csv`) formatında dışa aktarma; mevcut Excel verilerini sisteme güvenli bir şekilde yükleme.
* **Yedekleme Sistemi:** Uygulama kapanışında otomatik yedekleme ve manuel veritabanı kurtarma seçenekleri.
* **Kullanıcı Bazlı Log:** Hangi işlemin hangi kullanıcı tarafından, ne zaman yapıldığını takip eden detaylı hareket geçmişi.

### 🛡️ Otomatik Yedekleme ve Veri Güvenliği

Sisteminizdeki laboratuvar verilerinin kaybolmasını veya yanlışlıkla silinmesini önlemek için uygulamada **Akıllı Otomatik Yedekleme** sistemi bulunmaktadır:

* Uygulamayı (EXE dosyasını) her kapattığınızda, o anki veritabanınızın bir kopyası (`.db` formatında) programın bulunduğu yerdeki **`Yedekler`** klasörüne otomatik olarak kaydedilir.
* Dosya kirliliğini önlemek amacıyla sistem sadece **son 5 günün** yedeğini tutar, daha eski yedekler arka planda otomatik olarak temizlenir.
* Herhangi bir veri kaybı yaşarsanız, uygulama içindeki **Yedekleme -> Veritabanını Kurtar** seçeneğini kullanarak `Yedekler` klasöründeki istediğiniz tarihi seçip sisteminizi anında eski haline döndürebilirsiniz.
## 🛠️ Kullanılan Teknolojiler

* **Dil:** Python 3.x
* **Arayüz:** CustomTkinter (Modern Tkinter Wrapper)
* **Veritabanı:** SQLite3
* **Mimari:** Modüler Nesne Yönelimli Programlama (OOP)

## 📦 Kurulum ve Çalıştırma

1.  Bu depoyu bilgisayarınıza indirin:
    ```bash
    git clone [https://github.com/ErdemBK/laboratuvar-envanter-sistemi.git](https://github.com/ErdemBK/laboratuvar-envanter-sistemi.git)
    ```
2.  Gerekli kütüphaneyi kurun:
    ```bash
    pip install -r requirements.txt
    ```
3.  Uygulamayı başlatın:
    ```bash
    python main.py
    ```

## 📐 Proje Yapısı

* `main.py`: Uygulama yaşam döngüsü ve ana pencere yönetimi.
* `veritabani.py`: Veritabanı işlemleri, kilit mekanizmaları ve SQL sorguları.
* `modeller.py`: Veri sınıfları ve doğrulama mantığı.
* `sayfa_*.py`: Modüler sayfa tasarımları.
* `ayarlar.py`: Renk paletleri, fontlar ve dil çevirileri.


> 🛑 **ÖNEMLİ NOT:** Uygulamayı (EXE dosyasını) mutlaka boş bir klasörün içinde çalıştırın. Program ilk açılışta veritabanı (`.db`) ve işlem kayıtları (`.log`) için otomatik olarak ek dosyalar oluşturacaktır. Masaüstünde dağınık durmaması için bir klasör içine almanız önerilir.

---
**Hazırlayan:** [Erdem Büyükkahraman](https://github.com/ErdemBK)