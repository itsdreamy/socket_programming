"""
=============================================================
  Socket Communication System - SERVER
  Arsitektur  : Multi-client TCP Server dengan Multithreading
  Modul       : socket, threading
=============================================================
"""

import socket
import threading

# ─── Konfigurasi ────────────────────────────────────────────
HOST = "0.0.0.0"   # Dengarkan semua interface jaringan
PORT = 55555        # Port yang digunakan server

# ─── State Global ───────────────────────────────────────────
clients: list[socket.socket] = []   # Daftar socket client aktif
clients_lock = threading.Lock()      # Lock untuk akses thread-safe ke list clients


# ─── Fungsi Broadcast ───────────────────────────────────────
def broadcast(message: str, sender: socket.socket | None = None) -> None:
    """Kirim pesan ke semua client yang terhubung.

    Args:
        message: Teks pesan yang akan dikirim.
        sender : Socket pengirim (opsional). Jika diisi, pesan TIDAK
                 dikembalikan ke pengirim itu sendiri.
    """
    disconnected: list[socket.socket] = []

    with clients_lock:
        targets = list(clients)  # Salin agar lock tidak terlalu lama

    for client in targets:
        if client is sender:
            continue  # Lewati si pengirim
        try:
            client.sendall(message.encode("utf-8"))
        except (BrokenPipeError, ConnectionResetError, OSError):
            # Client sudah putus; tandai untuk dihapus
            disconnected.append(client)

    # Hapus client yang sudah putus koneksi
    if disconnected:
        with clients_lock:
            for c in disconnected:
                if c in clients:
                    clients.remove(c)


# ─── Handler per-Client ─────────────────────────────────────
def handle_client(client_socket: socket.socket, addr: tuple) -> None:
    """Thread worker: mengelola komunikasi satu client.

    Thread ini terus menerima pesan dari client hingga koneksi
    terputus (loop tidak berhenti sendiri selama client aktif).

    Args:
        client_socket : Socket untuk berkomunikasi dengan client.
        addr          : Tuple (ip, port) alamat client.
    """
    print(f"[+] Client terhubung: {addr[0]}:{addr[1]}")

    # Sambut client baru
    welcome = f"[SERVER] Selamat datang! Anda terhubung dari {addr[0]}:{addr[1]}"
    try:
        client_socket.sendall(welcome.encode("utf-8"))
    except OSError:
        pass

    # Beritahu semua client lain tentang client baru
    broadcast(f"[SERVER] Client baru bergabung: {addr[0]}:{addr[1]}")

    # ── Loop penerimaan pesan (tidak berhenti selama client aktif) ──
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                # Client menutup koneksi dengan graceful
                break

            message = data.decode("utf-8").strip()
            print(f"[{addr[0]}:{addr[1]}] {message}")

            # Broadcast pesan ke semua client lain
            broadcast(f"[{addr[0]}:{addr[1]}] {message}", sender=client_socket)

        except (ConnectionResetError, OSError):
            # Koneksi terputus secara paksa
            break

    # ── Bersihkan setelah client terputus ──
    with clients_lock:
        if client_socket in clients:
            clients.remove(client_socket)

    try:
        client_socket.close()
    except OSError:
        pass

    print(f"[-] Client terputus: {addr[0]}:{addr[1]}")
    broadcast(f"[SERVER] Client {addr[0]}:{addr[1]} telah meninggalkan obrolan.")


# ─── Thread Broadcast Manual dari Server ────────────────────
def server_input_loop(server_socket: socket.socket) -> None:
    """Baca input dari konsol server dan broadcast ke semua client.

    Thread ini berjalan terus (loop tidak berhenti) agar admin
    server dapat mengirim pesan kapan saja.

    Args:
        server_socket: Digunakan untuk menutup server saat admin
                       mengetik 'exit'.
    """
    print("[INFO] Ketik pesan untuk broadcast ke semua client. Ketik 'exit' untuk menutup server.\n")
    while True:
        try:
            msg = input()
        except EOFError:
            break

        if msg.strip().lower() == "exit":
            print("[SERVER] Menutup server...")
            broadcast("[SERVER] Server akan segera ditutup. Selamat tinggal!")
            server_socket.close()
            break

        if msg.strip():
            broadcast(f"[BROADCAST SERVER] {msg.strip()}")


# ─── Fungsi Utama ────────────────────────────────────────────
def main() -> None:
    # Buat socket TCP
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_socket.bind((HOST, PORT))
    except OSError as e:
        print(f"[ERROR] Tidak bisa bind ke {HOST}:{PORT} → {e}")
        return

    server_socket.listen()
    print(f"[SERVER] Mendengarkan di {HOST}:{PORT} ...")
    print("=" * 50)

    # Thread untuk menerima input broadcast dari server
    input_thread = threading.Thread(
        target=server_input_loop,
        args=(server_socket,),
        daemon=True,  # Ikut mati ketika main thread selesai
    )
    input_thread.start()

    # ── Loop penerimaan koneksi (terus menerus, tidak berhenti) ──
    while True:
        try:
            client_socket, addr = server_socket.accept()
        except OSError:
            # Server socket ditutup (misal dari thread input_loop)
            break

        # Daftarkan client baru secara thread-safe
        with clients_lock:
            clients.append(client_socket)

        # Buat thread baru untuk menangani client ini
        client_thread = threading.Thread(
            target=handle_client,
            args=(client_socket, addr),
            daemon=True,
        )
        client_thread.start()

        with clients_lock:
            jumlah = len(clients)
        print(f"[INFO] Jumlah client aktif: {jumlah}")

    print("[SERVER] Server telah berhenti.")


if __name__ == "__main__":
    main()
