# DeepSeek Harness (DSH)

İki ayrı düğme, aynı resmî dsh paketi ve EVREN’de **DeepSeek V4.1 Flash**. dsh henüz yoksa iki düğmeden de **dsh’yi kur** görünür. Kurulum için **Node.js 24.9+**, npm; CLI oturumu için ayrıca tmux gerekir. Claude, Codex veya NVIDIA hesabı şart değil.

## DSH CLI: tmux ve Codex için

1. **EVREN anahtarı** ekranından anahtarını kaydet. Projede `.env` oluşturma.
2. Atölye’de proje klasörünü seç, **DSH CLI**’ye tıkla. `aa-evren-cli` oturumu açılır veya varsa ona dönülür. Tarayıcı açılmaz.
3. Terminalde **DSH >** karşısına düz metin yaz ve Enter’a bas. Bash komutu yazman gerekmez. Atölye, **tek bir resmî `dsh --profile sdk-minimal` süreci** açar. Mesajlar aynı Harness oturumuna gider; yanıt ve sağlayıcının bildirdiği cache/token sayaçları SDK olaylarından gelir. Bu satır Atölye’ye aittir; DeepSeek’in yerleşik TUI’si değildir. `/new` yeni DSH kimliği açar, `/id` o anki DSH kimliğini gösterir, `/exit` oturumu kapatır. DSH kimliği ile tmux hedefi `aa-evren-cli` farklıdır. CLI oturumunu kapatınca geçici SDK sohbet geçmişi silinir; `/id` sonraki açılış için bir geri yükleme kodu değildir.
4. Codex’e hedefi vermek için **DSH CLI** satırına sağ tıkla → **Oturum kimliğini kopyala**. Kopyalanan ad `aa-evren-cli`. Bu ad tek başına görev göndermez. Açık oturum önceki çalışma klasöründe kalır; yeni proje için önce işi bitirip oturumu kapat.

Çıktıyı otomatik işlemek için **normal terminalde**, repo klasöründen `./bin/ajan-dsh --json "Görev metni"` çalıştır. Uzun görevi `./bin/ajan-dsh --json - < gorev.txt` ile ver. Bu komutları **DSH >** satırına yazma; orası düz metin içindir. Bunlar resmî dsh JSON olaylarıdır; tamamlanma için süreç çıkışı ve `final.reason.kind` birlikte kontrol edilir. CLI bu ilk sürümde metin görevleri alır; dosya ve web araçları kapalı. Eski `bash` veya `dsh headless` ekranı kalmışsa CLI oturumunun yanındaki **×** ile kapat ve yeniden aç. Projeden metin eklemeden önce metnin EVREN’e gideceğini unutma.

## DSH Web: resmî tarayıcı arayüzü

1. **EVREN anahtarı** düğmesinden anahtarını kaydet. Proje için `.env` oluşturma.
2. **DSH Web**'e tıkla. Uyumlu dsh yoksa **dsh’yi kur** görünür. Kurulum Node.js **24.9+** ve npm ister; Claude, Codex veya NVIDIA gerekmez.
3. **DSH Web**'e tekrar tıklayınca DeepSeek’in kendi Harness ekranı varsayılan tarayıcında açılır. Önizleme bildirimi çıkarsa **Continue**'a bas. Mesaj alanı henüz görünmüyorsa soldaki **Default workspace** yanında yeni oturum simgesine tıkla. Sonra mesajını yaz.
4. Kapatmak için Atölye'deki **×** düğmesine veya EVREN terminalinde **Ctrl+C**'ye bas. Bu geçici sohbetin geçmişi kapandıktan sonra saklanmaz.

Atölye [resmî dsh CLI paketinin 0.2.2-rc.5 sürümünü](https://github.com/deepseek-ai/deepseek-harness/tree/master/apps/cli) yerel `web` profiliyle açar; üçüncü taraf arayüzü yoktur. Bu sürümün resmî etkileşimli ekranı tarayıcıdadır. DeepSeek [yerleşik terminal arayüzünü kaldırdı](https://github.com/deepseek-ai/deepseek-harness/blob/master/.agents/notes/archived/simplification/2026-08-04-remove-tui-package.md).

İki EVREN profili de şu anda **metin içindir**. Yalnız **DeepSeek V4.1 Flash**'a bağlanır; proje dosyalarını düzenlemez, web ve ajan araçlarına model isteği göndermez. Başka modele sessizce geçmez. Sohbet metni EVREN'e gider. Anahtar yalnız doğrulanmış EVREN HTTPS adresine gönderilir; Harness'a veya tarayıcıya gerçek anahtar verilmez. Resmî arayüz yalnız bu bilgisayarda açılır; oturum bağlantısını paylaşma.

## Cache

EVREN aynı içerik tekrarlandığında sağlayıcı tarafı cache isabeti bildirebilir. Her istekte isabet garantisi yoktur. Cache, sohbetin geçmişini hatırlamasından farklıdır. Ubuntu’da resmî Harness ekranından aynı oturumda iki canlı mesaj tamamlandı. Web testinde ikinci istekte EVREN 320 cache okuma token’ı bildirdi. Ayrı CLI testinde aynı SDK sürecinde iki mesaj tamamlandı; ikinci tur 1.152 cache okuma token’ı gösterdi.

| Ekrandaki durum | Sonraki adım |
|---|---|
| Anahtar eksik veya okunamadı | **EVREN anahtarı** ekranını aç. [Ayar dosyası sorunları](sss.md#anahtar-kaydedilemiyor-ne-yapmalıyım). |
| dsh bulunamadı veya sürüm farklı | **dsh’yi kur** ve sonra **DSH Web**'e yeniden tıkla. |
| Varsayılan tarayıcı açılmadı | Sistemindeki varsayılan tarayıcıyı kontrol et; oturumu kapatıp **DSH Web**'e tekrar tıkla. |
| 401 / 403 | Anahtarın ve model erişimin EVREN hesabında açık mı kontrol et. |
| 429 / istek sınırı | Biraz bekle ve aynı mesajı tekrar gönder. |
