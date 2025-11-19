import os
import time
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# API Configuration
BASE_URL = os.getenv("BASE_URL")
BEARER_TOKEN = os.getenv("BEARER_TOKEN")

# Delay configuration (dalam detik)
DELAY_BETWEEN_PHOTOS = float(os.getenv("DELAY_BETWEEN_PHOTOS", "1.0"))  # Default 1 detik

if not BEARER_TOKEN:
    raise ValueError("BEARER_TOKEN tidak ditemukan di file .env")

# Headers dengan Bearer token
headers = {
    "Authorization": f"Bearer {BEARER_TOKEN}",
    "Content-Type": "application/json"
}


def get_yesterday_date():
    """Mendapatkan tanggal kemarin dalam format YYYY-MM-DD"""
    yesterday = datetime.now() - timedelta(days=1)
    return yesterday.strftime("%Y-%m-%d")


def get_panen_data(tanggal):
    """Fetch data panen dari API"""
    url = f"{BASE_URL}cmpmain/getData"
    
    payload = {
        "table": "panen",
        "select": [
            "id",
            "foto"
        ],
        "where": {
            "tanggal": tanggal,
            "foto": {
                "not null": True
            }
        }
    }
    
    print(f"Mengambil data panen untuk tanggal: {tanggal}")
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    
    data = response.json()
    
    if data.get("success"):
        print(f"Berhasil mengambil {data.get('count', 0)} data")
        return data.get("data", [])
    else:
        print("Gagal mengambil data")
        return []


def download_photo(photo_path, save_path):
    """Download foto dari API dan simpan ke local"""
    url = f"{BASE_URL}photos/get"
    
    payload = {
        "type": "panen_table",
        "path": photo_path
    }
    
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    
    # Cek apakah response adalah JSON (error response)
    content_type = response.headers.get('Content-Type', '').lower()
    is_json_response = 'application/json' in content_type or response.text.strip().startswith('{')
    
    if is_json_response:
        try:
            json_response = response.json()
            if not json_response.get("success", True):
                message = json_response.get("message", "")
                if "Photo not found" in message or "not found" in message.lower():
                    raise ValueError(f"Photo not found: {photo_path}")
        except ValueError:
            # Re-raise ValueError untuk photo not found
            raise
        except (KeyError, requests.exceptions.JSONDecodeError):
            # Jika parsing JSON gagal, lanjutkan dengan asumsi binary content
            pass
    
    # Simpan foto (hanya jika bukan error JSON)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, 'wb') as f:
        f.write(response.content)
    
    print(f"Foto tersimpan: {save_path}")


def main():
    # Get tanggal kemarin
    tanggal = get_yesterday_date()
    
    # Parse tanggal untuk folder
    date_obj = datetime.strptime(tanggal, "%Y-%m-%d")
    folder_date = date_obj.strftime("%d-%m-%Y")
    
    # Folder tujuan
    base_folder = Path("sawit") / folder_date
    base_folder.mkdir(parents=True, exist_ok=True)
    
    # Fetch data panen
    panen_data = get_panen_data(tanggal)
    
    # Delay setelah fetch data
    time.sleep(0.5)
    
    if not panen_data:
        print("Tidak ada data panen yang ditemukan")
        return
    
    # Download setiap foto
    print(f"\nMemulai download foto dari {len(panen_data)} data panen...")
    total_photos = 0
    downloaded_count = 0
    
    for idx, item in enumerate(panen_data, 1):
        photo_path = item.get("foto")
        photo_id = item.get("id")
        
        if not photo_path:
            print(f"Data {photo_id}: Foto path kosong, dilewati")
            continue
        
        # Split foto path jika ada titik koma (multiple photos)
        photo_paths = [path.strip() for path in photo_path.split(';') if path.strip()]
        total_photos += len(photo_paths)
        
        print(f"\nData {photo_id}: Ditemukan {len(photo_paths)} foto")
        
        # Download setiap foto
        for photo_idx, single_photo_path in enumerate(photo_paths, 1):
            # Nama file dari path
            filename = os.path.basename(single_photo_path)
            save_path = base_folder / filename
            
            try:
                print(f"  [{photo_idx}/{len(photo_paths)}] Downloading: {filename}")
                download_photo(single_photo_path, save_path)
                downloaded_count += 1
            except ValueError as e:
                # Skip jika photo not found
                if "Photo not found" in str(e):
                    print(f"  ⚠️  Foto tidak ditemukan, dilewati: {filename}")
                else:
                    print(f"  Error: {str(e)}")
                continue
            except Exception as e:
                print(f"  Error downloading {filename}: {str(e)}")
                continue
            
            # Delay antar foto untuk menghindari overload server
            if photo_idx < len(photo_paths) or idx < len(panen_data):
                time.sleep(DELAY_BETWEEN_PHOTOS)
    
    print(f"\nSelesai! {downloaded_count}/{total_photos} foto berhasil di-download")
    print(f"Foto tersimpan di folder: {base_folder}")


if __name__ == "__main__":
    main()

