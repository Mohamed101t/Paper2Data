# Paper2Data — العربية

**Paper2Data** هو تطبيق سطح مكتب يعمل دون الحاجة إلى الإنترنت، هدفه تسهيل تحويل الاستبيانات والنماذج الورقية إلى بيانات رقمية منظمة دون الحاجة إلى خبرة متقدمة في Excel أو قواعد البيانات.

> ورق → نموذج إدخال واضح → تحقق من البيانات → Excel / CSV

## ما الذي يقدمه التطبيق؟

- إنشاء مشاريع إدخال بيانات.
- بناء نموذج بدون برمجة.
- نظام مركزي يضم 41 نوع حقل.
- التحقق من صحة القيم قبل الحفظ.
- حفظ البيانات محليًا باستخدام SQLite.
- البحث ومراجعة السجلات وتعديلها وحذفها.
- تصدير ذكي إلى Excel وتصدير CSV.
- حماية النصوص من Spreadsheet Formula Injection أثناء التصدير.
- واجهة عربية RTL حقيقية، مع إبقاء الهاتف والأكواد والأرقام والروابط LTR داخل الحقول المناسبة.
- اللغات: العربية، الإنجليزية، الفرنسية، الروسية، الصينية.
- الوضع الفاتح والداكن.
- اختبارات Unit وIntegration وE2E وGUI E2E وSecurity وPerformance.

## المنصة الحالية

الإصدار الحالي هو **Windows Desktop MVP** باستخدام Python + PySide6. نسخة الموبايل موجودة في خارطة الطريق وليست جزءًا من الإصدار الحالي.

## التشغيل من المصدر

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts\build_translations.py
python main.py
```

## الاختبارات

```powershell
python -m pip install -r requirements_test.txt
python scripts\run_tests.py quick
python scripts\run_tests.py security
python scripts\run_tests.py e2e
python scripts\run_tests.py gui
python scripts\run_tests.py performance
python scripts\run_tests.py full
```

آخر Quality Gate محلي على Windows نجح مع **124 اختبارًا** قبل عملية الحزم.

## بناء نسخة Windows

```powershell
python -m pip install -r requirements_release.txt
powershell -ExecutionPolicy Bypass -File .\scripts\build_windows_release.ps1
```

قد يمنع Windows Smart App Control النسخ المحلية غير الموقعة. لا يجب تعطيل سياسات أمان المؤسسة كحل للنشر؛ النسخة العامة تحتاج مسار توقيع رقمي مناسب.

## الخصوصية

النسخة الحالية Offline-first ولا تحتاج حسابًا سحابيًا. في نسخة Windows المجمدة يتم تخزين البيانات القابلة للكتابة في مجلد بيانات المستخدم المحلي، وليس داخل ملفات البرنامج.

## فلسفة الكود

المشروع يلتزم بمبادئ:

- SRP
- DRY
- KISS
- YAGNI
- Layered Architecture
- Repository Pattern
- فصل UI عن Business Logic
- مكونات قابلة لإعادة الاستخدام واختبارها

للتفاصيل الكاملة راجع [README.md](README.md) والملفات داخل `docs/`.
