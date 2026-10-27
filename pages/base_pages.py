import pyautogui
import time


#def mostrar_coordenadas_mouse():
    #print("Mova o mouse. Pressione Ctrl+C para sair.\n")
    #try:
        #while True:
            #x, y = pyautogui.position()
            #print(f"X: {x} | Y: {y}", end="\r")
            #ime.sleep(0.1)

    #except KeyboardInterrupt:
        #print("\nMonitoramento encerrado.")

# Chamada da função
#mostrar_coordenadas_mouse()

#=====================================================================
def mover_mouse_para_elemento(driver, by, valor):
    elemento = driver.find_element(by, valor)

    rect = driver.execute_script("""
        const r = arguments[0].getBoundingClientRect();
        return {
            x: r.left + r.width/2,
            y: r.top + r.height/2
        };
    """, elemento)

    janela_x = driver.get_window_position()["x"]
    janela_y = driver.get_window_position()["y"]

    x = janela_x + rect["x"]
    y = janela_y + rect["y"]

    print(f"Coordenada da tela => X={int(x)} Y={int(y)}")

    pyautogui.moveTo(x, y, duration=1)

    return {"x": int(x), "y": int(y)}