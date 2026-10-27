"""
=============================================================
  Socket Communication System - CLIENT
  Arsitektur  : TCP Client dengan loop penerimaan pesan
  Modul       : socket, threading
=============================================================
"""

import socket
import threading
import sys

# ─── Konfigurasi ────────────────────────────────────────────
SERVER_HOST = "127.0.0.1"  # Ganti dengan IP server jika berbeda mesin
SERVER_PORT  = 55555


# ─── Loop Penerimaan Pesan ──────────────────────────────────
def receive_messages(client_socket: socket.socket) -> None:
    """Terus-menerus menerima dan menampilkan pesan dari server.

    Loop ini TIDAK berhenti selama koneksi aktif; hanya keluar
    jika koneksi terputus atau terjadi error fatal.

    Args:
        client_socket: Socket yang sudah terhubung ke server.
    """
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                # Server menutup koneksi
                print("\n[INFO] Koneksi ditutup oleh server.")
                break

            message = data.decode("utf-8")
            # Tampilkan pesan dan cetak ulang prompt agar tidak terganggu
            print(f"\n{message}")
            print("Anda: ", end="", flush=True)

        except (ConnectionResetError, OSError):
            print("\n[INFO] Koneksi ke server terputus.")
            break

    # Sinyal ke thread utama bahwa koneksi sudah mati
    client_socket.close()
    sys.exit(0)


# ─── Loop Pengiriman Pesan ──────────────────────────────────
def send_messages(client_socket: socket.socket) -> None:
    """Baca input dari pengguna dan kirimkan ke server.

    Loop ini TIDAK berhenti selama koneksi aktif; hanya keluar
    jika pengguna mengetik 'exit' atau koneksi terputus.

    Args:
        client_socket: Socket yang sudah terhubung ke server.
    """
    while True:
        try:
            msg = input("Anda: ")
        except (EOFError, KeyboardInterrupt):
            print("\n[INFO] Sesi diakhiri oleh pengguna.")
            break

        if msg.strip().lower() == "exit":
            print("[INFO] Memutuskan koneksi dari server...")
            break

        if not msg.strip():
            continue  # Abaikan input kosong

        try:
            client_socket.sendall(msg.encode("utf-8"))
        except OSError:
            print("[ERROR] Gagal mengirim pesan. Koneksi terputus.")
            break

    client_socket.close()
    sys.exit(0)


# ─── Fungsi Utama ────────────────────────────────────────────
def main() -> None:
    print("=" * 50)
    print("  Socket Communication System - CLIENT")
    print("=" * 50)

    # Buat socket TCP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        print(f"[+] Berhasil terhubung ke server {SERVER_HOST}:{SERVER_PORT}")
    except ConnectionRefusedError:
        print(f"[ERROR] Tidak bisa terhubung ke {SERVER_HOST}:{SERVER_PORT}. Pastikan server aktif.")
        return
    except OSError as e:
        print(f"[ERROR] {e}")
        return

    # ── Thread penerimaan: berjalan paralel, tidak menghalangi input ──
    recv_thread = threading.Thread(
        target=receive_messages,
        args=(client_socket,),
        daemon=True,  # Ikut mati ketika thread utama selesai
    )
    recv_thread.start()

    # ── Loop pengiriman berjalan di thread utama ──
    send_messages(client_socket)


if __name__ == "__main__":
    main()
