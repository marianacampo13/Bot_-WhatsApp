import time
from playwright.sync_api import sync_playwright

USER_DATA_DIR = "./whatsapp_session"

# IMPORTANTE: Incluye el código de país sin el signo '+' ni espacios (Ej: Colombia es 57 + número -> 573001234567)
PHONE_NUMBER = "573186577999"  
MESSAGE_TEXT = "Soy un bot de prueba fabricado por el mejor profe, este mensaje se enviará automáticamente cada 10 segundos hasta que el destinatario responda. ¡Gracias por tu paciencia!"
INTERVAL_SECONDS = 10  # Intervalo de reenvío (segundos)
CHECK_FREQUENCY = 5     # Monitoreo de respuesta (segundos)

def run_followup_loop():
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False,
            args=["--start-maximized"]
        )
        page = browser.new_page()

        # 1. Cargar WhatsApp Web para autenticación
        page.goto("https://web.whatsapp.com")
        print("\n" + "="*50)
        print("1. Si aparece el código QR, escanéalo con tu celular.")
        print("2. Espera a que carguen tus chats en la pantalla.")
        input("3. Cuando veas tus chats listos, PRESIONA ENTER AQUÍ EN LA TERMINAL...")
        print("="*50 + "\n")

        # 2. Navegar directamente al chat del número telefónico
        print(f"Abriendo conversación con: {PHONE_NUMBER}...")
        chat_url = f"https://web.whatsapp.com/send?phone={PHONE_NUMBER}"
        page.goto(chat_url)

        # 3. Esperar a que cargue la caja de texto para escribir el mensaje
        input_selector = 'footer div[contenteditable="true"]'
        print("Esperando a que cargue el cuadro de texto del chat...")
        chat_input = page.locator(input_selector).first
        chat_input.wait_for(state="visible", timeout=60000)
        time.sleep(3)  # Pausa breve para renderizar mensajes previos

        # Selector de mensajes entrantes (los que envía la otra persona)
        incoming_selector = 'div.message-in'
        initial_incoming_count = page.locator(incoming_selector).count()
        print(f"Chat cargado con éxito. Mensajes recibidos previos: {initial_incoming_count}")

        try:
            while True:
                # Verificar si respondieron antes de enviar
                current_incoming_count = page.locator(incoming_selector).count()
                if current_incoming_count > initial_incoming_count:
                    print(f"¡Respuesta detectada! Bucle terminado exitosamente.")
                    break

                # Escribir y enviar mensaje
                chat_input.click()
                chat_input.fill(MESSAGE_TEXT)
                page.keyboard.press("Enter")
                print(f"[{time.strftime('%H:%M:%S')}] Mensaje enviado. Esperando respuesta...")

                # Ciclo de espera con detección continua
                elapsed = 0
                responded = False
                while elapsed < INTERVAL_SECONDS:
                    time.sleep(CHECK_FREQUENCY)
                    elapsed += CHECK_FREQUENCY
                    
                    current_incoming_count = page.locator(incoming_selector).count()
                    if current_incoming_count > initial_incoming_count:
                        print(f"[{time.strftime('%H:%M:%S')}] ¡El destinatario ha respondido! Deteniendo...")
                        responded = True
                        break

                if responded:
                    break

        except KeyboardInterrupt:
            print("\nDetenido manualmente por el usuario.")
        finally:
            print("Cerrando navegador...")
            browser.close()

if __name__ == "__main__":
    run_followup_loop()