# Windows kurulumu

Windows'ta uygulama **Ubuntu 24.04, WSL 2 ve WSLg** ile açılır. Yerel Windows `.exe` dosyası değildir. Windows 11 veya Windows 10 derleme 19044 ve üzeri gerekir. Gerçek Windows açılışı henüz test edilmedi. [Microsoft WSLg kılavuzu](https://learn.microsoft.com/windows/wsl/tutorials/gui-apps)

1. Yönetici PowerShell'de `wsl --install -d Ubuntu-24.04` çalıştır. Gerekirse yeniden başlat. Ubuntu'yu bir kez açıp Linux kullanıcı hesabını oluştur. Mevcut kurulumda `wsl -l -v` ile dağıtımın adının `Ubuntu-24.04`, sürümünün **2** olduğunu doğrula. WSLg görünmüyorsa Microsoft kılavuzundaki `wsl --update` adımını izle.
2. Ubuntu terminalinde bağımlılıkları kur:

   ```bash
   sudo apt update
   sudo apt install python3-gi gir1.2-gtk-3.0 gir1.2-vte-2.91 tmux
   ```

3. [Kaynak ZIP'ini indir](https://github.com/OrcunSamiTandogan/ajan-atolyesi/archive/refs/heads/master.zip), Windows'ta yerel bir klasöre çıkar ve **kur-windows.cmd** dosyasını aç. Kurulum başarılıysa aynı komut pencereyi açmayı dener. Arkada açık duran komut penceresini kullanırken kapatma.
4. Sonraki açılışlarda çıkardığın klasördeki **ac-windows.cmd** dosyasını kullan. Windows Başlat menüsünde bir girişin görünmesi gerekmez.

Windows komutu çalışmazsa Ubuntu terminalinden dene:

```bash
"${XDG_DATA_HOME:-$HOME/.local/share}/ajan-atolyesi/ac"
```

Claude, Codex, Pi ve DSH kullanacaksan **Ubuntu içine** kur; Windows'taki ayrı kurulumları uygulama otomatik kullanmaz. Çalışma projelerini mümkünse Ubuntu'nun ev dizininde tut.

**Sonraki adım:** [NVIDIA veya EVREN ile ilk oturum](../README.md#2-nvidia-veya-evren-ile-ilk-oturumu-aç) · [Sorun giderme](sss.md)
