# Claude Code veya Codex’e kurdur

README’de seçtiğin kutunun sağ üstündeki kopyalama düğmesine bas ve promptu **kendi bilgisayarındaki Claude Code veya Codex terminaline** yapıştır. Normal izin ekranları açık kalır. İki sağlayıcının kurulumu birbirinden bağımsızdır; yalnız birini kullanmak için diğerinin anahtarı gerekmez.

## Pi ve EVREN

**İkisi birden: Pi + NVIDIA ve EVREN + DeepSeek**

```text
Ajan Atölyesi’ni ilk kez kuruyorum. Kesin seçimim: Pi + NVIDIA ve EVREN + DeepSeek, ikisi de. Seçimi tekrar sorma. Claude/Codex burada yalnız kurulum için; sağlayıcıların şartı olarak abonelik gösterme.

1. Yerel bilgisayarı ve işletim sistemini doğrula. Ajan Atölyesi kaynağı: https://github.com/OrcunSamiTandogan/ajan-atolyesi . Yerel repo veya çıkarılmış ZIP varsa onu kullan; yoksa yalnız bu deponun güncel master ZIP’ini kullan. Arşive ulaşılamıyorsa dur ve hatayı bildir; erişim anahtarı isteme. README.md ve yalnız bulunduğum sistemin rehberini oku: Ubuntu için docs/linux.md, macOS için docs/macos.md, Windows için docs/windows.md. Ubuntu’da GTK/VTE ve masaustune-kur.sh, macOS’ta Homebrew ve kur-macos.sh, Windows’ta Ubuntu 24.04 + WSL 2 + WSLg ve kur-windows.cmd yolunu izle. Windows yolu yerel .exe değildir. Grafik oturumuna erişimin yoksa pencereyi açmış gibi konuşma.

2. Pi ve resmî DeepSeek Harness (dsh) için Node.js 24.9+, npm ve Pi · NVIDIA ve DSH CLI için tmux kontrol et. Pi kaynağı: https://docs.pi.dev/latest/quickstart . DSH: docs/evren-dsh.md ve https://github.com/deepseek-ai/deepseek-harness/tree/master/apps/cli . Her yolu ayrı doğrula; biri takılırsa diğerini gereksiz yere durdurma. Yalnız eksik araçları, resmî kaynağı ve depodaki sabit sürümü kontrol ederek normal izinlerle kur. Yönetici onayı veya yeniden başlatma gerekiyorsa engeli aşma, gereken adımı söyle. Node ve npm’yi masaüstü uygulamasının Terminal satırından da kontrol et; yalnız giriş kabuğunda görünmeleri yeterli değil.

3. API anahtarımı sorma, okuma, yazma, yazdırma veya testte kullanma. Terminale, sohbete veya proje .env dosyasına koymamı isteme. Kurulum bitince anahtarı yalnız Atölye’nin maskeli alanına ben gireceğim. Önce NVIDIA anahtarı → Kaydet → proje seç → Pi · NVIDIA (varsayılan MiniMax M3.1 Flash). Sonra EVREN anahtarı → Kaydet → EVREN · DSH CLI (proje seç) veya EVREN · DSH Web (DeepSeek V4.1 Flash).

4. Uygulama açılışı, araç sürümü ve gerçek model yanıtı ayrı doğrulamalardır. Pi · NVIDIA için `aa-pi`, EVREN · DSH CLI için `aa-evren-cli` tmux hedefini ve sağ tık → Oturum kimliğini kopyala çıktısını anahtarsız testle ayrı doğrula. Her iki hedef de birbirinden bağımsızdır. Testi yapamazsan doğrulanmadığını söyle ve anahtarımı kaydettikten sonra kontrol sırasını göster. Kurulumda canlı model çağrısı yapma. İlk mesajı ben gönderirim: “Sadece MERHABA yaz.” Başka projelere, açık tmux oturumlarına, izin atlama moduna, Git push’a, yayın ve ödeme ayarlarına dokunma. Kısa Türkçe yanıt ver: Kurulanlar / Doğrulananlar / Şimdi basacağım düğme.
```

## Pi

**Yalnız Pi + NVIDIA**

```text
Ajan Atölyesi’ni ilk kez kuruyorum. Kesin seçimim: yalnız Pi + NVIDIA. Seçimi tekrar sorma. EVREN’i ve dsh’yi araştırma, kontrol etme, kurma veya ayarlama; EVREN anahtarı isteme. Claude/Codex burada yalnız kurulum için; ayrıca abonelik veya başka sağlayıcı gerekmiyor.

1. Yerel bilgisayarı ve işletim sistemini doğrula. Ajan Atölyesi kaynağı: https://github.com/OrcunSamiTandogan/ajan-atolyesi . Yerel repo veya çıkarılmış ZIP varsa onu kullan; yoksa yalnız bu deponun güncel master ZIP’ini kullan. Arşive ulaşılamıyorsa dur ve hatayı bildir; erişim anahtarı isteme. README.md ve yalnız bulunduğum sistemin rehberini oku: Ubuntu için docs/linux.md, macOS için docs/macos.md, Windows için docs/windows.md. Ubuntu’da GTK/VTE ve masaustune-kur.sh, macOS’ta Homebrew ve kur-macos.sh, Windows’ta Ubuntu 24.04 + WSL 2 + WSLg ve kur-windows.cmd yolunu izle. Windows yolu yerel .exe değildir. Grafik oturumuna erişimin yoksa pencereyi açmış gibi konuşma.

2. Pi için Node.js 22.19+, npm ve tmux kontrol et. Resmî Pi rehberi: https://docs.pi.dev/latest/quickstart . Sırf diğer kurulum seçeneği için Node yükseltme ya da başka araç ekleme. Yalnız eksik araçları, resmî kaynağı ve depodaki sabit sürümü kontrol ederek normal izinlerle kur. Yönetici onayı veya yeniden başlatma gerekiyorsa engeli aşma, gereken adımı söyle. Node ve npm’yi masaüstü uygulamasının Terminal satırından da kontrol et; yalnız giriş kabuğunda görünmeleri yeterli değil.

3. API anahtarımı sorma, okuma, yazma, yazdırma veya testte kullanma. Terminale, sohbete veya proje .env dosyasına koymamı isteme. Kurulum bitince anahtarı yalnız Atölye’nin maskeli alanına ben gireceğim. NVIDIA anahtarı → Kaydet → proje klasörünü seç → Pi · NVIDIA (varsayılan MiniMax M3.1 Flash).

4. Uygulama açılışı, araç sürümü ve gerçek model yanıtı ayrı doğrulamalardır. Pi · NVIDIA için `aa-pi` tmux hedefini ve sağ tık → Oturum kimliğini kopyala çıktısını anahtarsız testle ayrı doğrula. Testi yapamazsan doğrulanmadığını söyle ve anahtarımı kaydettikten sonra kontrol sırasını göster. Kurulumda canlı model çağrısı yapma. İlk mesajı ben gönderirim: “Sadece MERHABA yaz.” Başka projelere, açık tmux oturumlarına, izin atlama moduna, Git push’a, yayın ve ödeme ayarlarına dokunma. Kısa Türkçe yanıt ver: Kurulanlar / Doğrulananlar / Şimdi basacağım düğme.
```

## EVREN

**Yalnız EVREN + DeepSeek**

```text
Ajan Atölyesi’ni ilk kez kuruyorum. Kesin seçimim: yalnız EVREN + DeepSeek. Seçimi tekrar sorma. Pi ve NVIDIA’yı araştırma, kontrol etme, kurma veya ayarlama; NVIDIA anahtarı isteme. Claude/Codex burada yalnız kurulum için; ayrıca abonelik veya başka sağlayıcı gerekmiyor.

1. Yerel bilgisayarı ve işletim sistemini doğrula. Ajan Atölyesi kaynağı: https://github.com/OrcunSamiTandogan/ajan-atolyesi . Yerel repo veya çıkarılmış ZIP varsa onu kullan; yoksa yalnız bu deponun güncel master ZIP’ini kullan. Arşive ulaşılamıyorsa dur ve hatayı bildir; erişim anahtarı isteme. README.md ve yalnız bulunduğum sistemin rehberini oku: Ubuntu için docs/linux.md, macOS için docs/macos.md, Windows için docs/windows.md. Ubuntu’da GTK/VTE ve masaustune-kur.sh, macOS’ta Homebrew ve kur-macos.sh, Windows’ta Ubuntu 24.04 + WSL 2 + WSLg ve kur-windows.cmd yolunu izle. Windows yolu yerel .exe değildir. Grafik oturumuna erişimin yoksa pencereyi açmış gibi konuşma.

2. Resmî DeepSeek Harness (dsh) için Node.js 24.9+ ve npm, CLI için tmux kontrol et. docs/evren-dsh.md ve https://github.com/deepseek-ai/deepseek-harness/tree/master/apps/cli kullan. DSH CLI resmi SDK’ya bağlı ayrı tmux terminalidir; DSH Web resmî Harness ekranını tarayıcıda açar. Bunları ham API sohbetiyle veya birbiriyle karıştırma. Yalnız eksik araçları, resmî kaynağı ve depodaki sabit sürümü kontrol ederek normal izinlerle kur. Yönetici onayı veya yeniden başlatma gerekiyorsa engeli aşma, gereken adımı söyle. Node ve npm’yi masaüstü uygulamasının Terminal satırından da kontrol et; yalnız giriş kabuğunda görünmeleri yeterli değil.

3. API anahtarımı sorma, okuma, yazma, yazdırma veya testte kullanma. Terminale, sohbete veya proje .env dosyasına koymamı isteme. Kurulum bitince anahtarı yalnız Atölye’nin maskeli alanına ben gireceğim. EVREN anahtarı → Kaydet → EVREN · DSH CLI (proje klasörünü seç) veya EVREN · DSH Web (DeepSeek V4.1 Flash).

4. Uygulama açılışı, araç sürümü ve gerçek model yanıtı ayrı doğrulamalardır. EVREN · DSH CLI için `aa-evren-cli` tmux hedefini ve sağ tık → Oturum kimliğini kopyala çıktısını anahtarsız testle ayrı doğrula. EVREN · DSH Web için tmux hedefi bekleme. Testi yapamazsan doğrulanmadığını söyle ve anahtarımı kaydettikten sonra kontrol sırasını göster. Kurulumda canlı model çağrısı yapma. İlk mesajı ben gönderirim: “Sadece MERHABA yaz.” Başka projelere, açık tmux oturumlarına, izin atlama moduna, Git push’a, yayın ve ödeme ayarlarına dokunma. Kısa Türkçe yanıt ver: Kurulanlar / Doğrulananlar / Şimdi basacağım düğme.
```

**Atölye zaten kuruluysa:** **Claude ile kur** veya **Codex ile kur** içinde sağlayıcıları işaretleyebilirsin. Yeni oturuma yalnız seçtiğin yollar gönderilir; açık oturuma otomatik tekrar gönderilmez.

[Uygulamasız manuel kurulum](docs/manuel-kurulum.md) · [NVIDIA veya EVREN ile ilk oturum](README.md#2-nvidia-veya-evren-ile-ilk-oturumu-aç)
