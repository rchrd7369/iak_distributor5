# Aplikasi Terpadu Perusahaan - Modul Distributor

Ini adalah **Modul Distributor** dari aplikasi terpadu perusahaan, yang dibangun menggunakan **Flask** dan **Firebase Firestore** untuk mengelola operasi terkait distributor, seperti pelacakan pesanan, estimasi biaya pengiriman, dan pembaruan status pesanan. Aplikasi ini mencakup fitur-fitur utama seperti manajemen pesanan distributor, konfirmasi pengiriman, dan pelacakan status pengiriman menggunakan nomor resi.

## Daftar Isi

- [Gambaran Proyek](#gambaran-proyek)
- [Fitur](#fitur)
- [Teknologi yang Digunakan](#teknologi-yang-digunakan)
- [Instruksi Instalasi](#instruksi-instalasi)
- [Penggunaan](#penggunaan)
- [Berkontribusi](#berkontribusi)
- [Lisensi](#lisensi)

## Gambaran Proyek

Modul Distributor ini memungkinkan pengguna untuk:
- Mengelola distributor, menambah atau mengonfirmasi pesanan.
- Menghitung biaya pengiriman berdasarkan kota asal dan tujuan serta berat paket.
- Melacak pengiriman dengan memasukkan nomor resi.
- Memperbarui dan mengelola status pengiriman melalui antarmuka admin.

## Fitur

- **Sistem Login**: Mengautentikasi pengguna sebelum memberikan akses ke antarmuka admin.
- **Manajemen Pesanan**: Admin dapat menambah, mengedit, mengonfirmasi, dan menghapus pesanan distributor.
- **Perhitungan Biaya Pengiriman**: Menghitung biaya pengiriman secara otomatis berdasarkan kota asal, tujuan, dan berat.
- **Basis Data Real-time**: Terintegrasi dengan **Firebase Firestore** untuk menyimpan dan mengambil data pesanan distributor dan data pengiriman.
- **Pelacakan Pesanan**: Pengguna dapat memeriksa status pesanan mereka menggunakan nomor resi.
- **Pembaruan Status Pengiriman**: Admin dapat memperbarui status pengiriman dan memindahkan pesanan yang telah selesai ke histori.

## Teknologi yang Digunakan

- **Python**: Pengembangan backend.
- **Flask**: Framework web ringan untuk membangun aplikasi.
- **Firebase**: Firestore digunakan untuk menyimpan dan mengelola data distributor.
- **HTML/CSS**: Untuk menyusun dan merancang antarmuka web.
- **JavaScript**: Menambahkan interaktivitas untuk fungsionalitas seperti tampilan password dan penanganan form.

## Instruksi Instalasi

Untuk menginstal proyek ini secara lokal, ikuti langkah-langkah berikut:

### 1. Clone Repositori

```bash
git clone https://github.com/username/modul-distributor.git
cd modul-distributor
```

### 2. Membuat Lingkungan Virtual (Disarankan)

```bash
python -m venv env
source env/bin/activate  # Pada Windows gunakan `env\Scripts\activate`
```

### 3. Install Dependensi

```bash
pip install -r requirements.txt
```

### 4. Siapkan Firebase

- Buat proyek Firebase dan atur Firestore.
- Unduh kunci akun layanan (service account key) dari Firebase dan simpan di direktori root dengan nama file `ladju_distributor.json`.
  
### 5. Jalankan Aplikasi

```bash
python app.py
```

Aplikasi sekarang akan berjalan di `http://localhost:5000`.

## Penggunaan

Setelah aplikasi berjalan, berikut adalah cara penggunaannya:

### Fitur Pengguna

1. **Login**: Pengguna harus login melalui `/login`. Kredensial akan divalidasi menggunakan data yang disimpan di Firebase.
2. **Pelacakan Pesanan**: Pengguna dapat memeriksa status pesanan menggunakan nomor resi di halaman utama.

### Fitur Admin

1. **Dashboard Admin**: Setelah login, pengguna dapat mengakses antarmuka admin di mana mereka dapat:
   - Melihat semua pesanan distributor.
   - Mengonfirmasi pesanan dengan menghitung biaya pengiriman berdasarkan jarak dan berat.
   - Memperbarui status pesanan (misalnya, "Kurir mengambil paket", "Pesanan Selesai").
   - Menghapus pesanan yang sudah selesai dari histori.
   
2. **Perhitungan Biaya Pengiriman**: Sistem akan menghitung biaya pengiriman berdasarkan jarak antara kota asal dan tujuan (`JARAK_KOTA`) serta berat paket. Admin kemudian dapat mengonfirmasi biaya tersebut dan menyelesaikan pengiriman.

### Rute

- `/login`: Halaman login pengguna.
- `/logout`: Mengakhiri sesi pengguna.
- `/admin`: Dashboard admin untuk mengelola pesanan.
- `/api/distributor5/orders/cek_ongkir`: API untuk memeriksa biaya pengiriman.
- `/api/distributor5/orders/fix_kirim`: API untuk mengonfirmasi pesanan.
- `/update_status`: Memperbarui status pengiriman.
- `/`: Halaman utama untuk memeriksa status pesanan dengan nomor resi.

## Berkontribusi

Kontribusi sangat diterima! Untuk berkontribusi pada proyek ini:

1. Fork repositori ini.
2. Buat branch baru (`git checkout -b feature-branch`).
3. Commit perubahan Anda (`git commit -m 'Menambahkan fitur baru'`).
4. Push branch ke repositori forked Anda (`git push origin feature-branch`).
5. Buat pull request.

## Lisensi

Proyek ini dilisensikan di bawah Lisensi MIT. Lihat file [LICENSE](LICENSE) untuk informasi lebih lanjut.
