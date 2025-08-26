import pyautogui
import cv2
import numpy as np
import time
import requests

__version__ = "1.0.0"

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

def check_for_updates():
    try:
        repo_url = "https://api.github.com/repos/ege/hilebot/releases/latest"
        response = requests.get(repo_url)
        response.raise_for_status()
        latest = response.json()["tag_name"].lstrip("v")
        if latest > __version__:
            print(f"[GÜNCELLEME] Yeni sürüm mevcut: {latest}. Mevcut sürüm: {__version__}")
        else:
            print("[GÜNCELLEME] En son sürümü kullanıyorsunuz.")
    except Exception as e:
        print("[GÜNCELLEME] Güncelleme kontrolü başarısız:", e)

if __name__ == "__main__":
    print("Bot başladı. ESC ile durdurabilirsiniz.")
    check_for_updates()
    time.sleep(2)
    imza_cooldown = False

    while True:
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

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cv2.destroyAllWindows()