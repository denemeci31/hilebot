import pyautogui
import cv2
import numpy as np
import time
import requests
import keyboard
import sys
import os
import shutil
import zipfile

__version__ = "6.6.6"

MATCH_THRESH = 0.75

TEMPLATES = {
    "start": cv2.imread("assets/start.png"),
    "kapi1": cv2.imread("assets/kapi1.png"),
    "kapi2": cv2.imread("assets/kapi2.png"),
    "health": cv2.imread("assets/health.png"),
    "imza": cv2.imread("assets/imza.png"),
    "s": cv2.imread("assets/s.png"),
    "o": cv2.imread("assets/o.png"),
    "r": cv2.imread("assets/r.png"),
    "g": cv2.imread("assets/g.png"),
    "u": cv2.imread("assets/u.png"),
    "enter": cv2.imread("assets/enter.png"),
}

def screenshot():
    img = pyautogui.screenshot()
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

def find_all(template, screenshot_img, threshold=MATCH_THRESH):
    result = cv2.matchTemplate(screenshot_img, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(result >= threshold)
    h, w = template.shape[:2]
    matches = [(pt[0], pt[1], w, h) for pt in zip(*loc[::-1])]
    return matches

def click_center(x, y, w, h):
    center_x = x + w // 2
    center_y = y + h // 2
    pyautogui.moveTo(center_x, center_y, duration=0.2)
    pyautogui.click()
    time.sleep(0.3)

def auto_update():
    try:
        repo_url = "https://api.github.com/repos/denemeci31/hilebot/releases/latest"
        response = requests.get(repo_url)
        print("[GÜNCELLEME] API yanıtı alındı.")
        response.raise_for_status()
        data = response.json()
        latest_version = data["tag_name"].lstrip("v")
        download_url = data["zipball_url"]

        if latest_version > __version__:
            print(f"[GÜNCELLEME] Yeni sürüm mevcut: {latest_version}")
            ans = input("Güncelleme yapılsın mı? (e/h): ")
            if ans.lower() == "e":
                print("İndiriliyor...")
                zip_path = "update.zip"
                with requests.get(download_url, stream=True) as r:
                    r.raise_for_status()
                    with open(zip_path, "wb") as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)

                print("Kuruluyor...")
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall("update_temp")

                # Yeni dosyaları kopyala (geçici klasörler hariç)
                extracted_folder = os.listdir("update_temp")[0]
                for item in os.listdir(f"update_temp/{extracted_folder}"):
                    if item in [".git", "backup", "update_temp", "update.zip"]:
                        continue
                    s = os.path.join(f"update_temp/{extracted_folder}", item)
                    d = os.path.join(".", item)
                    if os.path.isdir(s):
                        shutil.copytree(s, d, dirs_exist_ok=True)
                    else:
                        shutil.copy2(s, d)

                # Temizlik
                shutil.rmtree("update_temp")
                os.remove(zip_path)

                print("Güncelleme tamamlandı. Yeniden başlatılıyor...")
                os.execv(sys.executable, ['python'] + sys.argv)
        else:
            print("[GÜNCELLEME] En son sürümü kullanıyorsunuz.")
    except Exception as e:
        print("[GÜNCELLEME] Otomatik güncelleme başarısız:", e)

if __name__ == "__main__":
    print("Bot başladı. ALT + H ile durdurabilirsiniz.")
    auto_update()
    time.sleep(2)
    imza_cooldown = False

    print("Bot çalışıyor... Durdurmak için ALT + H tuşlarına basın.")

    while True:
        if keyboard.is_pressed('alt+h'):
            print("[BOT] Durduruldu.")
            break

        frame = screenshot()

        # Kapılar ve start
        for key in ["start", "kapi1", "kapi2"]:
            matches = find_all(TEMPLATES[key], frame)
            if matches:
                click_center(*matches[0])
                print(f"{key} bulundu ve tıklandı!")

        # İmza kontrol
        if not imza_cooldown:
            imza_matches = find_all(TEMPLATES["imza"], frame)
            if imza_matches:
                print("[BOT] İmza bulundu! Hemen tıklanıyor...")
                click_center(*imza_matches[0])
                print("[BOT] İmza tıklandı, 10 saniye bekleniyor...")
                imza_cooldown = True
                time.sleep(10)

                # Bekleme sonrası sırayla tuş PNG'lerine bak ve tıkla
                for key in ["s","o","r","g","u","enter"]:
                    matches = find_all(TEMPLATES[key], screenshot())
                    if matches:
                        click_center(*matches[0])
                        print(f"{key} PNG bulundu ve tıklandı!")
                    time.sleep(1)

                imza_cooldown = False
                print("[BOT] Sıra tıklama tamamlandı, tekrar kontrol ediliyor...")

        time.sleep(0.1)  # küçük bekleme

    print("[BOT] Program kapatılıyor...")
    cv2.destroyAllWindows()
