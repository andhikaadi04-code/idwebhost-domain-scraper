#!/usr/bin/env python3
"""
IDwebhost Free Domain Scraper
============================
Mencari domain .my.id / .web.id / .biz.id yang TERSEDIA (belum terdaftar)
untuk diklaim lewat promo IDwebhost.

Cara kerja:
- Cek ketersediaan via DNS-over-HTTPS (query NS ke Cloudflare & Google).
  NXDOMAIN dari zona induk = domain belum terdaftar = tersedia.
- Untuk setiap domain yang tersedia, cetak LINK KLAIM LANGSUNG:
  https://order.idwebhost.com/domain/<domain>
  Buka link itu, uncheck upsell (hosting/SSL/backup), masukkan kupon,
  login akun IDwebhost, verifikasi total Rp0, lalu Bayar Sekarang.

Script ini TIDAK membuat order dan TIDAK login — hanya mencari + memberi link.
Klaim tetap dilakukan manual oleh pemilik akun (lebih aman).

Pakai:
    python3 scraper.py                  # pakai candidates.txt
    python3 scraper.py namaku brandku    # nama custom via argumen
    python3 scraper.py --tlds my.id,web.id --out hasil.json
"""

import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request

DOH_ENDPOINTS = [
    "https://cloudflare-dns.com/dns-query",
    "https://dns.google/resolve",
]

DEFAULT_TLDS = ["my.id", "web.id", "biz.id"]
ORDER_BASE = "https://order.idwebhost.com/domain/"
# Kupon mAts2Mey DINYATAKAN EXPIRED per 2026-10-04 ("Kode kupon sudah tidak
# tersedia"). Kabar baik: .my.id saat ini berlabel "Gratis" TANPA kupon.

# Harga promo yang teramati di situs IDwebhost (2026-10-04, bisa berubah):
#   .my.id  -> GRATIS tanpa kupon (harga normal Rp22.000)
#   .web.id -> Rp3.000 (harga normal Rp54.900)
#   .biz.id -> cek di situs


def doh_ns_query(domain, timeout=12):
    """Return 'available' | 'taken' | 'unknown' via DoH NS lookup."""
    params = urllib.parse.urlencode({"name": domain, "type": "NS"})
    last_err = None
    for base in DOH_ENDPOINTS:
        try:
            req = urllib.request.Request(
                f"{base}?{params}",
                headers={
                    "accept": "application/dns-json",
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) idwebhost-domain-scraper/1.0",
                },
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8", "replace"))
            status = data.get("Status")
            answers = data.get("Answer") or []
            # Status 3 = NXDOMAIN -> belum terdaftar
            if status == 3:
                return "available"
            # Status 0 + ada jawaban NS -> terdaftar & terdelegasi
            if status == 0 and any(a.get("type") == 2 for a in answers):
                return "taken"
            # Status 0 tanpa jawaban NS: kemungkinan terdaftar tapi tak
            # terdelegasi — anggap taken agar tidak memberi harapan palsu.
            if status == 0:
                return "taken"
            last_err = f"unexpected Status={status}"
        except Exception as e:  # noqa: BLE001 - coba endpoint berikutnya
            last_err = str(e)[:100]
            continue
    return f"unknown ({last_err})"


def valid_name(name):
    return bool(re.fullmatch(r"[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?", name))


def load_candidates(path):
    names = []
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip().lower()
                if not line or line.startswith("#"):
                    continue
                # boleh "namaku" atau "namaku.my.id" -> ambil bagian nama
                base = line.split(".")[0]
                if valid_name(base) and base not in names:
                    names.append(base)
    except FileNotFoundError:
        pass
    return names


def main():
    ap = argparse.ArgumentParser(description="IDwebhost free domain scraper")
    ap.add_argument("names", nargs="*", help="nama domain custom (tanpa TLD)")
    ap.add_argument("--tlds", default=",".join(DEFAULT_TLDS),
                    help="daftar TLD dipisah koma")
    ap.add_argument("--candidates", default="candidates.txt",
                    help="file daftar nama kandidat")
    ap.add_argument("--delay", type=float, default=0.35,
                    help="jeda antar query (detik)")
    ap.add_argument("--out", default="",
                    help="simpan hasil ke file JSON")
    args = ap.parse_args()

    tlds = [t.strip().lower().lstrip(".") for t in args.tlds.split(",") if t.strip()]
    names = [n.strip().lower().split(".")[0] for n in args.names]
    names = [n for n in names if valid_name(n)]
    if not names:
        names = load_candidates(args.candidates)
    if not names:
        print("Tidak ada nama kandidat. Isi candidates.txt atau beri argumen.")
        sys.exit(1)

    total = len(names) * len(tlds)
    print(f"Mengecek {len(names)} nama x {len(tlds)} TLD = {total} domain...\n")

    results = []
    available = []
    n = 0
    for name in names:
        for tld in tlds:
            n += 1
            domain = f"{name}.{tld}"
            status = doh_ns_query(domain)
            mark = {"available": "✅ TERSEDIA",
                    "taken": "❌ terpakai"}.get(status, f"❓ {status}")
            print(f"[{n}/{total}] {domain:35s} {mark}", flush=True)
            results.append({"domain": domain, "status": status,
                            "claim_url": ORDER_BASE + domain})
            if status == "available":
                available.append(domain)
            time.sleep(args.delay)

    print("\n" + "=" * 60)
    if available:
        print(f"🎉 {len(available)} domain TERSEDIA — klaim manual:\n")
        for d in available:
            print(f"  • {d}\n    {ORDER_BASE + d}\n")
        print("Langkah klaim per domain:")
        print("  1. Buka link di atas (halaman keranjang IDwebhost).")
        print("  2. UNCHECK upsell yang otomatis tercentang: paket hosting,")
        print("     addon SSL Murah, dan Daily Backup.")
        print("  3. Untuk .my.id: TIDAK perlu kupon — sudah berlabel Gratis.")
        print("     (Kupon mAts2Mey sudah expired per 2026-10-04.)")
        print("  4. Login akun IDwebhost (atau buat akun baru).")
        print("  5. Pastikan TOTAL = Rp0, centang persetujuan,")
        print("     lalu klik Bayar Sekarang.")
        print("\nCatatan: harga promo bisa berubah sewaktu-waktu.")
        print("Verifikasi total Rp0 di halaman checkout sebelum bayar.")
    else:
        print("Tidak ada domain tersedia dari daftar ini. Coba nama lain.")

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump({"results": results, "available": available}, f,
                      indent=2, ensure_ascii=False)
        print(f"\nHasil disimpan ke {args.out}")


if __name__ == "__main__":
    main()
