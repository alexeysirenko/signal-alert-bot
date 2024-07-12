Додати свій номер в конфіг
docker build -t my_signal_app .
docker run -it --name my_signal_container my_signal_app
Підключитись до контейнера, запустити скрипт send_signal_message.py і зареєструватись в signal