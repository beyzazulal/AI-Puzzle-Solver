# AI-Puzzle-Solver


<img width="695" height="841" alt="Ekran görüntüsü 2026-04-22 150607" src="https://github.com/user-attachments/assets/a9a52234-11fb-4405-8293-7c7dec460de6" />


# 🧩 8-Puzzle Solver: AI-Based Heuristic Search Analysis

Bu proje, yapay zekanın temel taşlarından olan **"Arama Algoritmaları"** üzerine odaklanmış kapsamlı bir çalışmadır. Klasik 8-Puzzle problemini temel alarak; maliyet, zaman ve bellek kullanımı gibi metrikler üzerinden farklı AI stratejilerinin performans analizini gerçekleştirir.

## 🧠 Uygulanan Algoritma Mimarisi

Proje, hem kör (uninformed) hem de bilgiye dayalı (informed) arama tekniklerini içermektedir:

### 1. Uninformed Search (Bilgisiz Arama)
* **Breadth-First Search (BFS):** Hedef duruma giden en kısa yolu garanti eder. Geniş bir arama uzayını taradığı için bellek kullanımı yüksektir.
* **Depth-First Search (DFS):** Daha az bellek tüketir ancak çözümün optimal olmasını garanti etmez; derin döngülere girebilir.
* **Iterative Deepening Search (IDS):** DFS'nin bellek verimliliği ile BFS'nin optimalliğini birleştirerek katmanlı bir arama yapar.

### 2. Informed Search (Bilgili Arama)
* **A* Search Algorithm:** Projenin en güçlü kısmıdır. Mevcut maliyet ($g(n)$) ile hedefe olan tahmini uzaklığı ($h(n)$) toplayarak en düşük toplam maliyetli düğümü seçer.


## 🔬 Sezgisel Fonksiyon (Heuristic) Karşılaştırması

$A^*$ algoritmasının verimliliği kullanılan sezgisel yönteme bağlıdır. Projede iki ana yöntem test edilmiştir:

1.  **Manhattan Distance:** Her bir karonun olması gereken yere olan yatay ve dikey uzaklıklarının toplamı.
2.  **Misplaced Tiles:** Sadece yanlış yerde duran karoların sayısını temel alır.

> **Analiz Sonucu:** Manhattan Distance, daha "bilgili" bir sezgisel yöntem olduğu için çözüm yolunda çok daha az düğüm genişleterek $A^*$ algoritmasının en hızlı şekilde sonuç vermesini sağlamıştır.

---

## 🛠 Öne Çıkan Teknik Özellikler

* **Esnek Izgara Desteği:** 3x3 (8-Puzzle), 5x5 (24-Puzzle) ve 7x7 boyutlarındaki karmaşık bulmacaları destekleyen dinamik altyapı.
* **Çoklu Veri Girişi:**
    * **Manuel Tasarım:** Kullanıcı arayüz üzerinden tıklayarak kendi bulmacasını oluşturabilir.
    * **Dosyadan Yükleme:** `.txt` formatındaki önceden tanımlanmış matris verilerini sisteme aktarabilme.
    * **Randomize:** Rastgele başlangıç durumları üreterek algoritma dayanıklılığını test etme.
* **Görsel Simülasyon:** Çözüm bulunduktan sonra hamlelerin adım adım izlenebildiği interaktif GUI.
* **Performans Analiz Paneli:** Genişletilen düğüm sayısı, geçen süre ve hamle derinliği gibi verilerin gerçek zamanlı gösterimi.



---

## 💻 Kurulum ve Kullanım

### Gereksinimler
- Python 3.11+
- Tkinter (Arayüz için)

### Çalıştırma
1. Proje dizininde PowerShell veya Terminal açın.
2. Ana uygulamayı başlatın:
   ```bash
   python solver_gui.py
   ```
3. Arayüzden istediğiniz bulmaca boyutunu ve algoritmayı seçip "Solve" butonuna tıklayın.

## 📊 Örnek Veri Formatı
Proje, `.txt` dosyalarından şu formatta veri okuyabilmektedir:
```text
7 2 1
3 6 8
5 4 0 
```
*(Not: '0' rakamı boş karoyu temsil eder.)*

