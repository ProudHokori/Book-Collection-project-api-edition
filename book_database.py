import pygsheets as pgs


class BookDatabase:
    def __init__(self, service_file, spreadsheet, worksheet):
        self.google_client = pgs.authorize(service_file=service_file)
        self.spreadsheet_name = spreadsheet
        self.worksheet_name = worksheet
        self.update_sheet(self.spreadsheet_name, self.worksheet_name)
        self.findable_list = ["BookID", "Manga's Name (TH.)",
                              "Manga's Name (ENG.)", "ISBN"]
        self.filterable_list = ["Author", "Publisher", "Category",
                                "Rating", "Status", "Location","Cover"]

    def update_sheet(self, spreadsheet='Book collection demo', worksheet='Sheet1'):
        self.spreadsheet = self.google_client.open(spreadsheet)
        self.worksheet = self.spreadsheet.worksheet_by_title(worksheet)
        self.update_df()

    def update_df(self):
        self.bookdf = self.worksheet.get_as_df()

    def add_book(self, book):
        if not self.get_last_id():
            header = [["BookID", "Manga's Name (TH.)", "Manga's Name (ENG.)",
                       "Author", "Publisher", "ISBN", "Category",
                       "Rating", "Status", "Location", "Cover"]]
            for i in range(1, len(header[0]) + 1):
                self.worksheet.cell((1, i)).color = (204 / 255, 184 / 255, 167 / 255)
            self.worksheet.frozen_rows = 1
            self.worksheet.update_row(index=1, values=header)

        added_cell = self.get_last_id() + 2
        book_values = [[book.id, book.nameTH, book.nameEN,
                        book.author, book.publisher, book.isbn,
                        book.category, book.rating, book.status,
                        book.location, book.cover]]
        self.worksheet.update_row(index=added_cell, values=book_values)
        self.update_df()

    def get_last_id(self):
        self.update_df()
        try:
            last = int(self.bookdf.BookID.iloc[-1])
        except:
            last = 0
        return last

    def edit_book(self, bookID, edited_list):
        edited_cell = int(bookID) + 1
        self.worksheet.update_row(index=edited_cell, values=[edited_list])
        self.update_df()

    def get_a_book(self, bookID):
        return self.bookdf.iloc[int(bookID) - 1]

    def find_book(self, findable, detail):
        # user have to choose findable and input detail return book.
        try:
            book = self.bookdf.iloc[self.bookdf[self.bookdf[findable] == detail].index[0]]
        except:
            book = 0
        return book

    def all_findable_book(self, findable):
        if findable in self.findable_list:
            findable_list = self.bookdf[findable].unique().tolist()
            if '' in findable_list:
                findable_list.remove('')
            if '-' in findable_list:
                findable_list.remove('-')
            return findable_list

    def all_filterable_book(self, filterable):
        if filterable in self.filterable_list:
            filterable_list = self.bookdf[filterable].unique().tolist()
            return filterable_list

    def selected_column(self, selected):
        return self.bookdf[selected]

    def filter_books(self, filterable, detail):
        # return df of filtered books.
        try:
            filtered_bookdf = self.bookdf[self.bookdf[filterable] == detail]
        except:
            filtered_bookdf = 0
        return filtered_bookdf

    def all_col(self):
        # return all books' df.
        return self.bookdf.columns.tolist()


if __name__ == '__main__':
    from book import Book

    bookdb = BookDatabase('keys.json',
                          'My book collection',
                          'Sheet3')
    # book = Book(bookdb, "ทาสรักบรรดาศักดิ์", "Danshaku no Aijin", "Takenaka Sei",
    #             "CN", "978-4-7997-3116-1", "once story", "4.7", "read", "shelved")
    # print(bookdb.bookdf.iloc[bookdb.bookdf.index[bookdb.bookdf['ISBN'] == '978-4-4036-6390-1']])
    print(bookdb.all_col())
