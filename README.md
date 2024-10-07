
# diziwatch-indirici

diziwatch.net icin yt-dlp ve selenium kutuphanelerini kullanan basit bir script




## Özellikler

- İndirmek için bölüm seçebilme , çoklu/bütün bölümleri seçebilme
- Jellyfin,Plex gibi medya paketleri için bölüm adı uyumluluğu
- İndirilecek klasörü seçebilme , varsayılan klasör atama



## Gereksinimler 
### Paketlenmiş script için gerek yok

Gerekli kütüphaneler için
```bash
pip install -r requirements.txt
```
Kullanmanız için mutlaka geckodriver kurulu ve PATH'e ekli olmalı  
[Geckodriver](https://github.com/mozilla/geckodriver/releases)

## Kullanım
### Paketlenmiş script için direk exe'yi açabilirsiniz

```bash
python cli.py
```
eğer gereksinimleri yüklediyseniz bir sorun olmadan açılacaktır

## Eklenecekler

- [ ] GUI

- [ ] chrome webdriver'a destek verilmesi

- [ ] Selenium'a bağlılığın azaltılması

- [ ] Tum sezonları indirme seçeneği

- [ ] Kodun commentlenmesi

- [ ] Hata denetimleri ve logging'in geliştirilmesi

- [x] Anime/Dizi arama fonksiyonunun baştan yazılması
 
- [x] Kodun parçalanması ve modülerliğin sağlanması
