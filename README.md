Markdown
# 🧪 Bulut Tabanlı Laboratuvar Envanter Sistemi v2.0 (Cloud-Based Laboratory Inventory System)

Modern, hızlı, güvenli ve çoklu kullanıcı destekli bir şekilde laboratuvar envanterini, kimyasal stoklarını ve malzeme hareketlerini takip etmek için geliştirilmiş bulut tabanlı bir masaüstü uygulamasıdır. Projenin ilk versiyonundaki yerel SQLite ve CustomTkinter mimarisi; yerini **Flet (Flutter tabanlı) UI framework** ve **Neon PostgreSQL bulut veritabanı** entegrasyonuna bırakarak tamamen cross-platform, çok kullanıcılı ve gerçek zamanlı senkronizasyon yeteneğine kavuşturulmuştur.

## 🚀 Öne Çıkan Özellikler

* **Modern & Reaktif Arayüz:** Flet ile geliştirilmiş, kullanıcı dostu, göz yormayan ve asenkron mimariye sahip modern Karanlık/Aydınlık tema desteği.
* **☁️ Bulut Veritabanı Entegrasyonu:** Gücünü Neon PostgreSQL altyapısından alan, dünyanın her yerinden anlık erişilebilir ve şifrelenmiş güvenli veritabanı bağlantısı.
* **👥 Çoklu Kullanıcı & Oturum Yönetimi:** Laboratuvarda hangi personelin hangi işlemi gerçekleştirdiğini izleyen, kullanıcı bazlı kimlik doğrulama sistemi.
* **Çift Dil Desteği:** Tek tuşla arayüzdeki tüm dinamik metinleri, toast bildirimlerini ve alert dialogları Türkçe (TR) ve İngilizce (EN) dilleri arasında anında dönüştüren lokalizasyon katmanı.
* **Gelişmiş Geri Al/İleri Al (Undo/Redo):** Bellek üstünde nesne tabanlı çalışan ve hiçbir Flet versiyon güncellemesinden etkilenmeyecek şekilde optimize edilmiş Geri Al / İleri Al mekanizması.
* **Akıllı İçe/Dışa Aktarma:** Envanter verilerini otomatik olarak konumlara göre sıralı şekilde ve işlem geçmişini Excel (`.csv`) formatında dışa aktarma; mevcut Excel ve JSON verilerini sisteme güvenli bir şekilde yükleme katmanı.
* **Kullanıcı Bazlı Log (Detaylı Denetim Kaydı):** Hangi işlemin hangi kullanıcı tarafından, ne zaman yapıldığını; miktar değişikliklerinde eski ve yeni değerlerin ne olduğunu saniyesi saniyesine takip eden gelişmiş hareket geçmişi.
* **📊 Akıllı Kota Takibi:** Bağlantı bilgileri menüsü üzerinden PostgreSQL sistem dosyalarının boyutunu ve Neon Free Tier üzerindeki anlık 500 MB'lık kota kullanım oranını görsel ProgressBar ile takip edebilme.

### 🛡️ Otomatik Yedekleme ve Veri Güvenliği

Sisteminizdeki laboratuvar verilerinin kaybolmasını veya yanlışlıkla silinmesini önlemek için uygulamada **Akıllı Otomatik Yerel Yedekleme** ve **Bulut Kurtarma** sistemi bulunmaktadır:

* Uygulama içerisinde herhangi bir malzeme ekleme, silme veya düzenleme işlemi gerçekleştirildiğinde, o anki veritabanınızın tam bir kopyası (`.json` formatında) programın bulunduğu yerdeki **`Yedekler`** klasörüne otomatik olarak kaydedilir.
* Dosya kirliliğini ve disk doluluğunu önlemek amacıyla sistem sadece **en güncel 5 yedeği** tutar, daha eski yedekler arka planda otomatik olarak temizlenir.
* Herhangi bir veri kaybı veya bulut senkronizasyon problemi yaşarsanız, uygulama içindeki **Yedekleme -> Veritabanı (JSON) Yükle** seçeneğini kullanarak `Yedekler` klasöründeki istediğiniz tarihi seçip sisteminizi anında eski haline döndürebilirsiniz.

## 🛠️ Kullanılan Teknolojiler

* **Dil:** Python 3.11+
* **Arayüz Frameworkü:** Flet (Flutter for Python)
* **Veritabanı Motoru:** PostgreSQL (Hosted on Neon.tech)
* **Veritabanı Sürücüsü:** Psycopg2-binary
* **Mimari:** Modüler Nesne Yönelimli Programlama (OOP) ve Event-Driven UI

## 📐 Proje Yapısı

Proje, spagetti kod yapısından tamamen uzak, katmanlı ve her modülün kendi sorumluluğuna sahip olduğu clean-code prensiplerine uygun tasarlanmıştır:

* `main.py`: Uygulama yaşam döngüsü, pencere ayarları ve ana yönlendirici (Router).
* `ayarlar.py`: Renk paletleri, font konfigürasyonları ve TR/EN dil sözlükleri ile çeviri motoru.
* `veri.py`: PostgreSQL bulut bağlantı motoru, Undo/Redo hafıza yönetimi, otomatik yedekleme ve SQL sorguları.
* `ui_bilesenleri.py`: Toast mesajları, dialog pencereleri ve native işletim sistemi (Windows/Linux/Mac) dosya pencereleri araçları.
* `sayfa_baglanti.py`: Bulut veritabanı bağlantı ekranı ve link doğrulama katmanı.
* `sayfa_kullanici.py`: Kullanıcı giriş ve oturum yönetim ekranı.
* `sayfa_envanter.py`: Gelişmiş malzeme arama, filtreleme, alfabetik sıralama ve listeleme arayüzü.
* `sayfa_ekle.py`: Yuvarlatılmış modern hatlara (Smooth UI) sahip, validasyon korumalı yeni malzeme ekleme formu.
* `sayfa_konumlar.py`: Laboratuvar içi oda, dolap ve raf lokasyon yönetim modülü (Konum silindiğinde malzemeleri otomatik koruma altına alır).
* `sayfa_gecmis.py`: Kullanıcı aksiyonlarını geriye dönük detaylarıyla listeleyen loglama arayüzü.
* `sayfa_yedekleme.py`: Manuel veri yedekleme, Excel çıktısı alma ve bulut kurtarma arayüzü.

## 🚀 Kurulum ve Çalıştırma

Uygulamayı kaynak kodundan (Windows, Linux, macOS) çalıştırmak isterseniz aşağıdaki adımları izleyebilirsiniz:

1. Depoyu bilgisayarınıza indirin ve proje klasörüne girin:

```bash
git clone [https://github.com/ErdemBK/laboratuvar-envanter-sistemi.git](https://github.com/ErdemBK/laboratuvar-envanter-sistemi.git)
cd laboratuvar-envanter-sistemi
Gerekli kütüphaneleri kurun:

Bash
pip install -r requirements.txt
(Linux/macOS kullanıcıları alternatif olarak şunu kullanabilir: python3 -m pip install -r requirements.txt)

Uygulamayı başlatın:

Bash
python main.py
(Linux/macOS kullanıcıları alternatif olarak şunu kullanabilir: python3 main.py)

📦 Dağıtım ve Dağıtılabilir Sürüm (Executable) Oluşturma
Terminal bağımlılığı olmadan, uygulamayı tek bir yürütülebilir (.exe veya binary) dosya haline getirip son kullanıcılara dağıtmak için iki güçlü seçeneğiniz vardır:

Seçenek A: Flet CLI ile Paketleme (Önerilen)
Bash
flet pack main.py --name "Bulut_Envanter_Sistemi"
Seçenek B: Standart PyInstaller ile Paketleme
Her seferinde terminal kullanmak istemiyorsanız, önce pip install pyinstaller komutunu çalıştırın. Ardından aşağıdaki komutla uygulamanın bağımsız çalıştırılabilir sürümünü oluşturabilirsiniz:

Bash
pyinstaller --noconfirm --onefile --windowed main.py
🐧 Linux Kullanıcıları İçin Önemli Çalıştırma Notu:
İşlem bittiğinde, proje klasörünüzün içindeki dist/ klasörüne girin. Derlenen dosyayı masaüstüne aldıktan sonra doğrudan çift tıklayarak çalıştırabilmek için işletim sistemine izin vermeniz gerekir:

Yöntem 1 (Terminal): Dosyanın olduğu klasörde terminal açın ve şu komutu uygulayın:

Bash
chmod +x Bulut_Envanter_Sistemi
Yöntem 2 (Arayüz): Dosyaya sağ tıklayıp Özellikler > İzinler (Properties > Permissions) kısmından "Dosyayı bir program gibi çalıştırmaya izin ver" (Allow executing file as program) seçeneğini işaretleyin.

[!IMPORTANT]
Önemli Güvenlik ve Kota Notu:

PostgreSQL mimarisinin doğası gereği, veritabanı tamamen boş olsa dahi sistem katalogları ve şema dosyaları nedeniyle standart olarak ~7.5 MB depolama alanı kaplar. Uygulama içerisine ekleyeceğiniz her bir malzeme kaydı sadece birkaç bayt boyutunda yer kapladığından, Neon Free Tier tarafından sunulan 500 MB'lık ücretsiz kota on binlerce ürünlük bir laboratuvarda dahi güvenle yetecektir.

Güvenliğiniz için bulut veritabanı bağlantı linkinizi (postgresql://...) kimseyle paylaşmayınız. Projeyi GitHub'a yüklemeden önce gizli bilgilerin internete sızmasını önlemek adına .env ve yerel_hafiza.json dosyalarının temizlendiğinden veya .gitignore listesinde yer aldığından emin olunuz.

Geliştirici: Erdem Büyükkahraman