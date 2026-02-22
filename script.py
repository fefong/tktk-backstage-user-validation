import os
import time
import keyboard
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException


# ==============================
# CONFIGURAÇÕES
# ==============================

load_dotenv()

CHROME_PROFILE_PATH = os.getenv("CHROME_PROFILE_PATH")
START_URL = os.getenv("START_URL")
BLACKLIST_FILE = os.getenv("BLACKLIST_FILE")
VERIFIED_FILE = os.getenv("VERIFICATED_FILE")
USERS_SOURCE_FILE = os.getenv("USERS_SOURCE_FILE")

BATCH_SIZE = 30


# ==============================
# UTILITÁRIOS
# ==============================

def load_users_as_set(file_path):
    if not file_path or not os.path.exists(file_path):
        return set()

    with open(file_path, "r", encoding="utf-8") as file:
        return {
            line.strip().replace("@", "")
            for line in file
            if line.strip()
        }


def load_source_users():
    users = []
    seen = set()

    with open(USERS_SOURCE_FILE, "r", encoding="utf-8") as file:
        for line in file:
            username = line.strip().replace("@", "")
            if username and username not in seen:
                seen.add(username)
                users.append(username)

    return users


def append_users_to_file(file_path, users):
    if not users:
        return

    with open(file_path, "a", encoding="utf-8") as file:
        for user in users:
            file.write(user + "\n")


def deduplicate_file(file_path):
    if not file_path or not os.path.exists(file_path):
        return

    print(f"🧹 Removendo duplicados do arquivo: {file_path}")

    unique = []
    seen = set()

    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            user = line.strip().replace("@", "")
            if user and user not in seen:
                seen.add(user)
                unique.append(user)

    with open(file_path, "w", encoding="utf-8") as file:
        for user in unique:
            file.write(user + "\n")

    print(f"✅ Arquivo limpo. Total único: {len(unique)}")


# ==============================
# CAPTCHA
# ==============================

def is_captcha_present(driver):
    try:
        driver.find_element(
            By.XPATH,
            "//span[contains(text(),'Seleciona 2 objetos com a mesma forma')]"
        )
        return True
    except NoSuchElementException:
        return False


def handle_captcha_if_present(driver):
    if is_captcha_present(driver):
        print("🛑 Captcha detectado. Resolva e pressione F8.")
        keyboard.wait("F8")

        while is_captcha_present(driver):
            time.sleep(1)

        print("✅ Captcha resolvido.")


# ==============================
# AÇÕES UI
# ==============================

def click_recruit_creators(wait):
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//span[text()='Recrutar criadores']")
        )
    ).click()


def click_invite_creators(wait):
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//span[text()='Convidar criadores']")
        )
    ).click()


def click_next_button(wait):
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[@data-id='invite-host-next']")
        )
    ).click()


def click_previous_button(wait):
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//span[text()='Anterior']")
        )
    ).click()


def wait_for_textarea(wait):
    wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//textarea[contains(@placeholder,'Insira até 30 criadores')]")
        )
    )



def fill_textarea(wait, driver, users):
    textarea = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//textarea[contains(@placeholder,'Insira até 30 criadores')]")
        )
    )

    # Foca no textarea
    textarea.click()
    time.sleep(0.5)

    # Seleciona tudo e apaga (forma correta para React)
    textarea.send_keys(Keys.CONTROL, "a")
    time.sleep(0.5)
    textarea.send_keys(Keys.DELETE)
    time.sleep(1)

    # Confirma que realmente limpou
    current_value = textarea.get_attribute("value")
    if current_value.strip() != "":
        textarea.clear()
        time.sleep(1)

    # Agora envia apenas os usuários do lote atual
    textarea.send_keys("\n".join(users))
    time.sleep(1)
    textarea = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//textarea[contains(@placeholder,'Insira até 30 criadores')]")
        )
    )

    # Limpeza real
    driver.execute_script("""
        const t = arguments[0];
        t.value = '';
        t.dispatchEvent(new Event('input', { bubbles: true }));
    """, textarea)

    time.sleep(1)
    print()
    print(users)
    print()
    textarea.clear()
    textarea.send_keys("\n".join(users))
    time.sleep(1)


def wait_for_selection_screen(wait):
    wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//span[text()='Selecione os criadores para convidar']")
        )
    )


def analyze_table(driver):
    print("🔎 Verificando tabela de usuários...")

    rows = driver.find_elements(By.XPATH, "//tr[@data-row-key]")

    verified = []
    blocked = []

    for row in rows:
        username = row.get_attribute("data-row-key")
        cols = row.find_elements(By.TAG_NAME, "td")

        if len(cols) < 3:
            continue

        status = cols[1].text.strip()
        invite_type = cols[2].text.strip()

        if status == "Disponível" and invite_type == "Regular":
            verified.append(username)
        else:
            blocked.append(username)

    print(f"➕ Adicionando {len(verified)} criadores à lista de verificados")
    print(f"🚫 Adicionando {len(blocked)} criadores à lista de bloqueados")

    return verified, blocked


# ==============================
# MAIN
# ==============================

def main():

    print("🔄 Iniciando bot...")

    chrome_options = Options()
    chrome_options.add_argument(f"--user-data-dir={CHROME_PROFILE_PATH}")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 30)

    driver.get(START_URL)

    print("⌨️ Pressione F8 para iniciar.")
    keyboard.wait("F8")

    # 🔹 Fluxo inicial
    click_recruit_creators(wait)
    time.sleep(2)

    click_invite_creators(wait)
    time.sleep(3)

    # 🔥 Loop recalculando sempre do arquivo
    while True:

        source_users = load_source_users()
        blacklist = load_users_as_set(BLACKLIST_FILE)
        verified_existing = load_users_as_set(VERIFIED_FILE)

        available_users = [
            u for u in source_users
            if u not in blacklist and u not in verified_existing
        ]

        print(f"📊 Restantes disponíveis: {len(available_users)}")

        if not available_users:
            break

        batch = available_users[:BATCH_SIZE]

        print(f"\n🚀 Processando lote com {len(batch)} usuários")

        wait_for_textarea(wait)
        fill_textarea(wait, driver, batch)

        print("➡️ Clicando Próximo...")
        click_next_button(wait)
        time.sleep(3)

        handle_captcha_if_present(driver)

        print("⏳ Aguardando validação...")
        wait_for_selection_screen(wait)

        verified, blocked = analyze_table(driver)

        append_users_to_file(VERIFIED_FILE, verified)
        append_users_to_file(BLACKLIST_FILE, blocked)

        print("✅ Processamento do lote atual concluído")

        click_previous_button(wait)
        time.sleep(2)

    print("\n🧹 Limpando duplicados finais...")
    deduplicate_file(BLACKLIST_FILE)
    deduplicate_file(VERIFIED_FILE)

    print("🏁 Processamento finalizado com sucesso.")


if __name__ == "__main__":
    main()