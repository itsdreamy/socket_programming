# Socket Communication System

Aplikasi komunikasi berbasis **TCP Socket** menggunakan Python — arsitektur **Server–Client** dengan dukungan banyak client secara bersamaan.

---

## Struktur Proyek

```
2/
├── server.py   # Multi-client TCP Server (multithreading)
└── client.py   # TCP Client (loop penerimaan & pengiriman)
```

---

## Cara Menjalankan

### 1 — Jalankan Server
```bash
python server.py
```

### 2 — Jalankan Satu atau Lebih Client (terminal terpisah)
```bash
python client.py
```

> Untuk menguji banyak client, buka beberapa terminal dan jalankan `python client.py` di masing-masing.

---

## Perintah Tersedia

| Konteks | Perintah | Efek |
|---------|----------|------|
| Server  | *(teks apa pun)* | Broadcast ke semua client |
| Server  | `exit` | Tutup server & notifikasi semua client |
| Client  | *(teks apa pun)* | Kirim pesan ke server (diteruskan ke semua client lain) |
| Client  | `exit` | Putuskan koneksi dari server |

---

## Arsitektur

```
┌─────────────────────────────────────────────────────────┐
│                        SERVER                           │
│                                                         │
│  Main Thread: accept() loop (terus-menerus)             │
│  Input Thread: baca stdin → broadcast ke semua client   │
│                                                         │
│  Setiap client baru → Thread worker handle_client()     │
│    └─ recv() loop → broadcast ke client lain            │
└─────────┬──────────────┬──────────────┬─────────────────┘
          │ TCP          │ TCP          │ TCP
    ┌─────┴──────┐ ┌─────┴──────┐ ┌────┴───────┐
    │  CLIENT 1  │ │  CLIENT 2  │ │  CLIENT N  │
    │            │ │            │ │            │
    │ recv_thread│ │ recv_thread│ │ recv_thread│
    │ (daemon)   │ │ (daemon)   │ │ (daemon)   │
    │            │ │            │ │            │
    │ send loop  │ │ send loop  │ │ send loop  │
    │ (main thrd)│ │ (main thrd)│ │ (main thrd)│
    └────────────┘ └────────────┘ └────────────┘
```
