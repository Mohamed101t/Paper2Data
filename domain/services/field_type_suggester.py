import re

from domain.entities.field_type import FieldType


class FieldTypeSuggester:
    """Lightweight deterministic suggestions; no AI or external service required."""

    _RULES = (
        (FieldType.EMAIL, ("email", "e-mail", "بريد", "courriel", "электрон", "邮箱", "邮件")),
        (FieldType.PHONE_NUMBER, ("phone", "mobile", "هاتف", "جوال", "تلفون", "téléphone", "телефон", "手机", "电话")),
        (FieldType.DATE, ("birth date", "date of birth", "تاريخ الميلاد", "تاريخ", "date", "дата", "日期", "生日")),
        (FieldType.TIME, ("time", "وقت", "heure", "время", "时间")),
        (FieldType.CURRENCY, ("salary", "price", "cost", "amount", "راتب", "سعر", "تكلفة", "مبلغ", "salaire", "prix", "зарплат", "цена", "工资", "价格", "金额")),
        (FieldType.PERCENTAGE, ("percentage", "percent", "نسبة", "pourcentage", "процент", "百分比")),
        (FieldType.INTEGER, ("age", "count", "quantity", "children", "عمر", "عدد", "كمية", "âge", "nombre", "возраст", "количество", "年龄", "数量")),
        (FieldType.IDENTIFIER, ("id", "identifier", "record number", "survey number", "رقم الاستبيان", "معرف", "رقم السجل", "identifiant", "идентификатор", "编号", "标识")),
        (FieldType.NATIONAL_ID, ("national id", "national number", "رقم وطني", "الهوية", "identité nationale", "паспорт", "身份证")),
        (FieldType.POSTAL_CODE, ("postal", "zip", "رمز بريدي", "code postal", "почтов", "邮编")),
        (FieldType.URL, ("url", "website", "site", "رابط", "موقع", "сайт", "链接", "网站")),
        (FieldType.COUNTRY, ("country", "دولة", "pays", "страна", "国家")),
        (FieldType.STATE_PROVINCE, ("state", "province", "ولاية", "محافظة", "province", "область", "省")),
        (FieldType.CITY, ("city", "مدينة", "ville", "город", "城市")),
        (FieldType.ADDRESS, ("address", "عنوان", "adresse", "адрес", "地址")),
        (FieldType.RATING, ("rating", "stars", "تقييم", "نجوم", "note", "оценк", "评分")),
        (FieldType.YES_NO, ("yes/no", "yes no", "هل ", "نعم", "non oui", "да нет", "是否")),
    )

    @classmethod
    def suggest(cls, field_name: str) -> str | None:
        normalized = cls._normalize(field_name)
        if not normalized:
            return None
        for field_type, keywords in cls._RULES:
            if any(keyword.casefold() in normalized for keyword in keywords):
                return field_type
        return None

    @staticmethod
    def _normalize(value: str) -> str:
        return re.sub(r"\s+", " ", (value or "").strip().casefold())
