# DBSCAN Kümeleme Analizi Sonuçları

## Kullanılan Yöntem

Bu projede deprem verilerinin mekânsal yoğunluklarını belirlemek amacıyla DBSCAN kümeleme algoritması kullanılmıştır.

Analizde büyüklüğü 4.0 ve üzerindeki depremler değerlendirilmiştir.

## Model Parametreleri

- Algoritma: DBSCAN
- Komşuluk yarıçapı: 15 km
- Minimum örnek sayısı: 15
- Mesafe yöntemi: Haversine

## Analiz Sonuçları

- Analiz edilen deprem sayısı: 4.217
- Tespit edilen deprem bölgesi sayısı: 32
- Gürültü olarak sınıflandırılan deprem sayısı: 1.458
- Kümelere dahil edilen deprem sayısı: 2.759

## Değerlendirme

DBSCAN algoritması sonucunda deprem kayıtlarının yoğunlaştığı 32 bölge belirlenmiştir.

Analiz edilen 4.217 deprem kaydından 2.759'u kümelere dahil edilirken 1.458'i gürültü olarak sınıflandırılmıştır.

Bu sonuçlar, incelenen veri kümesindeki deprem yoğunluklarının mekânsal dağılımını göstermektedir. Tek başına gelecekteki depremleri veya sigorta riskini tahmin etmez.

## Görselleştirme

DBSCAN kümeleme sonuçlarının haritası bu klasörde bulunmaktadır.
