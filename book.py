from book_database import BookDatabase


class Book:
    def __init__(self, database, nameTH, nameEN, author, publisher,
                 isbn, category, rating, status, location,
                 cover=r"picApp/cover/default_cover.png"):
        # book's details
        self.nameTH = nameTH
        self.nameEN = nameEN
        self.author = author
        self.publisher = publisher
        self.isbn = isbn
        self.status = status
        self.category = category
        self.rating = self.check_rating(rating)
        self.location = location
        self.cover = cover

        # own book database
        self.database = database
        self.id = self.manage_id()

        # add self book to database
        self.database.add_book(self)

    def manage_id(self):
        return str(BookDatabase.get_last_id(self.database) + 1).zfill(3)

    @staticmethod
    def check_rating(rating):
        try:
            rating = float(rating)
        except ValueError:
            rating = 0
        return rating


if __name__ == '__main__':
    service_file = 'keys.json'
    spreadsheet = 'My book collection'
    worksheet = 'Sheet1'
    bookdb = BookDatabase(service_file, spreadsheet, worksheet)


    # test add book to sheet
    book = Book(bookdb, "ทาสรักบรรดาศักดิ์", "Danshaku no Aijin", "Takenaka Sei",
                "CN", "978-4-7997-3116-1", "once story", "4.7", "read", "shelved")
    print(bookdb.get_last_id())


