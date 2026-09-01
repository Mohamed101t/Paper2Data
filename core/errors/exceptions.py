class Paper2DataException(Exception):
    """الاستثناء الرئيسي لجميع أخطاء التطبيق."""
    pass

class DatabaseException(Paper2DataException):
    """يُطلق عند حدوث خطأ في عمليات قاعدة البيانات SQLite."""
    pass

class ValidationException(Paper2DataException):
    """يُطلق عند فشل التحقق من صحة البيانات المدخلة."""
    pass

class NotFoundException(Paper2DataException):
    """يُطلق عند عدم العثور على عنصر مطلوب (مشروع، سجل، أو حقل)."""
    pass