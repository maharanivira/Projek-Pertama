#!/usr/bin/env python3
"""
Skrip manajemen keuangan sederhana.

Fitur:
- Tambah pemasukan / pengeluaran
- Simpan dan muat transaksi ke `data.json`
- Tampilkan ringkasan bulanan (total pemasukan, pengeluaran, dan saldo)
- Mode `--test` untuk menjalankan contoh otomatis tanpa input

Gunakan: `python chochocranci.py` untuk interaktif
	   `python chochocranci.py --test` untuk demo otomatis
"""
import json
import os
import sys
from datetime import date, datetime

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data.json')


def load_data():
	if not os.path.exists(DATA_FILE):
		return {"transactions": []}
	with open(DATA_FILE, 'r', encoding='utf-8') as f:
		try:
			return json.load(f)
		except Exception:
			print('Peringatan: gagal membaca data.json; membuat data baru.')
			return {"transactions": []}


def save_data(data):
	with open(DATA_FILE, 'w', encoding='utf-8') as f:
		json.dump(data, f, ensure_ascii=False, indent=2)


def add_transaction(tx_type, amount, category='', note='', tx_date=None):
	data = load_data()
	if tx_date is None:
		tx_date = date.today().isoformat()
	txn = {
		'type': tx_type,  # 'income' or 'expense'
		'amount': float(amount),
		'category': category,
		'note': note,
		'date': tx_date,
		'created_at': datetime.now().isoformat(),
	}
	data['transactions'].append(txn)
	save_data(data)


def get_month_transactions(year, month):
	data = load_data()
	results = []
	for t in data['transactions']:
		try:
			d = datetime.fromisoformat(t['date']).date()
		except Exception:6
			try:
				d = datetime.fromisoformat(t.get('created_at')).date()
			except Exception:
				continue
		if d.year == year and d.month == month:
			results.append(t)
	return results


def summarize_month(year, month):
	txs = get_month_transactions(year, month)
	total_income = sum(t['amount'] for t in txs if t['type'] == 'income')
	total_expense = sum(t['amount'] for t in txs if t['type'] == 'expense')
	balance = total_income - total_expense
	return {
		'income': total_income,
		'expense': total_expense,
		'balance': balance,
		'count': len(txs),
	}


def print_summary(year, month):
	s = summarize_month(year, month)
	print('\nRingkasan untuk {:04d}-{:02d}'.format(year, month))
	print('  Total Pemasukan : Rp{:,.2f}'.format(s['income']))
	print('  Total Pengeluaran: Rp{:,.2f}'.format(s['expense']))
	print('  Saldo            : Rp{:,.2f}'.format(s['balance']))
	print('  Jumlah transaksi : {}'.format(s['count']))


def list_transactions(txs):
	if not txs:
		print('Tidak ada transaksi.')
		return
	for i, t in enumerate(txs, 1):
		print(f"{i}. [{t['date']}] {t['type'].upper():7} Rp{t['amount']:,.2f} - {t.get('category','')} {t.get('note','')}")


def interactive_menu():
	while True:
		print('\n--- Manajemen Keuangan Sederhana ---')
		print('1) Tambah Pemasukan')
		print('2) Tambah Pengeluaran')
		print('3) Lihat Ringkasan Bulan Ini')
		print('4) Lihat Semua Transaksi')
		print('5) Hapus Semua Transaksi (konfirmasi)')
		print('0) Keluar')
		choice = input('Pilih angka: ').strip()
		if choice == '1':
			amt = input('Jumlah (contoh 150000): ').strip()
			try:
				float(amt)
			except Exception:
				print('Jumlah tidak valid. Gunakan angka, mis. 150000 atau 150000.50')
				continue
			cat = input('Kategori (opsional): ').strip()
			note = input('Catatan (opsional): ').strip()
			add_transaction('income', amt, cat, note)
			print('Pemasukan tersimpan.')
		elif choice == '2':
			amt = input('Jumlah (contoh 50000): ').strip()
			try:
				float(amt)
			except Exception:
				print('Jumlah tidak valid. Gunakan angka, mis. 50000 atau 50000.00')
				continue
			cat = input('Kategori (opsional): ').strip()
			note = input('Catatan (opsional): ').strip()
			add_transaction('expense', amt, cat, note)
			print('Pengeluaran tersimpan.')
		elif choice == '3':
			today = date.today()
			print_summary(today.year, today.month)
		elif choice == '4':
			data = load_data()
			list_transactions(data.get('transactions', []))
		elif choice == '5':
			confirm = input('Ketik "YA" untuk konfirmasi hapus semua: ').strip()
			if confirm.upper() == 'YA':
				save_data({"transactions": []})
				print('Semua transaksi dihapus.')
			else:
				print('Dibatalkan.')
		elif choice == '0':
			print('Selesai. Sampai jumpa!')
			break
		else:
			print('Pilihan tidak dikenal. Coba lagi.')


def demo_run():
	# Tambahkan beberapa transaksi contoh untuk bulan ini
	today = date.today()
	y, m = today.year, today.month
	add_transaction('income', 5000000, 'Gaji', 'Gaji bulan ini', f'{y}-{m:02d}-01')
	add_transaction('expense', 1500000, 'Sewa', 'Sewa rumah', f'{y}-{m:02d}-02')
	add_transaction('expense', 300000, 'Makan', 'Makan dan belanja', f'{y}-{m:02d}-05')
	print('Menjalankan demo: menambahkan 3 transaksi contoh.')
	print_summary(y, m)


def main(argv=None):
	import argparse

	parser = argparse.ArgumentParser(description='Skrip manajemen keuangan sederhana')
	parser.add_argument('--test', action='store_true', help='Jalankan demo otomatis (tanpa input)')
	parser.add_argument('--demo', action='store_true', help='Alias untuk --test')
	parser.add_argument('--noninteractive', action='store_true', help='Jalankan ringkasan singkat bila tidak ada TTY')
	args = parser.parse_args(argv)

	# Jika environment tidak interaktif dan tidak ada flag, beri pesan dan keluar
	if not sys.stdin.isatty() and not (args.test or args.demo or args.noninteractive):
		print('Program membutuhkan mode interaktif. Jalankan dengan --test untuk demo, atau buka di terminal interaktif.')
		sys.exit(1)

	try:
		if args.test or args.demo or args.noninteractive:
			demo_run()
		else:
			interactive_menu()
	except KeyboardInterrupt:
		print('\nTerhenti oleh pengguna (KeyboardInterrupt). Keluar.')


if __name__ == '__main__':
	main()

