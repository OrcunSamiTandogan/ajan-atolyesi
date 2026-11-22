# Sık sorulan sorular

## İlk kurulum

**Claude veya Codex olmadan kullanabilir miyim?**
Evet. Atölye'yi kur, **NVIDIA anahtarı**'na tıkla, anahtarını kaydet, örnek ZIP klasörünü seç ve **Pi**'ye tıkla. Pi yoksa **Pi’yi kur**'a bas. Pi rotasında dsh ve Claude/Codex hesabı gerekmez.

**Pi kurulmadı veya Node/npm bulunamadı. Ne yapmalıyım?**
Pi'nin npm kurulumu Node.js **22.19 veya üzeri** ister. [Pi'nin resmî rehberindeki](https://docs.pi.dev/latest/quickstart) kurucuyu kullanabilir veya güncel [Node.js](https://nodejs.org/) ve npm kurabilirsin. Windows'ta bunu Windows'a değil Ubuntu/WSL içine yap. Atölye'yi kapatıp yeniden aç. Aynı hata kalırsa normal terminalden `pi --version` çalıştır; uygulama menüsünün, yalnız terminal oturumunda ayarlanmış PATH'i görmeyebileceğini unutma.

**ZIP bağlantısı açılmıyor.**
[Depo ana sayfasını](https://github.com/OrcunSamiTandogan/ajan-atolyesi) açıp **Code → Download ZIP** yolunu kullan. Hesap anahtarı veya özel erişim satın alman gerekmez.

**Windows'ta Başlat'ta uygulamayı bulamıyorum.**
Ubuntu terminalinde `"${XDG_DATA_HOME:-$HOME/.local/share}/ajan-atolyesi/ac"` çalıştır. [Windows rehberi](windows.md) WSL 2 ve WSLg önkoşullarını açıklar.

**Yeni sürümü nasıl yüklerim?**
Son ZIP'i indir ve sisteminin kurucusunu yeniden çalıştır. Atölye penceresini kapatıp aç. Kurucu uygulama dosyalarını yeniler, anahtar dosyasını yeniden oluşturmaz. Oturumlar arasında geçmek, çalışan terminali kapatmak demek değildir.

## Anahtar ve model

**Projenin `.env` dosyası boş. Anahtarım nerede?**
Soldaki **Atölye anahtarları (.env)** düğmesine tıkla. Varsayılan yol `~/.config/ajan-atolyesi/.env`; `XDG_CONFIG_HOME` ayarlıysa onun altındadır. Bu dosya şifreli kasa değil; sadece sahibi okuyup yazabilir (0600). Anahtarı proje `.env`'sine kopyalama, Git'e ekleme, ekran görüntüsüne veya sohbete koyma. Atölye üzerinden NVIDIA anahtarıyla açılan Pi başka sağlayıcıların ortam anahtarlarını almaz ve eklentileri yüklemez. Kendi araçları NVIDIA anahtarına erişebileceği için güvenmediğin projeyi açma.

## Anahtar kaydedilemiyor, ne yapmalıyım?

**Henüz girilmedi** yazıyorsa ilgili sağlayıcının düğmesinden anahtarı kaydet. **Kayıtlı**, anahtarın yerelde saklandığını gösterir; geçerliliği ancak sağlayıcıya istek atınca belli olur. Anahtar değişince ilgili açık oturumu kapatıp aç: NVIDIA için Pi, EVREN için DSH CLI ve DSH Web.

**Okunamadı** yazıyorsa mevcut dosya otomatik olarak ezilmez. **Atölye anahtarları (.env)** ekranındaki konumu aç. Dosya normal bir dosyaysa ve sana aitse, kendi özel ayar klasöründe farklı bir isme taşı; silme, paylaşma veya proje içine koyma. Ardından iki sağlayıcıdan kullandığın anahtarları maskeli ekrandan tekrar gir. Dosya sana ait değilse izinleri rastgele değiştirme; önce dosya konumunu kontrol et.

## NVIDIA modeli yavaş veya yanıt vermiyor, ne yapmalıyım?

Pi'de **Esc** ile bekleyen işi durdur, `/model` yaz, başka bir model seç. MiniMax açıksa **Nemotron 3.5 Lightning** veya **Kimi K3.1 Pro** deneyebilirsin. Önce tek cümlelik isteği tekrar gönder. Modelin listede görünmesi, hesabının onu çağırabildiğini göstermez.

| Ekranda ne var? | Sonraki adım |
|---|---|
| `401` / `403` | Doğru NVIDIA hesabından anahtar ve model erişimini kontrol et. Kaydet, Pi'yi yeniden aç. |
| `429` | İstek/kota sınırı olabilir. Tekrar denemeden önce bekle; sağlayıcı limitini kontrol et. |
| `404` veya model bulunamadı | `/model` ile bir başka NVIDIA modeli seç; model kataloğunu kontrol et. |
| Yanıt var ama dosya değişmiyor | Model yanıtı gördün; araç çağrısı ayrı. [Demo görevinin](../demo/GOREV.md) testini çalıştır. |

**NVIDIA kartı gerekir mi?**
Hayır. Bu rota NVIDIA'nın sunucularındaki API'yi kullanır. Hesabın, internet bağlantın ve model erişimin gerekir. Kota ve ücret sağlayıcının hesabına bağlıdır.

<a id="evren--dsh-cli-ve-dsh-web-farkı-ne" name="evren--dsh-cli-ve-dsh-web-farkı-ne"></a>

## DSH CLI ve DSH Web farkı ne?

**DSH CLI** tarayıcı açmadan `aa-evren-cli` tmux oturumuna bağlanır. **DSH >** satırına doğrudan mesaj yazıp Enter’a bas; Atölye mesajları tek resmî DSH SDK sürecine iletir. Cache ve token sayaçları varsa yanıt altında görünür. **DSH Web** ise DeepSeek’in kendi tarayıcı arayüzünü açar. İkisi aynı kayıtlı EVREN anahtarını ve DeepSeek V4.1 Flash’ı kullanır. [İlk kullanım rehberi](evren-dsh.md).

## Oturumlar ve güvenlik

**Claude veya Codex komutu bulunamadı.**
Bu araçları Atölye'nin kurulum düğmesi indirmez; düğme kurulu aracı açıp ona kurulum talimatı verir. Önce [Claude Code](https://code.claude.com/docs/en/setup) veya [Codex](https://learn.chatgpt.com/docs/auth) rehberini izle. Linux/macOS'ta normal terminalde `claude --version` veya `codex --version` çalıştır. Windows'ta komutu WSL içindeki Ubuntu terminalinde çalıştır. NVIDIA ile başlamak için bunları kurman gerekmez.

**“Codex ile teyit et”e bastım ama kontrol başlamadı.**
Açık `aa-codex` veya `aa-claude` oturumu bu Atölye’nin oluşturduğu normal izinli oturumsa uygulama ona geri bağlanır. Kimliği veya izin modu doğrulanamayan oturumlara bağlanmaz. Ana ad dışarıdan açılmış bir oturuma aitse Atölye kendi `aa-codex-atolye` veya `aa-claude-atolye` oturumunu açar; iki ad da başka oturumlara aitse hiçbirine dokunmaz. Doğrulama promptu mevcut oturuma otomatik gönderilmez. Ajan ekranda açıksa [doğrulama promptunu](../DOGRULAMA-PROMPTU.md) kendin gönder ve hangi aracı kontrol edeceğini belirt. İlk kurulum için [kurulum seçeneklerini](../BASLA.md) kullan.

**Satırdaki renkler ve × nedir?**
Koyu nokta terminalin kapalı, yeşil açık, mavi yakın zamanda ekrana çıktı geldiğini söyler. Modelin düşünüp düşünmediğini ölçmez. **×** ilgili oturumu sonlandırır; sadece başka satıra tıklamak onu çalışır bırakır.

**Ajana açık oturumları nasıl hatırlatırım?**
Sol menünün başlığındaki **Oturum hatırlatıcısı** simgesinden **Panoya kopyala**’yı seç, sonra metni ajanın mesaj alanına yapıştır. Metin, açıldığı anda görülen tam tmux adlarını ve gönderim kontrollerini içerir. Çalışan ajanın sistem ayarını değiştirmez ve hiçbir oturuma otomatik mesaj göndermez.

**Açık oturumun kimliğini nasıl kopyalarım?**
**Codex oturumu**, **Claude oturumu**, **Pi** veya **DSH CLI** satırına sağ tıkla, **Oturum kimliğini kopyala**’yı seç. Panoya aynı makinedeki açık oturumun gerçek tmux adı gider (örneğin `aa-codex`, `aa-codex-atolye` veya `aa-pi`). Bir ajana hedef verirken tahmin etmek yerine bu kopyalanan adı kullan. Bu işlem tek başına görev göndermez. Klasör seçiciyi değiştirmen açık tmux oturumunu taşımaz. Seçili klasör farklıysa Atölye, açık panelin klasörünü ayrıca gösterir. Kapalı oturumlar ile tmux kullanmayan DSH Web ve normal Terminal satırlarında seçenek pasiftir.

**Hangi izinlerle açılır?**
Bu dağıtım izinleri atlayan bir mod sunmaz. Normal mod, kullandığın aracın kendi onay ve erişim ayarlarına tabidir. tmux bir güvenlik katmanı değildir. Güvenmediğin repo, eklenti veya dışarıdan gelen PR'ları anahtarların ve hesapların olan bir bilgisayarda çalıştırma. Atölye'nin başlattığı Pi ve onun alt süreçleri NVIDIA anahtarına erişebilir; ilk denemede örnek projeyi kullan.

**Kurulum gerektirmeyen yol var mı?**
Atölye'yi kurmadan [manuel rehberi](manuel-kurulum.md) izle. Paketler ilgili CLI'lar için yine gerekir.
