# Sürüm değerlendirmesi

Bu belge, **ilk kez kuran birinin neyi tamamlayabildiğini** ve hangi iddiaların henüz kanıtı olmadığını ayırır.

| Akış | Kanıt | Açık iş |
|---|---|---|
| Ubuntu: temiz ayarlarla kurulum | Bir Ubuntu bilgisayarda geçici boş HOME/XDG altında ilk kurulum ve üzerine kurulum, `.desktop` doğrulaması, kurulu başlatıcıdan GTK ve gömülü terminal geçti. | Başka Linux dağıtımları için garanti yok. |
| Claude/Codex olmadan Pi | Resmî Pi 1.6.0 paketi ayrı bir geçici dizinde kuruldu ve sürüm komutu doğrulandı. Temiz ayar üzerinden iki maskeli anahtarı kaydetme, Pi kurulum düğmesi, proje seçimi ve terminale geçiş GTK testinde sahte CLI/anahtarla geçti. | Canlı NVIDIA hesabıyla sıfırdan kayıt ve bir dosya düzenleme bu testin parçası değil. |
| NVIDIA modelleri | MiniMax varsayılan; Kimi ve MiniMax seçimi görüldü. MiniMax ve Nemotron kısa canlı isteklere yanıt verdi. | Kimi canlı testte zaman aşımına uğradı. Üç modelin kodlama başarısı karşılaştırılmadı. |
| EVREN | Ubuntu’da gerçek Chrome ve resmî dsh web ile aynı oturumda iki canlı yanıt tamamlandı; EVREN yönlendirme başlığı her iki turda DeepSeek V4.1 Flash, ikinci turda 320 cache-read token gösterdi. Yerel sahte sağlayıcı testinde anahtar ayrımı geçti. | Proje düzenleme ve web araçları bu sürümde kapalı. |
| EVREN CLI | Bir Ubuntu bilgisayarda `aa-evren-cli` içinde aynı gerçek `sdk-minimal` PID’si ve Harness kimliğiyle iki canlı DeepSeek turu tamamlandı. İlk tur 0, ikinci tur 1.152 cache okuma token’ı bildirdi. | Dosya ve web araçları kapalı; Mac/Windows’ta doğrulanmadı. |
| macOS | Kaynaktan `.app` üreten kurucu ve bağımlılık kontrolü mevcut. | Apple Silicon Mac'te temiz kurulum, Finder açılışı, gömülü terminal ve ilk oturum; Intel ayrıca denenmeli. Hazır imzalı ve notarize paket yok. |
| Windows | WSL 2/WSLg kurucu ve ayrı `ac-windows.cmd` başlatıcısı mevcut. | Gerçek Windows'ta kurulum dosyasına çift tıklama, ayrı başlatıcı, gömülü terminal ve ilk oturum. Başlat menüsü entegrasyonu garanti değil. |
| GitHub Actions | PR'da birim, Bash ve izole GTK kontrolleri tanımlı. Linux kurucusu ayrıca boş HOME/XDG ortamında çalıştırılır; üretilen menü girdisi doğrulanır ve kurulu `ac` başlatıcısıyla Xvfb altında terminal açılır. | `master` push'u CI çalıştırmaz. Yerel test sonucu GitHub Actions sonucu değildir. Kurulu resmî dsh ile anahtarsız loopback testi Ubuntu’da ayrıca `python3 -B tests/check_evren_transport.py` komutuyla çalıştırılır; varsayılan Actions işi bu testi çalıştırmaz. |

## Bir sonraki gerçek hesap kabul testi

1. Yeni bir kullanıcı ayarıyla ZIP'i aç; Claude ve Codex yüklemeden Pi'yi kur.
2. Güvendiğin örnek klasörü seç, NVIDIA anahtarını maskeli ekrandan kaydet ve Pi'yi aç.
3. Önce tek cümlelik yanıtı, sonra [demo görevinde](../demo/GOREV.md) dosya değişikliği ve iki testin geçtiğini ayrı ayrı kaydet.
4. Aynı akışı Mac ve Windows/WSL üzerinde ayrı ayrı dene. Bir adım çalışmadıysa işletim sistemi, tam hata ve takıldığın düğmeyi yaz. Anahtar ve kişisel verileri ekleme.
