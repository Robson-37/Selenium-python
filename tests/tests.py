import os
import sys
import time
import unittest
import ctypes
import pyautogui
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Ajuste de sensibilidade do PyAutoGUI
pyautogui.PAUSE = 0.2
pyautogui.FAILSAFE = False

# Garante compatibilidade de DPI com telas do Windows (100%, 125%, 150%)
if sys.platform == "win32":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # Per-monitor DPI aware
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def mover_mouse_para_elemento(driver, by, valor):
    # Aguarda o elemento estar visível
    elemento = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((by, valor))
    )

    # Rola suavemente até o elemento estar visível no centro da tela
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", elemento)
    time.sleep(0.4)

    # --- Método 1: Localização por Imagem (OpenCV) ---
    # Tira um print do elemento e localiza onde ele realmente está na tela do monitor.
    # É imune a erros de DPI, barra de ferramentas ou zoom.
    temp_img = f"temp_{valor}.png"
    try:
        elemento.screenshot(temp_img)
        pos = pyautogui.locateCenterOnScreen(temp_img, confidence=0.75)
        if pos:
            print(f"[Visão Computacional] Elemento '{valor}' encontrado em X={pos.x} Y={pos.y}")
            pyautogui.moveTo(pos.x, pos.y, duration=0.8)
            if os.path.exists(temp_img):
                os.remove(temp_img)
            return {"x": pos.x, "y": pos.y}
    except Exception as err:
        print(f"[Aviso] Busca por imagem não encontrou: {err}. Usando cálculo de coordenadas.")
    finally:
        if os.path.exists(temp_img):
            try:
                os.remove(temp_img)
            except Exception:
                pass

    # --- Método 2: Cálculo Matemático com correção de DPI e offset ---
    metrics = driver.execute_script("""
        const r = arguments[0].getBoundingClientRect();
        return {
            elemX: r.left + r.width / 2,
            elemY: r.top + r.height / 2,
            toolbarHeight: window.outerHeight - window.innerHeight,
            screenX: window.screenX,
            screenY: window.screenY,
            dpr: window.devicePixelRatio || 1
        };
    """, elemento)

    # Obter posição e tamanho da janela segundo o Selenium
    win_rect = driver.get_window_rect()
    win_x = win_rect["x"]
    win_y = win_rect["y"]

    # Fator de escala do Windows (DPI)
    dpr = metrics["dpr"]
    toolbar = metrics["toolbarHeight"]

    # Coordenadas ajustadas na tela
    x = win_x + (metrics["elemX"] * dpr)
    y = win_y + (toolbar * dpr) + (metrics["elemY"] * dpr)

    print(f"[Coordenadas] Movendo para X={int(x)} Y={int(y)} (DPR={dpr})")
    pyautogui.moveTo(x, y, duration=0.8)
    return {"x": int(x), "y": int(y)}


class TestExample(unittest.TestCase):
    def setUp(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(options=options)
        self.driver.get("https://www.saucedemo.com/")
        # Pequena pausa para garantir carregamento e foco da tela
        time.sleep(1)

    def test_login(self):
        # 1. Campo de usuário
        mover_mouse_para_elemento(self.driver, By.ID, "user-name")
        pyautogui.click()
        pyautogui.write("standard_user", interval=0.1)
        time.sleep(0.5)

        # 2. Campo de senha
        mover_mouse_para_elemento(self.driver, By.ID, "password")
        pyautogui.click()
        pyautogui.write("secret_sauce", interval=0.1)
        time.sleep(0.5)

        # 3. Botão de login
        mover_mouse_para_elemento(self.driver, By.ID, "login-button")
        pyautogui.click()

        # Tempo para visualizar a página após o login
        time.sleep(5)

        mover_mouse_para_elemento(self.driver, By.ID, "add-to-cart-sauce-labs-backpack")
        pyautogui.click()
        time.sleep(5)

    def tearDown(self):
        self.driver.quit()


if __name__ == "__main__":
    unittest.main()
