
import time
from playwright.sync_api import sync_playwright

USER_DATA_DIR = "./whatsapp_session"

# Conserva aquí tu número con código de país.
PHONE_NUMBER = "573143111803"

MESSAGE_TEXT = (
    "Soy un bot de prueba fabricado por el mejor profe. "
    "Este es un mensaje automático de prueba."
)

INTERVAL_SECONDS = 10
CHECK_FREQUENCY = 2
MAX_SENDS = 10


def run_followup_loop():
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False,
            args=["--start-maximized"]
        )

        page = (
            browser.pages[0]
            if browser.pages
            else browser.new_page()
        )

        try:
            page.goto("https://web.whatsapp.com")

            print("Espera a que WhatsApp Web cargue.")
            input("Cuando tus chats estén listos, presiona ENTER...")

            page.goto(
                f"https://web.whatsapp.com/send?phone={PHONE_NUMBER}"
            )

            input_selector = 'footer div[contenteditable="true"]'
            chat_input = page.locator(input_selector).first
            chat_input.wait_for(state="visible", timeout=60000)

            time.sleep(5)

            incoming_selector = (
                '[data-testid^="conv-msg-"]:has('
                '[data-testid="tail-in"])'
            )

            mensajes_entrantes = page.locator(incoming_selector)

            # Registrar los identificadores que existen antes de enviar.
            ids_iniciales = set(
                mensajes_entrantes.evaluate_all(
                    """elementos => elementos
                        .map(el => el.getAttribute('data-testid'))
                        .filter(Boolean)"""
                )
            )

            print("Mensajes entrantes registrados:", len(ids_iniciales))
            print("Comenzando la prueba...")

            envios = 0

            while envios < MAX_SENDS:
                # Comprobar si aparece un identificador nuevo.
                ids_actuales = set(
                    mensajes_entrantes.evaluate_all(
                        """elementos => elementos
                            .map(el => el.getAttribute('data-testid'))
                            .filter(Boolean)"""
                    )
                )

                nuevos = ids_actuales - ids_iniciales

                if nuevos:
                    print("Se detectó un elemento entrante nuevo.")
                    print("Deteniendo los envíos para verificar la respuesta.")
                    break

                chat_input.click()
                chat_input.fill(MESSAGE_TEXT)
                page.keyboard.press("Enter")

                envios += 1
                print(f"Envío {envios} de {MAX_SENDS} realizado.")

                # Esperar y revisar periódicamente.
                inicio_espera = time.monotonic()

                while time.monotonic() - inicio_espera < INTERVAL_SECONDS:
                    time.sleep(CHECK_FREQUENCY)

                    ids_actuales = set(
                        mensajes_entrantes.evaluate_all(
                            """elementos => elementos
                                .map(el => el.getAttribute('data-testid'))
                                .filter(Boolean)"""
                        )
                    )

                    nuevos = ids_actuales - ids_iniciales

                    if nuevos:
                        print("Se detectó un elemento entrante nuevo.")
                        print("El programa se detendrá.")
                        return

                # No volver a enviar si se alcanzó el límite.
                if envios >= MAX_SENDS:
                    print("Se alcanzó el límite de envíos.")
                    break

            print("Proceso finalizado.")

        except KeyboardInterrupt:
            print("Programa detenido manualmente.")

        except Exception as error:
            print("Ocurrió un error:", error)

        finally:
            print("Cerrando navegador...")
            try:
                browser.close()
            except Exception:
                pass


if __name__ == "__main__":
    run_followup_loop()
