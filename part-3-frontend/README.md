# Электронный учебник

## Задача проекта
Разработать веб-сайт, с помощью которого преподаватели курсов могут выкладывать статьи, а студенты — просматривать их и комментировать.

Курс состоит из статей, а статьи — из абзацев текста и изображений. Каждая статья имеет своё название. Статьи можно комментировать.

Для упрощения работы с сайтом есть бот для Telegram.

Возможности веб-сайта:
* Любой человек может просматривать список курсов, список статей курса, статьи и комментарии к ним.
* Любой человек может зарегистрироваться, указав желаемый логин, пароль и электронную почту, и стать пользователем сайта.
* Любой пользователь сайта может создать курс. Создатель курса в рамках курса является преподавателем, а все остальные пользователи — учениками.
* Преподаватель курса может создать новую статью, введя её текст и прикрепив изображения, а также отредактировать текст или изображения ранее созданной.
* Ученики и преподаватель курса могут комментировать статьи.
* Преподаватели могут оставлять комментарии-ответы к комментариям учеников, а также удалять их.
* Ученик может добавить курс в "избранные" и удалить его оттуда. "Избранные" курсы отображаются первыми в списке курсов.
* Любой пользователь сайта может просматривать свой личный кабинет. В личном кабинете отображаются курсы, созданные пользователем, и оставленные им комментарии.
* С помощью личного кабинета любой пользователь может прикрепить свой аккаунт Telegram к аккаунту в электронном учебнике. К аккаунту может быть прикреплён только один аккаунт Telegram.
* Бот Telegram присылает уведомления:
  * Преподавателю, когда кто-то из учеников комментирует статьи на его курсе.
  * Ученикам, когда преподаватель отвечает на их комментарии.
  * Ученикам, когда появляются новые статьи на "избранных" курсах.

## Технологический стек
* [Flask](https://flask.palletsprojects.com/en/2.3.x/) в качестве веб-фреймворка.
* `requirements.txt` и `virtualenv` для управления зависимостями.
* .env-файл для управления конфигурацией.
* SQLite3 в качестве базы данных в процессе разработки, с возможностью замены на MariaDB впоследствии.
* [Flask-Login](https://flask-login.readthedocs.io/en/0.6.2/) для авторизации и аутентификации.
* [Jinja2](https://jinja.palletsprojects.com/en/3.1.x/intro/) для создания HTML-страниц.
* [WTForms](https://wtforms.readthedocs.io/en/3.0.x/) и [Flask-WTF](https://flask-wtf.readthedocs.io/en/1.0.x/) для создания и валидации веб-форм.
* [Bootstrap](https://getbootstrap.ru/) в качестве CSS-фреймворка.
* Постараться обойтись без JavaScript, чтобы не изучать ещё один язык ;)

## Схема работы с базой данных
Данные передаются в объектах, объявленных в модуле `models`, при этом все операции над данными производятся с помощью функций модуля `db`

## Установка и запуск

1. Создайте виртуальное окружение и установите зависимости
```bash
python3 -m virtualenv venv
source venv/bin/activate # Unix
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
```
(или воспользуйтесь PyCharm)

2. Инициализируйте базу данных
```bash
flask --app webapp init-db
```

3. Запустите сервер
```bash
flask --app webapp run
```

При необходимости изменить параметры запуска отредактируйте файл `.env`

## Лицензия
Исходный код проекта доступен по лицензии [Creative Commons-Noncommercial](https://creativecommons.org/licenses/by-nc/4.0/)
