# Kualiti Udara Taiping

Halaman awam yang memaparkan bacaan Indeks Pencemar Udara (IPU) bagi stesen
pemantauan **CA10A, Taiping, Perak**, bersama ramalan cuaca MET Malaysia dan
bandingan dengan stesen-stesen lain di Perak.

Halaman: https://aizuddin13.github.io/IPU-Taiping/

## Kandungan

| Fail | Keterangan |
| --- | --- |
| `index.html` | Halaman itu sendiri. Tiada kebergantungan luar — semua carta dilukis sendiri sebagai SVG. |
| `data/ipu.json` | Bacaan IPU sejam bagi Taiping, tetingkap bergolek tujuh hari (168 bacaan). |
| `data/perak.json` | Bacaan semasa kelima-lima stesen di Perak. |
| `data/cuaca.json` | Ramalan cuaca tujuh hari bagi pekan Taiping. |

## Kemas kini

Fail data dalam `data/` ditulis semula setiap jam oleh satu tugas berjadual
dan ditolak ke repositori ini. GitHub Pages menerbitkan semula halaman itu
secara automatik selepas setiap commit, jadi biasanya ia lewat satu hingga dua
minit berbanding portal rasmi.

## Sumber

- Bacaan IPU: Sistem Pengurusan Indeks Pencemar Udara (APIMS), Jabatan Alam
  Sekitar — https://eqms.doe.gov.my/APIMS/main
- Ramalan cuaca: MET Malaysia, melalui portal data terbuka kerajaan
  (`api.data.gov.my/weather/forecast`)

Kedua-duanya data awam kerajaan Malaysia. Halaman ini bukan terbitan rasmi
mana-mana agensi. Untuk keputusan kesihatan yang penting, rujuk portal APIMS
atau nasihat Kementerian Kesihatan.
