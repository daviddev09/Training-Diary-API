def create_verify_register_html_message(
    name: str, email: str, confirmation_code: str
) -> str:
    html_template = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Подтверждение регистрации</title>
</head>
<body style="margin: 0; padding: 0; background-color: #0d0d0d; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; -webkit-font-smoothing: antialiased;">
    
    <!-- Основной контейнер-подложка -->
    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #0d0d0d; padding: 40px 10px;">
        <tr>
            <td align="center">
                
                <!-- Карточка письма -->
                <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 520px; background-color: #161618; border: 1px solid #2a2a2e; border-radius: 16px; padding: 40px 30px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);">
                    
                    <!-- Шапка / Заголовок -->
                    <tr>
                        <td align="center" style="padding-bottom: 24px;">
                            <h1 style="color: #ffffff; font-size: 22px; font-weight: 700; margin: 0; line-height: 1.4; text-align: center;">
                                <span style="color: #6366f1;">{name}</span>, вы пытаетесь зарегистрироваться на сайте <span style="color: #ffffff;">"training-diary.com"</span>
                            </h1>
                        </td>
                    </tr>

                    <!-- Почта пользователя -->
                    <tr>
                        <td align="center" style="padding-bottom: 28px;">
                            <p style="color: #a1a1aa; font-size: 14px; margin: 0; text-align: center;">
                                Используя почту: <strong style="color: #e4e4e7;">{email}</strong>
                            </p>
                        </td>
                    </tr>

                    <!-- Блок с подтверждающим кодом -->
                    <tr>
                        <td align="center" style="padding: 20px 0 30px 0;">
                            <div style="background-color: #000000; border: 1px solid #3f3f46; border-radius: 12px; padding: 20px 30px; display: inline-block;">
                                <span style="font-family: 'Courier New', Courier, monospace; font-size: 36px; font-weight: 800; color: #ffffff; letter-spacing: 12px; text-shadow: 0 0 12px rgba(255, 255, 255, 0.9), 0 0 20px rgba(255, 255, 255, 0.4); padding-left: 12px;">
                                    {confirmation_code}
                                </span>
                            </div>
                        </td>
                    </tr>

                    <!-- Информационный текст и таймер -->
                    <tr>
                        <td align="center" style="padding-bottom: 32px;">
                            <p style="color: #a1a1aa; font-size: 14px; line-height: 1.6; margin: 0; text-align: center;">
                                Чтобы подтвердить регистрацию, введите этот код на сайте.<br>
                                <span style="color: #ef4444; font-weight: 600;">Код действителен только 60 секунд.</span>
                            </p>
                        </td>
                    </tr>

                    <!-- Разделитель и футер -->
                    <tr>
                        <td align="center" style="border-top: 1px solid #27272a; padding-top: 24px;">
                            <p style="color: #52525b; font-size: 12px; margin: 0; text-align: center;">
                                Если вы не запрашивали этот код, просто проигнорируйте данное письмо.
                            </p>
                        </td>
                    </tr>

                </table>
                
            </td>
        </tr>
    </table>

</body>
</html>"""
    return html_template


def create_diary_pdf_created_notification_html_message(name: str, pdf_link: str) -> str:
    html_message = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ваш дневник тренировок готов</title>
</head>
<body style="margin: 0; padding: 0; background-color: #0d0d0d; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; -webkit-font-smoothing: antialiased;">
    
    <!-- Основной контейнер-подложка -->
    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #0d0d0d; padding: 40px 10px;">
        <tr>
            <td align="center">
                
                <!-- Карточка письма -->
                <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 520px; background-color: #161618; border: 1px solid #2a2a2e; border-radius: 16px; padding: 40px 30px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);">
                    
                    <!-- Шапка / Заголовок -->
                    <tr>
                        <td align="center" style="padding-bottom: 24px;">
                            <h1 style="color: #ffffff; font-size: 22px; font-weight: 700; margin: 0; line-height: 1.4; text-align: center;">
                                <span style="color: #6366f1;">{name}</span>, PDF файл вашего дневника готов!
                            </h1>
                        </td>
                    </tr>

                    <!-- Подзаголовок / Описание -->
                    <tr>
                        <td align="center" style="padding-bottom: 28px;">
                            <p style="color: #a1a1aa; font-size: 14px; margin: 0; text-align: center;">
                                PDF файл вашего дневника с сайта <strong style="color: #ffffff;">"training-diary.com"</strong> готов к скачиванию.
                            </p>
                        </td>
                    </tr>

                    <!-- Блок с иконкой PDF вместо 4-значного кода -->
                    <tr>
                        <td align="center" style="padding: 20px 0 30px 0;">
                            <div style="background-color: #000000; border: 1px solid #3f3f46; border-radius: 12px; padding: 24px 36px; display: inline-block;">
                                <!-- Векторная иконка PDF с эффектом свечения -->
                                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="filter: drop-shadow(0px 0px 12px rgba(255, 255, 255, 0.85)) drop-shadow(0px 0px 20px rgba(99, 102, 241, 0.6)); display: block; margin: 0 auto;">
                                    <path d="M14 2H6C4.89543 2 4 2.89543 4 4V20C4 21.1046 4.89543 22 6 22H18C19.1046 22 20 21.1046 20 20V8L14 2Z" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                                    <path d="M14 2V8H20" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                                    <path d="M10 12H14" stroke="#6366f1" stroke-width="2" stroke-linecap="round"/>
                                    <path d="M10 16H14" stroke="#6366f1" stroke-width="2" stroke-linecap="round"/>
                                </svg>
                            </div>
                        </td>
                    </tr>

                    <!-- Информационный текст и ссылка на скачивание -->
                    <tr>
                        <td align="center" style="padding-bottom: 32px;">
                            <p style="color: #a1a1aa; font-size: 15px; line-height: 1.6; margin: 0 0 16px 0; text-align: center;">
                                Вы можете сохранить документ на свое устройство в любое время:
                            </p>
                            <!-- Синяя ссылка под иконкой -->
                            <a href="{pdf_link}" target="_blank" style="color: #3b82f6; font-size: 16px; font-weight: 700; text-decoration: none; border-bottom: 2px solid #3b82f6; padding-bottom: 2px; display: inline-block;">
                                Нажмите чтобы скачать
                            </a>
                        </td>
                    </tr>

                    <!-- Разделитель и футер -->
                    <tr>
                        <td align="center" style="border-top: 1px solid #27272a; padding-top: 24px;">
                            <p style="color: #52525b; font-size: 12px; margin: 0; text-align: center;">
                                Если вы не запрашивали генерацию PDF, просто проигнорируйте данное письмо.
                            </p>
                        </td>
                    </tr>

                </table>
                
            </td>
        </tr>
    </table>

</body>
</html>"""
    return html_message
