# IDwebhost Free Domain Scraper

Mencari domain **.my.id / .web.id / .biz.id** yang masih tersedia untuk
diklaim lewat promo IDwebhost (script hanya *mencari* — klaim tetap manual
di akun IDwebhost masing-masing).

## Cara pakai

```bash
cd ~/workspace/idwebhost-domain-scraper

# 1) Cek daftar di candidates.txt (default)
python3 scraper.py

# 2) Cek nama sendiri
python3 scraper.py namaku brandku tokoku

# 3) Hanya TLD tertentu + simpan JSON
python3 scraper.py --tlds my.id,web.id --out hasil.json
```

Output: daftar domain **TERSEDIA** + link klaim langsung
`https://order.idwebhost.com/domain/<domain>`.

## Cara klaim (manual, per domain)

1. Buka link klaim dari output script.
2. **Uncheck** upsell yang otomatis tercentang: paket hosting, addon
   *SSL Murah*, dan *Daily Backup*.
3. Untuk **.my.id: TIDAK perlu kupon** — domain sudah berlabel *Gratis*
   di keranjang. (Kupon `mAts2Mey` sudah expired per 2026-10-04:
   *"Kode kupon sudah tidak tersedia."*)
4. Login akun IDwebhost (atau buat akun baru).
5. **Pastikan TOTAL = Rp0**, centang persetujuan, klik *Bayar Sekarang*.

## Info promo (terverifikasi 2026-10-04)

| TLD | Harga promo di situs | Catatan |
|-----|---------------------|---------|
| .my.id | **Gratis, tanpa kupon** (normal Rp22.000) | label "Gratis" langsung di hasil pencarian & keranjang |
| .web.id | Rp3.000 (normal Rp54.900) | kupon sudah expired, tetap Rp3.000 |
| .biz.id | cek di situs | — |

Harga dapat berubah sewaktu-waktu — selalu verifikasi total Rp0
di halaman checkout sebelum menyelesaikan order.

## Cara kerja teknis

- Ketersediaan dicek via **DNS-over-HTTPS** (Cloudflare, fallback Google):
  query NS; `NXDOMAIN` dari zona induk = belum terdaftar.
- IDwebhost sendiri memblokir akses API otomatis dari script
  (request API whois hang/tidak merespons), jadi pengecekan memakai DNS
  publik yang netral.
- Domain yang *terdaftar tapi belum didelegasi* (tanpa NS) diperlakukan
  sebagai "terpakai" agar tidak memberi harapan palsu. Kebenaran final
  tetap di halaman pencarian IDwebhost saat klaim.
