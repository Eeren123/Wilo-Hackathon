# Akış Lab — Hackathon Konsept Tasarımı

Veri merkezlerinde soğutma suyu ve pompa verimliliğini anlatan, etkileşimli senaryo alanı içeren Türkçe Streamlit sunum prototipi.

## Çalıştırma

Python 3.10+ gerekir. Gerekli paketler `requirements.txt` içinde listelenmiştir.

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Varsayılan adres `http://localhost:8501` olur. Proje ortamında `npm run dev` de Streamlit uygulamasını başlatır.

## Deneyim

- Açılış alanı, veri merkezi soğutmasındaki su ve operasyon problemlerini kısa biçimde anlatır.
- Dört adımlı akış veri toplamadan etki ölçümüne kadar konsepti açıklar.
- Senaryo laboratuvarındaki yük, pompa debisi/hızı ve giriş sıcaklığı ayarları grafik, metrikler, anomali sinyali ve WUE tahminini günceller.
- Kaynaklar, ayrıntılı veri tablosu yerine kısa keşif kartları olarak sunulur.

## Simülasyon sınırları

`app.py` içindeki `simulate` fonksiyonu açık formüllü bir demo optimizasyon yaklaşımıdır. Bu model saha verisine dayalı yapay zekâ, fizik tabanlı tesis modeli veya güvenlik sertifikalı kontrol sistemi değildir. Ekrandaki sayılar temsili simülasyondur; gerçek ölçüm veya gerçekleşmiş tasarruf anlamına gelmez.

WUE = yıllık veri merkezi su tüketimi (L) / BT ekipmanlarının yıllık enerji tüketimi (kWh). WUE değerindeki düşüş, birim BT enerjisi başına daha az su kullanımını gösterir. Gerçek hesap doğrudan ölçülmüş su ve BT enerji verisi gerektirir.

## Araştırma kaynakları

- [Frontier Supercomputer 2023 Cooling Dataset](https://figshare.com/articles/dataset/Dataset_of_Frontier_supercomputer/24391240/4?file=47812750) — Frontier sisteminin soğutma/çalışma koşulları. Takviye suyu veya buharlaşmayı doğrudan ölçtüğü iddia edilmez.
- [Water Sustainability Dataset](https://osf.io/g3zvd/) — OSF su sürdürülebilirliği veri seti; entegrasyon öncesi özgün kapsamı incelenmelidir.
- [NREL Data Center Cooling Dataset](https://github.com/M-D-Murphy/Data-Centre-Waste-Heat) — NREL ESIF HPC merkezinin hibrit hava/sıvı soğutmasından 12 aylık dakikalık sıcaklık ve soğutma gücü verileri; doğrudan su tüketimi ölçümü değildir.
