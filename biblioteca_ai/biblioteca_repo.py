from db import get_connection


def sp_get_users():
    with get_connection() as cn:
        cur = cn.cursor()
        cur.execute("EXEC dbo.SP_GetUsers")
        return cur.fetchall()


def sp_count_books_by_category(category_name: str):
    with get_connection() as cn:
        cur = cn.cursor()
        cur.execute("EXEC dbo.SP_CountBooksByCategory @CategoryName = ?", (category_name,))
        return cur.fetchall()


def sp_top_authors_by_loans_month(year: int, month: int):
    with get_connection() as cn:
        cur = cn.cursor()
        cur.execute("EXEC dbo.SP_TopAuthorsByLoans @Year = ?, @Month = ?", (year, month))
        return cur.fetchall()


def sp_overdue_loans(as_of_date=None):
    with get_connection() as cn:
        cur = cn.cursor()
        if as_of_date:
            cur.execute("EXEC dbo.SP_OverdueLoans @AsOfDate = ?", (as_of_date,))
        else:
            cur.execute("EXEC dbo.SP_OverdueLoans")
        return cur.fetchall()