from dataclasses import dataclass


@dataclass
class LanguageTemplate:
    # VerificationErrors
    wrong_email_type: str
    wrong_username_type: str
    wrong_password: str
    email_verify_code_timeout: str
    email_verify_code_wrong: str
    invalid_access_token: str
    invalid_refresh_token: str
    invalid_guest_token: str
    user_refresh_session_empty: str
    refresh_token_time_out: str
    admin_access_error: str
    owner_access_error: str
    unprocessable_content: str
    delete_access_denied: str

    # 404NotFoundErrors
    cache_user_data_not_found: str
    user_not_found: str
    diary_not_found: str
    tr_day_not_found: str
    circuit_not_found: str
    exercise_not_found: str
    weight_not_found: str
    empty_circuit: str
    empty_diary: str

    # LIMITS
    guest_diary_limit: str
    guest_tr_days_limit: str
    guest_circuits_limit: str
    guest_exercises_limit: str
    user_diary_limit: str
    user_tr_days_limit: str
    user_circuits_limit: str
    user_exercises_limit: str
    user_weights_limit: str
    user_exercise_create_limit: str

    # UniqueErrors
    email_is_in_use_error: str
    username_is_in_user_error: str
    exercise_name_is_in_use_error: str

    # Messages
    smtp_register_verify: str
    register_verification_code_sended: str
    diary_pdf_file_creating: str

    # For Frontend
    ff_title: str


RUSSIAN = LanguageTemplate(
    # VerificationErrors
    wrong_email_type="В нашем сервисе можно регистрироваться только по google почте",
    wrong_username_type="Имя пользователя должно начинаться с знака '@'",
    wrong_password="Пароль не совпадает",
    email_verify_code_timeout="Время действия кода подтверждения истёк",
    email_verify_code_wrong="Код подтверждения почты не совпадает, код будет аннулирован!",
    invalid_access_token="Невалидный токен разрешения",
    invalid_refresh_token="Невалидный токен обновления",
    refresh_token_time_out="Срок действия токена обновления истёк! Войдите заново",
    invalid_guest_token="Невалидный гостевой токен",
    user_refresh_session_empty="Возможно вы сделали выход из этого устройства",
    admin_access_error="Ошибка роли! Разрешается только админам!",
    owner_access_error="Ошибка роли! Разрешается только овнеру",
    unprocessable_content="Неверные данные",
    delete_access_denied="Нельзя удалить пользователя чья роль равно или выше вашего!",

    # 404NotFoundErrors
    cache_user_data_not_found="Предоставленные данные невалидны, введите свои данные заново",
    user_not_found="Пользователь не найден",
    diary_not_found="Дневник не найден",
    tr_day_not_found="Тренировочный день не найден",
    circuit_not_found="Цикл тренировки не найден",
    exercise_not_found="Упражнение не найдено",
    weight_not_found="Вес не найден!",
    empty_circuit="Ваш тренировочный круг пуст",
    empty_diary="Ваш дневник пуст, невозможно создать PDF с пустым дневником",

    # LIMITS
    guest_diary_limit="Лимит превышен. Гость может иметь только один дневник! Авторизуйтесь для увеличения лимита",
    guest_tr_days_limit="Лимит превышен. Гость может иметь только 7 тренировочных дней! Авторизуйтесть для увеличения лимита",
    guest_circuits_limit="Лимит превышен. Гость может добавить только 4 круга тренировок в каждый тренировочный день! Авторизуйтесь для увеличения лимита",
    guest_exercises_limit="Лимит превышен. Гость может добавить только 7 упражнений в каждый круг тренировки. Авторизуйтесь для увеличения лимита",
    user_diary_limit="Лимит превышен. Пользователь может иметь только 3 дневников!",
    user_tr_days_limit="Лимит превышен. Пользователь может иметь 90 тренировочных дней в одном дневнике!",
    user_circuits_limit="Лимит превышен. Пользователь может добавлять только 7 кругов тренировок в каждый тренировочный день!",
    user_exercises_limit="Лимит превышен. Пользователь может добавлять только 14 упражнений в каждый круг тренировки!",
    user_exercise_create_limit="Лимит превышен. Пользователь может создать только 10 кастомных упражнений!",
    user_weights_limit="Лимит превышен. Пользователь может иметь только 10 записей веса!",

    # UniqueErrors
    email_is_in_use_error="Эта почта адреса используется, введите адрес своей э-почты!",
    username_is_in_user_error="Это имя пользователя занято. Попробуйте написать что-то другое",
    exercise_name_is_in_use_error="Это имя упражнения уже занято. Придумайте что-то другое",

    # Messages
    smtp_register_verify="Подтверждение регистрации",
    register_verification_code_sended="Код подтверждения регистрации был отправлен на вашу почту, если его нет проверьте ящик спам",
    diary_pdf_file_creating="Генерация PDF файла вашего дневника поставлена в очередь, как только она будет готова мы отправим письмо на вашу почту:",

    # For Frontend
    ff_title="Привет",
)

TURKMEN = LanguageTemplate(
    # VerificationErrors
    wrong_email_type="Biziň saýtymyzda diňe gmail poçta arkaly registrasiýa edip bilersiňiz",
    wrong_username_type="Ulanyjy ady '@' belgi bilen başlanmalydyr",
    wrong_password="Siziň parolyňyz nädogry",
    email_verify_code_timeout="Elektron poçta tassyklama kodynyň wagty doldy",
    email_verify_code_wrong="Girizen e-poçta tassyklama kodyňyz nädogry, kod ýok edildi! Täze kod alyň",
    invalid_access_token="Ygtyýarlylandyryş tokeniňiz nädogry",
    invalid_refresh_token="Täzeleme tokeniňiz nädogry",
    invalid_guest_token="Myhman tokeniňiz nädogry",
    refresh_token_time_out="Täzeleme tokeniňiziň wagty doldy! Täzeden giriş ediň",
    user_refresh_session_empty="Belki siz bu enjamyňyzdan çykyş edendiriňiz",
    admin_access_error="Rolyňyza deň gelmeýär! Diňe admin ulanyja rugsat edilýär!",
    owner_access_error="Rolyňyza deň gelmeýär! Diňe ownera rugsat berilýär",
    unprocessable_content="Ýalňyş maglumat!",
    delete_access_denied="Özüňden roly beýik ýa-da deň ulanyjyny ýok edip bolmaýar",

    # 404NotFoundErrors
    cache_user_data_not_found="Girizen maglumatlaryňyzyň wagty doldy. Maglumatlaryňyzy täzeden giriziň",
    user_not_found="Ulanyjy tapylmady",
    diary_not_found="Gündelik tapylmady",
    tr_day_not_found="Trenirowka güni tapylmady",
    circuit_not_found="Aýlaw tapylmady",
    exercise_not_found="Maşk tapylmady",
    weight_not_found="Agramyňyz tapylmady",
    empty_circuit="Siziň aýlawyňyz boş",
    empty_diary="Sizin gundeliginiz bos, bos gundelikden PDF yasap bolmayar",

    # LIMITS
    guest_diary_limit="Çägiňiz doldy! Myhman ulanyjy diňe 1 sany gündelik saklap biler! Çägiňizi giňeltmek üçin registrasiýa ediň",
    guest_tr_days_limit="Çägiňiz doldy! Myhman ulanyjy gündeligine diňe 7 sany trenirowka güni goşup biler! Çägiňizi giňeltmek üçin registrasiýa ediň",
    guest_circuits_limit="Çagiňiz doldy! Myhman ulanyjy her trenirowka günine diňe 4 sany aýlaw goşup biler! Çägiňizi giňeltmek üçin registrasiýa ediň",
    guest_exercises_limit="Çägiňiz doldy! Myhman ulanyjy her aýlawyna diňe 7 sany maşk goşup biler! Çägiňizi giňeltmek üçin registrasiýa ediň",
    user_diary_limit="Çägiňiz doldy! Ulanyjy diňe 3 sany gündelik saklap biler!",
    user_tr_days_limit="Çägiňiz doldy! Ulanyjy her gündeligine diňe 90 sany trenirowka güni goşup biler!",
    user_circuits_limit="Çägiňiz doldy! Ulanyjy her trenirowka gününe diňe 7 sany aýlaw goşup biler!",
    user_exercises_limit="Çägiňiz doldy! Ulanyjy her aýlawyna diňe 14 sany maşk goşup biler!",
    user_exercise_create_limit="Çägiňiz doldy! Ulanyjy özi tarapyndan diňe 10 sany maşk düzüp biler!",
    user_weights_limit="Çägiňiz doldy! Ulanyjy öz agramy hakynda diňe 10 sany bellik saklap biler!",

    # UniqueErrors
    email_is_in_use_error="Bu e-poçta salgysy ulanyşda. Öz e-poçta salgyňyzy giriziň!",
    username_is_in_user_error="Bu ulanyjy ady eýýäm ulanylýar. Başga ulanyjy ady giriziň",
    exercise_name_is_in_use_error="Bu maşk ady eýýäm ulanyňda. Başga maşk ady giriziň",

    # Messages
    smtp_register_verify="Registrasiya tassyklama",
    register_verification_code_sended="Registrasiya tassyklama kody poctanyza ugradyldy, eger-de ol yok bolsa spamy barlan",
    diary_pdf_file_creating="Sizin gundeliginizin PDF fayl yasalmagy nobata goyuldy, fayl tayyn bolan son biz size poctanyza hat ugradarys. Poctanyz:",
    
    # For Frontend
    ff_title="Salam",
)

LANGUAGES = {"ru": RUSSIAN, "tm": TURKMEN}
