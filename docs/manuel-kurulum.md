# Ajan Atölyesi olmadan: tmux, Pi ve dsh

Masaüstü uygulamasını kurman gerekmez. Bu rehberi Ubuntu, macOS veya Windows'ta **WSL 2 içindeki Ubuntu** terminalinden izle.

## 1. İki terminal aç

Ubuntu'da `sudo apt install tmux`, Mac'te [Homebrew](https://brew.sh/) kuruluysa `brew install tmux` çalıştır.

```bash
tmux new-session -A -s aa-manuel
```

`Ctrl+b` tuşlarına basıp bırak, sonra `c` tuşuna bas: ikinci bir terminal sekmesi açılır. `Ctrl+b`, sonra `n` ile iki sekme arasında geç. `Ctrl+b`, sonra `d` oturumu kapatmadan ayırır. Geri dönmek için tekrar yukarıdaki komutu çalıştır. [tmux kılavuzu](https://github.com/tmux/tmux/wiki/Getting-Started)

## 2. İlk sekme: Pi ve NVIDIA

1. [Pi'yi resmî kılavuzdan kur](https://docs.pi.dev/latest/quickstart). `pi --version` ile kontrol et.
2. `pi` aç. Pi içinde **/login → NVIDIA NIM** seç ve NVIDIA anahtarını yalnızca Pi'nin anahtar ekranına gir. Sonra **/model** ile modeli seç. Anahtar sohbet girdisi değildir.
3. [Kimi K3.1 Pro](https://build.nvidia.com/moonshotai/kimi-k3_1-pro) listede yoksa Pi'nin [model ayarına](https://docs.pi.dev/latest/models-configuration) NVIDIA sağlayıcısı altında `moonshotai/kimi-k3.1-pro` ekle. Mevcut ayar dosyanı silme. Bu repodaki test, modelin Pi'de seçildiğini gördü ancak canlı Kimi yanıtı zaman aşımına uğradı. Denenmiş alternatif: **Nemotron 3.5 Lightning**.

Anahtarı kalıcı kaydetmek istemiyorsan Bash'te bu alternatif, yalnız Pi çalışırken geçerlidir:

```bash
(
  read -rs -p 'NVIDIA anahtarı: ' NVIDIA_API_KEY
  printf '\n'
  export NVIDIA_API_KEY
  pi --models 'nvidia/*'
)
```

## 3. İkinci sekme: dsh

`node -v` çalıştır. Burada denenen dsh sürümü Node **24.9 veya üstünü** gerektirir. Daha eskiyse Node'u [resmî siteden](https://nodejs.org/) güncelle.

```bash
npm install -g @deepseek-ai/dsh@0.2.2-rc.5
dsh --version
dsh --profile headless --help
```

`npm` yazma izni hatası verirse `sudo npm` kullanma; Node'u kendi hesabına kurduğundan emin ol. [Resmî dsh CLI](https://github.com/deepseek-ai/deepseek-harness/tree/master/apps/cli)

dsh'nin **kendi sağlayıcısı** olan DeepSeek'e giriş için DeepSeek anahtarı gerekir. Sadece ayrı bir deneme yapmak istiyorsan, normal izinlerle ve boş bir dizinde:

```bash
(
  cd "$(mktemp -d)" || exit 1
  read -rs -p 'DeepSeek anahtarı (EVREN değil): ' DEEPSEEK_API_KEY
  printf '\n'
  export DEEPSEEK_API_KEY
  dsh --profile headless "Sadece merhaba yaz."
)
```

Bu istek **DeepSeek hesabının** ücret ve kullanım sınırlarına tabidir. EVREN'e gitmez.

### EVREN anahtarını dsh'yi açmadan doğrula

[ZIP'ten](https://github.com/OrcunSamiTandogan/ajan-atolyesi/archive/refs/heads/master.zip) çıkardığın klasörde:

```bash
python3 bin/evren-baglanti-kontrol
```

EVREN anahtarını görünmeyen alana gir. Komut yalnız EVREN'deki model listesini okur ve **DeepSeek V4.1 Flash** listede mi söyler. Model çağırmaz ve anahtarı kaydetmez. **EVREN anahtarını `DEEPSEEK_API_KEY` olarak dsh'ye verme.** Atölye'de **EVREN · DSH CLI** tmux içindeki resmî Harness SDK oturumunu, **EVREN · DSH Web** resmî tarayıcı arayüzünü açar. Rehber: [EVREN · DeepSeek Harness](evren-dsh.md). [Durum ve teknik not](evren-dsh.md)

Gerçek anahtarları prompt'a, komut satırına, ekran görüntüsüne veya Git'e koyma.
