# İlk görev: Türkçe slug

Aşağıdaki metni **Pi sohbetine** ver; API anahtarını buraya yazma.

ZIP kullanıyorsan önce proje klasöründe `cp demo/slug.py demo/slug.once.py` çalıştır. Bu, değişiklikten önceki kopyayı saklar. Git klonu kullandıysan bu adıma gerek yok.

> Yalnızca `demo/slug.py` ve gerekirse `demo/test_slug.py` üzerinde çalış. `slugify`, Türkçe harfleri ASCII'ye çevirsin, sözcükleri tek tireyle ayırsın ve uçlardaki tireleri silsin. Örnek: `İstanbul, Çağrı ve Işık!` → `istanbul-cagri-ve-isik`. Hazır testi silme veya gevşetme. `python3 -B -m unittest discover -s demo` komutunu çalıştır. İlk kez kodlama ajanı kullanan birine Türkçe cevap ver. En fazla üç satır yaz: **Ne değişti?**, **Test geçti mi?**, **Şimdi ne yapayım?** Son satırda değişikliği görmek için Git klonunda `git diff -- demo`, ZIP’te `diff -u demo/slug.once.py demo/slug.py` komutunu ver. Test başarısızsa geçmiş gibi yazma. Yeni paket kurma, repo dışına yazma ve push yapma.

Başlangıçta ASCII testi geçer, Türkçe test bilerek kalır. Görev bitince ikisi de geçmeli. Ajan değiştirmeden sonucu görmek için aynı test komutunu elle çalıştırabilirsin.
