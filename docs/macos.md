# macOS kurulumu

Bu kaynak kurucusu aynı GTK uygulamasını Mac'inde `.app` olarak oluşturur. Hazır, imzalı veya Apple tarafından notarize edilmiş bir indirilebilir uygulama değildir. Gerçek Mac/Finder açılışı henüz test edilmedi; öncelikli hedef Apple Silicon ve Homebrew.

1. [Homebrew](https://brew.sh/) kur ve kendi kurulum çıktısındaki PATH adımını tamamla.
2. Terminalde bağımlılıkları kur:

   ```bash
   brew install gtk+3 vte3 pygobject3 tmux
   ```

3. [Kaynak ZIP'ini indir](https://github.com/OrcunSamiTandogan/ajan-atolyesi/archive/refs/heads/master.zip), çıkar ve çıkan klasörde `bash kur-macos.sh` çalıştır.
4. Finder'da **Git → Klasöre Git** (⇧⌘G), `~/Applications` yaz, **Ajan Atölyesi**'ni aç. Bu klasör sistemin `/Applications` klasörü değil. Terminal karşılığı: `open "$HOME/Applications/Ajan Atölyesi.app"`.

Açılmazsa aşağıdaki ilk komut paketleri ve uygun Homebrew Python'u pencere açmadan kontrol eder. İkinci komut pencere ve gömülü terminali grafik oturumunda kontrol eder.

```bash
"$HOME/Applications/Ajan Atölyesi.app/Contents/MacOS/ajan-atolyesi" --check-deps
"$HOME/Applications/Ajan Atölyesi.app/Contents/MacOS/ajan-atolyesi" --check-terminal
```

Pi veya EVREN DSH için uygulamanın **Terminal** satırında `node -v` ve `npm -v` çalıştır. Uygulama kabuk başlangıç dosyalarını okumaz; yalnız shell oturumunda etkinleşen nvm/fnm gibi bir kurulum Finder'dan görünmeyebilir. Desteklenen sürümler ve elle kurulum için [Sorun giderme](sss.md). Claude ve Codex'i kullanacaksan ayrıca kendi resmî kurulumlarını ve hesabını hazırla.

Apple bir güvenlik uyarısı gösterirse kaynağı doğrula ve [Apple'ın uyarı açıklamasına](https://support.apple.com/en-us/102445) bak; Gatekeeper'ı kapatma. Homebrew paketleri: [VTE](https://formulae.brew.sh/formula/vte3), [PyGObject](https://formulae.brew.sh/formula/pygobject3).

**Sonraki adım:** [NVIDIA veya EVREN ile ilk oturum](../README.md#2-nvidia-veya-evren-ile-ilk-oturumu-aç) · [Sorun giderme](sss.md)
