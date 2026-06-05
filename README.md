# Telegram Bot: Work Hours Tracker

Цей бот допомагає відстежувати робочі години, зміни та автоматично розраховує нічні години. Дані зберігаються в Google Sheets.

## Функціонал
1. **Щотижневий вибір зміни**: Щонеділі о 20:00 бот запитує зміну на наступний тиждень.
2. **Щоденний збір годин**: Щодня о 20:00 бот запитує кількість відпрацьованих годин.
3. **Автоматичні розрахунки**:
   - Нічні години (якщо зміна №3).
   - Облік польських свят та вихідних (автоматично через бібліотеку `holidays`).
   - Підтримка кодів: `u` (відпустка), `up` (неопл. відпустка), `l4` (лікарняний).
4. **Звіти**: Щоденний короткий звіт та повний звіт в кінці місяця.
5. **Алярм**: Повідомлення при перевищенні 200 годин за місяць.

## Розгортання (Google Cloud Run)

### 1. Підготовка
- Переконайтеся, що файл `tgbotworkhours-f15c0ec0bb4d.json` знаходиться в корені проекту.
- Налаштуйте `.env` (або змінні оточення в Cloud Run):
  - `BOT_TOKEN`: Токен вашого бота.
  - `CHAT_ID`: Ваш ID чату.
  - `WEBHOOK_HOST`: URL вашого сервісу в Cloud Run (після першого розгортання).

### 2. Створення Docker образу та Push
Замініть `PROJECT_ID` на ваш ID проекту Google Cloud.
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/workhours-bot
```

### 3. Розгортання в Cloud Run
```bash
gcloud run deploy workhours-bot \
  --image gcr.io/PROJECT_ID/workhours-bot \
  --platform managed \
  --region europe-central2 \
  --allow-unauthenticated \
  --set-env-vars BOT_TOKEN=...,CHAT_ID=...
```

### 4. Налаштування Cloud Scheduler
Створіть завдання для тригерів:

- **Вибір зміни (Неділя 20:00)**:
  `gcloud scheduler jobs create http ask-shift --schedule="0 20 * * 7" --uri="URL_BOTA/tasks/ask-shift" --location=europe-central2`

- **Збір годин (Щодня 20:00)**:
  `gcloud scheduler jobs create http ask-hours --schedule="0 20 * * *" --uri="URL_BOTA/tasks/ask-hours" --location=europe-central2`

- **Місячний звіт (Останній день місяця 20:00)**:
  `gcloud scheduler jobs create http monthly-report --schedule="0 20 L * *" --uri="URL_BOTA/tasks/report" --location=europe-central2`

*Замініть `URL_BOTA` на реальну адресу сервісу Cloud Run.*

## Структура Google Sheets
Таблиця `tg_bot_work_hour` повинна мати лист `Sheet1` (основна статистика) та `Shifts` (для зберігання вибраних змін). Бот створить їх автоматично, якщо вони відсутні, за умови наявності прав доступу у сервісного акаунту.
