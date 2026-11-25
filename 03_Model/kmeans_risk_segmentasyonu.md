# K-Means ile Sigorta Risk Segmentasyonu

## Kullanılan Yöntem

Projede illerin deprem verilerine göre risk gruplarına ayrılması amacıyla K-Means kümeleme algoritması kullanılmıştır.

## Model Parametreleri

- Algoritma: K-Means
- Küme sayısı: 5
- Segment sayısı: 5

## Risk Skorlarının Belirlenmesi

K-Means algoritması sonucunda iller beş kümeye ayrılmıştır.

Her kümenin ortalama tehlike puanı hesaplanmış ve kümeler bu ortalamaya göre sıralanmıştır.

En yüksek ortalama tehlike puanına sahip kümeye 5, en düşük ortalamaya sahip kümeye 1 risk skoru atanmıştır.

## Risk Segmentleri

- Risk 1: En düşük göreli risk grubu
- Risk 2: Düşük göreli risk grubu
- Risk 3: Orta göreli risk grubu
- Risk 4: Yüksek göreli risk grubu
- Risk 5: En yüksek göreli risk grubu

## Sonuç

Bu segmentasyon sayesinde iller, projede kullanılan deprem göstergeleri açısından karşılaştırılabilir risk gruplarına ayrılmıştır.

Elde edilen sonuçlar sigorta risklerinin ön değerlendirmesinde kullanılabilecek bir analiz sunmaktadır. Ancak gerçek sigorta riskini belirlemek için bina özellikleri, zemin koşulları, güncel deprem tehlike verileri ve diğer faktörlerin de değerlendirilmesi gerekir.

İl bazındaki sonuçlar `il_risk_skorlari.csv` dosyasında bulunmaktadır.
