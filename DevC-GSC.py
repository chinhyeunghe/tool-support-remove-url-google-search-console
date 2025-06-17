# pip install customtkinter
import customtkinter as ctk
from tkinter import filedialog
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
import csv
import time
import os
import sys
import threading

ctk.set_appearance_mode("dark")  # Giao diện dark mode
ctk.set_default_color_theme("blue")

def resource_path(relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

class URLRemoverApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Đặng Đức Chính (DevC) - Tool siêu nhân xóa URL Google Search Console")
        self.geometry("700x500")

        self.file_path = None
        self.urls = []
        

        # Load ảnh nền
        # Load ảnh
        self.bg_image = ctk.CTkImage(Image.open(resource_path("images-FS.png")), size=(80, 80))
        self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
        self.bg_label.place(x=15, y=15)

        # Giao diện
        self.label = ctk.CTkLabel(self, text="Tool Xóa URL Google Search Console", font=("Arial", 20))
        self.label.pack(pady=20)

        self.domain_label = ctk.CTkLabel(self, text="Nhập domain website (vd: mbt.com.vn):")
        self.domain_label.pack(pady=5)

        self.domain_input = ctk.CTkEntry(self, width=400)
        self.domain_input.pack(pady=5)

        self.choose_button = ctk.CTkButton(self, text="💾 File .CSV Google SC", command=self.choose_file, fg_color='#27ae60', hover_color='#2ecc71')
        self.choose_button.pack(pady=10)

        self.run_button = ctk.CTkButton(self, text="Bắt đầu", command=self.run_tool, state="disabled", width=200, height=40, font=("Arial", 18, "bold"))
        self.run_button.pack(pady=10)

        self.textbox = ctk.CTkTextbox(self, width=600, height=350)
        self.textbox.pack(pady=10)
    

    def choose_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            self.file_path = file_path
            self.urls = self.read_csv(file_path)
            self.textbox.insert("end", f"✔ Đã chọn file: {file_path}\n")
            self.textbox.insert("end", f"✔ Đã đọc {len(self.urls)} URL.\n")
            self.run_button.configure(state="normal")

    def read_csv(self, file_path):
        urls = []
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                if row:
                    urls.append(row[0])
        return urls

    def run_tool(self):
        threading.Thread(target=self.process_urls).start()

    def log(self, message):
        self.textbox.insert("end", f"{message}\n")
        self.textbox.see("end")

    def process_urls(self):
        domain = self.domain_input.get().strip()
        if not domain:
            self.log("❗ Vui lòng nhập domain trước khi chạy tool!")
            return

        url_console = f'https://search.google.com/search-console/removals?resource_id=sc-domain%3A{domain}&hl=fr'

        chrome_options = Options()

        # Dùng thư mục profile để giữ đăng nhập Google
        user_data_dir = os.path.join(os.getcwd(), 'temp', 'profile')
        chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
        chrome_options.add_argument("--profile-directory=Default")

        # Một số option để tránh bị phát hiện
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)

        service = Service()
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # Che dấu webdriver
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        # Mở trang removals
        driver.get(url_console)

        # Đợi trang tải và URL đúng
        WebDriverWait(driver, 120).until(lambda d: "search-console/removals" in d.current_url)

        self.log(f"✔ Đã vào trang Removals của domain: {domain}")

        try:
            for url in self.urls:
                try:
                    # Bấm nút thêm URL mới
                    menu_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, "ZGldwb"))
                        # EC.element_to_be_clickable((By.XPATH, "/html/body/div[8]/c-wiz[4]/div/div[2]/div/div/div/div/div[2]/span[1]/div/div/div/div[1]/div/div[2]/div"))
                    )
                    menu_button.click()

                    # Nhập URL cần xóa
                    url_input = WebDriverWait(driver, 20).until(
                        # EC.presence_of_element_located((By.CLASS_NAME, 'VfPpkd-fmcmS-wGMbrd'))
                        EC.presence_of_element_located((By.XPATH, "/html/body/div[8]/div[6]/div/div[2]/span/div/div/div[2]/span[1]/div[2]/label/input"))
                    )

                    url_input.clear()
                    url_input.send_keys(url)
                    self.log(f"✔ Đã điền URL: {url}")

                    # Click nút tiếp theo
                    button_next = WebDriverWait(driver, 20).until(
                        EC.element_to_be_clickable((By.XPATH, "/html/body/div[8]/div[6]/div/div[2]/div[3]/div[2]"))
                    )
                    button_next.click()

                    time.sleep(3)

                    # Click nút xác nhận
                    button_success = WebDriverWait(driver, 20).until(
                        EC.element_to_be_clickable((By.XPATH, '/html/body/div[8]/div[6]/div/div[2]/div[3]/div[2]'))
                    )
                    button_success.click()

                    time.sleep(3)
                    elements = driver.find_elements(By.XPATH, '/html/body/div[8]/div[6]/div/div[2]/div[3]/div')
                    elements2 = driver.find_elements(By.XPATH, '/html/body/div[8]/div[6]/div/div[2]/div[3]/div[2]')

                    if elements:
                        # Nếu tìm thấy ít nhất 1 phần tử, Selenium sẽ click vào phần tử đầu tiên
                        self.log(f"✔ URL này đã được xóa trước đó: {url}")
                        elements[0].click()
                    else:
                        self.log(f"✔ Đã xóa URL: {url}")

                    
                    time.sleep(2)

                except Exception as e:
                    self.log(f"❌ Lỗi khi xử lý URL {url}: {e}")
                    continue

            self.log("✔ Đã hoàn tất!")

        except Exception as e:
            self.log(f"❌ Lỗi tổng: {e}")

        driver.quit()
    

if __name__ == "__main__":
    app = URLRemoverApp()
    app.mainloop()
