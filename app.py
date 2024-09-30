from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Inisialisasi Firebase Admin SDK
cred = credentials.Certificate("ladju_distributor.json")
firebase_admin.initialize_app(cred)

# Firestore database instance
db = firestore.client()

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Kunci rahasia untuk sesi flash

# Fungsi untuk mengecek validitas login menggunakan Firestore
def check_login(username, password):
    try:
        user_ref = db.collection('users').where('username', '==', username).where('password', '==', password).get()
        return len(user_ref) > 0
    except Exception as e:
        print(f"Error checking login: {e}")
        return False

# Fungsi untuk mengambil data jarak dan lama pengiriman dari Firestore
def get_jarak_kota():
    try:
        jarak_docs = db.collection('jarak_kota').stream()
        return {(doc.id.split('_')[0], doc.id.split('_')[1]): doc.to_dict()['jarak'] for doc in jarak_docs}
    except Exception as e:
        print(f"Error getting jarak kota: {e}")
        return {}

def get_lama_pengiriman():
    try:
        lama_docs = db.collection('lama_pengiriman').stream()
        return {(doc.id.split('_')[0], doc.id.split('_')[1]): doc.to_dict()['lama'] for doc in lama_docs}
    except Exception as e:
        print(f"Error getting lama pengiriman: {e}")
        return {}

# Fungsi untuk mengambil daftar status dari Firestore
def get_status_list():
    try:
        status_docs = db.collection('status_list').stream()
        return [doc.to_dict()['status'] for doc in status_docs]
    except Exception as e:
        print(f"Error getting status list: {e}")
        return []

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if check_login(username, password):
            session['username'] = username  # Simpan status login dalam session
            flash('Login successful!', 'success')
            return redirect(url_for('admin'))
        else:
            flash('Invalid username or password!', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()  # Hapus session user
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# Route untuk cek harga oleh supplier
@app.route('/api/distributor5/orders/cek_ongkir', methods=['POST'])
def cek_harga():
    data = request.get_json()  # Menerima data dalam format JSON
    kota_tujuan = data.get('kota_tujuan')
    kota_asal = data.get('kota_asal')
    berat = float(data.get('berat', 0))
    id_log = data.get('id_log')

    # Perhitungan ongkos kirim berdasarkan jarak dan berat
    JARAK_KOTA = get_jarak_kota()
    LAMA_PENGIRIMAN = get_lama_pengiriman()

    jarak = JARAK_KOTA.get((kota_tujuan.lower(), kota_asal.lower()), 0)
    ongkos_kirim = (jarak * 500) + (berat * 1000)

    lama_pengiriman = LAMA_PENGIRIMAN.get((kota_tujuan.lower(), kota_asal.lower()), 'Tidak diketahui')

    if jarak == 0:
        return {'status': 'error', 'message': 'Kombinasi kota tujuan dan kota asal tidak ditemukan.'}, 400

    # Generate ID berdasarkan id_log
    new_id = f'LOGDISS{id_log}'

    try:
        # Simpan data pesanan ke Firestore collection 'tb_pesanan'
        db.collection('tb_pesanan').document(new_id).set({
            'kota_tujuan': kota_tujuan,
            'kota_asal': kota_asal,
            'berat': berat,
            'quantity': data.get('quantity', 0),
            'id_log': id_log,
            'status': 'Menunggu Konfirmasi'
        })
    except Exception as e:
        print(f"Error saving order: {e}")
        return {'status': 'error', 'message': 'Gagal menyimpan pesanan.'}, 500

    # Kembalikan hasil perhitungan ongkos kirim sebagai response
    return jsonify({
        'status': 'success',
        'harga_pengiriman': ongkos_kirim,
        'jarak': jarak,
        'id_log': id_log,
        'lama_pengiriman': lama_pengiriman
    })

# Route untuk konfirmasi pesanan dan menyimpannya ke 'tb_ongkos_kirim'
@app.route('/api/distributor5/orders/fix_kirim', methods=['POST'])
def confirm_pesanan():
    data = request.get_json()  # Menerima data JSON
    id_log = data.get('id_log')
    pesanan_id = f'LOGDISS{id_log}'
    
    # Ambil data dari tb_pesanan berdasarkan id_log
    pesanan_doc = db.collection('tb_pesanan').document(pesanan_id).get()

    if pesanan_doc.exists:
        pesanan_data = pesanan_doc.to_dict()

        kota_tujuan = pesanan_data['kota_tujuan']
        kota_asal = pesanan_data['kota_asal']
        berat = pesanan_data['berat']
        quantity = pesanan_data['quantity']

        # Perhitungan ongkos kirim berdasarkan jarak dan berat
        JARAK_KOTA = get_jarak_kota()
        LAMA_PENGIRIMAN = get_lama_pengiriman()

        jarak = JARAK_KOTA.get((kota_tujuan.lower(), kota_asal.lower()), 0)
        ongkos_kirim = (jarak * 500) + (berat * 1000)
        lama_pengiriman = LAMA_PENGIRIMAN.get((kota_tujuan.lower(), kota_asal.lower()), 'Tidak diketahui')

        if jarak == 0:
            return jsonify({'status': 'error', 'message': 'Kombinasi kota tujuan dan kota asal tidak ditemukan.'}), 400

        # Mapping kode kota
        supplier_codes = {'madura': 'S01', 'solo': 'S02', 'batam': 'S03'}
        retail_codes = {'ngawi': 'R01', 'denpasar': 'R02', 'surabaya': 'R03'}

        supplier_code = supplier_codes.get(kota_asal.lower(), 'S00')
        retail_code = retail_codes.get(kota_tujuan.lower(), 'R00')

        # Generate id_resi
        existing_resi = db.collection('tb_ongkos_kirim').where('kota_tujuan', '==', kota_tujuan)\
            .where('kota_asal', '==', kota_asal).stream()

        pk_count = sum(1 for _ in existing_resi) + 1
        no_resi = f'LES{supplier_code}{retail_code}PK{str(pk_count).zfill(3)}'

        # Generate tanggal pembelian
        tanggal_pembelian = datetime.now().strftime('%Y-%m-%d')

        try:
            # Simpan data ke 'tb_ongkos_kirim'
            new_ongkos_id = f'LOGDIS{str(id_log).zfill(5)}'
            db.collection('tb_ongkos_kirim').document(new_ongkos_id).set({
                'kota_tujuan': kota_tujuan,
                'kota_asal': kota_asal,
                'harga_pengiriman': str(ongkos_kirim),
                'berat': berat,
                'quantity': quantity,
                'no_resi': no_resi,
                'status': 'Pesanan sedang diproses',
                'id_log': pesanan_data['id_log'],
                'tanggal_pembelian': tanggal_pembelian,
                'lama_pengiriman': lama_pengiriman
            })

            # Hapus pesanan dari 'tb_pesanan'
            db.collection('tb_pesanan').document(pesanan_id).delete()
        except Exception as e:
            print(f"Error confirming order: {e}")
            return jsonify({'status': 'error', 'message': 'Gagal mengonfirmasi pesanan.'}), 500

        # Kembalikan response ke supplier
        return jsonify({
            'status': 'success',
            'harga_pengiriman': ongkos_kirim,
            'no_resi': no_resi,
            'tanggal_pembelian': tanggal_pembelian,
            'lama_pengiriman': lama_pengiriman
        })

    return jsonify({'status': 'error', 'message': 'Pesanan tidak ditemukan.'}), 404

# Route untuk memperbarui status ongkos kirim
@app.route('/update_status', methods=['POST'])
def update_status():
    try:
        doc_id = request.form['doc_id']
        new_status = request.form['status']
        
        # Tambahkan print statement untuk memastikan data diterima dengan benar
        print(f"doc_id: {doc_id}, new_status: {new_status}")
        
        # Dapatkan data dokumen dari tb_ongkos_kirim
        doc_ref = db.collection('tb_ongkos_kirim').document(doc_id)
        
        # Pastikan dokumen ada sebelum melakukan update
        if doc_ref.get().exists:
            doc_ref.update({
                'status': new_status
            })
        
            # Jika status adalah "Pesanan Selesai", pindahkan ke tb_histori_pesanan
            if new_status == "Pesanan Selesai":
                doc_data = doc_ref.get().to_dict()
                db.collection('tb_histori_pesanan').document(doc_id).set(doc_data)
                db.collection('tb_ongkos_kirim').document(doc_id).delete()
        else:
            flash('Dokumen tidak ditemukan.', 'danger')
    except Exception as e:
        print(f"Error: {e}")
        flash('Terjadi kesalahan saat memperbarui status.', 'danger')

    return redirect(url_for('admin'))

@app.route('/admin')
def admin():
    try:
        # Ambil data dari Firestore collection 'tb_pesanan', 'tb_ongkos_kirim', dan 'tb_histori_pesanan'
        pesanan_docs = db.collection('tb_pesanan').stream()
        ongkos_docs = db.collection('tb_ongkos_kirim').stream()
        histori_docs = db.collection('tb_histori_pesanan').stream()

        # Mengonversi dokumen Firestore menjadi list Python
        pesanan_list = [{'new_id': doc.id, **doc.to_dict()} for doc in pesanan_docs]
        ongkos_list = [{'new_id': doc.id, **doc.to_dict()} for doc in ongkos_docs]
        histori_list = [{'new_id': doc.id, **doc.to_dict()} for doc in histori_docs]

        for ongkos in ongkos_list:
            ongkos['harga_pengiriman'] = float(ongkos['harga_pengiriman'])

        for histori in histori_list:
            histori['harga_pengiriman'] = float(histori['harga_pengiriman'])

        # Ambil daftar status dari Firestore
        status_list = get_status_list()

        return render_template(
            'admin.html', 
            pesanan=pesanan_list, 
            ongkos=ongkos_list, 
            histori_pesanan=histori_list, 
            status_list=status_list,
            format_harga=format_harga
        )
    except Exception as e:
        print(f"Error loading admin data: {e}")
        flash('Terjadi kesalahan saat memuat data admin.', 'danger')
        return render_template('admin.html', pesanan=[], ongkos=[], histori_pesanan=[], status_list=[])

def format_harga(harga):
    return f"Rp {harga:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

@app.route('/delete_history/<id>', methods=['POST'])
def delete_history(id):
    try:
        # Hapus data dari tb_ongkos_kirim berdasarkan ID
        db.collection('tb_histori_pesanan').document(id).delete()
    except Exception as e:
        print(f"Error deleting history: {e}")
        flash('Terjadi kesalahan saat menghapus histori.', 'danger')
    return redirect(url_for('admin'))

# Cek resi route
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        nomor_resi = request.form.get('nomor_resi')
        
        try:
            # Cari nomor resi di Firestore pada tabel tb_ongkos_kirim
            ongkos_kirim_doc = db.collection('tb_ongkos_kirim').where('no_resi', '==', nomor_resi).get()
            
            # Jika resi ditemukan di tb_ongkos_kirim
            if ongkos_kirim_doc:
                ongkos_kirim_data = ongkos_kirim_doc[0].to_dict()
                lama_pengiriman = ongkos_kirim_data.get('lama_pengiriman', 'Data lama pengiriman tidak tersedia')
                return render_template('index.html', nomor_resi=nomor_resi, status=ongkos_kirim_data['status'], lama_pengiriman=lama_pengiriman)
            
            # Jika resi tidak ditemukan di tb_ongkos_kirim, cari di tb_histori_pesanan
            histori_pesanan_doc = db.collection('tb_histori_pesanan').where('no_resi', '==', nomor_resi).get()
            
            # Jika resi ditemukan di tb_histori_pesanan
            if histori_pesanan_doc:
                histori_pesanan_data = histori_pesanan_doc[0].to_dict()
                lama_pengiriman = histori_pesanan_data.get('lama_pengiriman', 'Data lama pengiriman tidak tersedia')
                return render_template('index.html', nomor_resi=nomor_resi, status=histori_pesanan_data['status'], lama_pengiriman=lama_pengiriman)
            
            # Jika tidak ditemukan di kedua tabel
            error = "Nomor resi tidak ditemukan."
            return render_template('index.html', error=error)
        except Exception as e:
            print(f"Error checking resi: {e}")
            return render_template('index.html', error="Terjadi kesalahan saat memeriksa nomor resi.")

    # Jika request GET, tampilkan halaman tanpa error atau status
    return render_template('index.html')

@app.route('/api/status/<string:id_resi>', methods=['GET'])
def get_status(id_resi):
    try:
        # Cari nomor resi di Firestore pada tabel tb_ongkos_kirim
        ongkos_kirim_doc = db.collection('tb_ongkos_kirim').where('no_resi', '==', id_resi).get()
        
        # Jika resi ditemukan di tb_ongkos_kirim
        if ongkos_kirim_doc:
            ongkos_kirim_data = ongkos_kirim_doc[0].to_dict()
            lama_pengiriman = ongkos_kirim_data.get('lama_pengiriman', 'Data lama pengiriman tidak tersedia')
            return jsonify({
                'lama_pengiriman': lama_pengiriman,
                'status': ongkos_kirim_data['status']
            })
        
        # Jika resi tidak ditemukan di tb_ongkos_kirim, cari di tb_histori_pesanan
        histori_pesanan_doc = db.collection('tb_histori_pesanan').where('no_resi', '==', id_resi).get()
        
        # Jika resi ditemukan di tb_histori_pesanan
        if histori_pesanan_doc:
            histori_pesanan_data = histori_pesanan_doc[0].to_dict()
            lama_pengiriman = histori_pesanan_data.get('lama_pengiriman', 'Data lama pengiriman tidak tersedia')
            return jsonify({
                'lama_pengiriman': lama_pengiriman,
                'status': histori_pesanan_data['status']
            })
        
        # Jika tidak ditemukan di kedua tabel
        return jsonify({'error': 'Nomor resi tidak ditemukan.'}), 404
    except Exception as e:
        print(f"Error getting status: {e}")
        return jsonify({'error': 'Terjadi kesalahan saat memeriksa status.'}), 500

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)