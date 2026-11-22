# Ajan Atölyesi'ne katkı

1. GitHub erişimin varsa bir dal aç. Private fork hesabında izinliyse kendi fork'undan da çalışabilirsin.
2. Değişikliği küçük tut ve `python3 -B -m unittest discover -s tests` çalıştır. Ubuntu grafik oturumunda `./bin/ajan-pencere --check-ui` ile pencereyi kontrol et.
3. PR aç, neyi değiştirdiğini ve hangi testleri çalıştırdığını yaz. PR açılınca Ubuntu CI; birim testlerini, Bash sözdizimini ve gömülü terminali kontrol eder. Kontroller yeşil olsa da insan incelemesi gerekir.

Gerçek anahtar, `.env`, oturum verisi veya müşteri kodu paylaşma. Testler sahte anahtar kullanır. Varsayılan tasarım: solda oturumlar, sağda sadece terminal.
