from tkinter import *
from tkinter.ttk import Combobox, Progressbar
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
from webbrowser import open_new
from book_database import BookDatabase
from book import Book
from pandastable import Table
from copy import copy
import pandas as pd
import matplotlib
import seaborn as sns
from threading import Thread
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

matplotlib.use('TkAgg')
pd.options.mode.chained_assignment = None


class BookApp(Tk):
    """ This is the mediator class of each page """

    def __init__(self, *args):
        Tk.__init__(self, *args)
        self.title("Book collection project (API edition)")
        self.frames = {}
        self.app_width = 1280
        self.app_height = 720
        self.init_screen()

    def progress_database(self):
        """ Use to show on screen when loading database"""
        self.bar = Progressbar(self, length=300, mode="indeterminate")
        self.bar.place(relx=0.5, rely=0.72, anchor="center")

        load_pic = PhotoImage(file="picApp/load_pic.png")
        pic = Label(self, image=load_pic)
        pic.img = load_pic
        pic.place(relx=0.5, rely=0.5, anchor="center")

        self.task_thread = Thread(target=self.load_database)
        self.bar.start()
        self.task_thread.start()
        self.after(100, self.check_load_database)

    def check_load_database(self):
        """ Use to check stutus of loading task """
        if self.task_thread.is_alive():
            self.after(100, self.check_load_database)
        else:
            self.bar.stop()
            self.bar.place_forget()
            self.manage_all_page()

    def load_database(self):
        """ Load database on Google sheet """
        service_file = 'keys.json'
        spreadsheet = 'Book collection demo'
        worksheet = 'Sheet1'
        self.database = BookDatabase(service_file, spreadsheet, worksheet)

    def init_screen(self):
        """ Init screen size, position """
        left = int(self.winfo_screenwidth() - self.app_width) // 2
        top = int(self.winfo_screenheight() / 2 - self.app_height / 1.8)
        self.geometry(f"{self.app_width}x{self.app_height}+{left}+{top}")
        self.resizable(False, False)

    def manage_all_page(self):
        """ Use to manage all page in this app """
        container = Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        all_page = (HomePage, ChangeSheetPage,
                    MenuPage, AddBookPage,
                    FindBookPage, EditBookPage,
                    ShowBooksPage, FilterBookPage,
                    BookStatisticPage, AboutAppPage)
        for page in all_page:
            frame = page(container, self)
            self.frames[page] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(HomePage)

    def show_frame(self, page):
        """ Use to raise selected frame to screen """
        frame = self.frames[page]
        frame.tkraise()

    def run(self):
        self.progress_database()
        self.mainloop()


class Page(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.database = controller.database
        self.init_background()
        self.init_command_bar()

    def init_background(self, bg=r"picApp/init_bg.png"):
        bg_img = PhotoImage(file=bg)
        bg = Label(self, image=bg_img)
        bg.img = bg_img
        bg.place(relx=0.5, rely=0.5, anchor='center')

    def init_command_bar(self):

        home_btn = Button(self, text="🏠 Home",
                          command=lambda: self.controller.show_frame(HomePage),
                          **self.button_style('normal'))
        menu_btn = Button(self, text="☰ Menu",
                          command=lambda: self.controller.show_frame(MenuPage),
                          **self.button_style('normal'))
        change_btn = Button(self, text="✎ Change sheet's name",
                            command=lambda: self.controller.show_frame(ChangeSheetPage),
                            **self.button_style('normal'))
        quit_btn = Button(self, text="➜| Quit",
                          command=self.quit,
                          **self.button_style('quit'))

        place_option = {"anchor": "n", "width": 255, "height": 39}
        home_btn.place(relx=0.181, rely=0, **place_option)
        menu_btn.place(relx=0.395, rely=0, **place_option)
        change_btn.place(relx=0.608, rely=0, **place_option)
        quit_btn.place(relx=0.822, rely=0, **place_option)

    def init_reset_btn(self, text, command):
        reload_btn = Button(self, text=text,
                            command=command,
                            **self.button_style('special'))
        reload_btn.place(relx=0.86, rely=1, anchor='s',
                         width=145, height=39)

    def progress_task(self, task):
        """ Use to show on screen when loading database"""
        self.bar = Progressbar(self, length=200, mode="indeterminate")
        self.bar.place(relx=0.175, rely=0.99, anchor="s")
        self.loading_text = ["Loading", "Loading.", "Loading..", "Loading..."]
        self.progress_num = 0
        self.loading = Label(self, text=self.loading_text[self.progress_num],
                             **self.label_style('normal', 14)
                             )
        self.loading.place(relx=0.262, rely=0.957)
        self.task_thread = Thread(target=task)
        self.bar.start()
        self.task_thread.start()
        self.after(200, self.check_load_task)

    def check_load_task(self):
        """ Use to check stutus of loading task """
        if self.task_thread.is_alive():
            self.progress_num += 1
            if self.progress_num == 4:
                self.progress_num = 0
            self.loading.config(text=self.loading_text[self.progress_num],
                                **self.label_style('normal', 14))
            self.after(200, self.check_load_task)
        else:
            self.bar.stop()
            self.bar.place_forget()
            self.loading.place_forget()

    @staticmethod
    def button_style(selected='normal', font_size=16):
        # default style
        font = ('Song Myung', font_size, 'normal')
        bg = "#214F4C"
        fg = "#CCB8A7"
        afg = "#CCB8A7"

        if selected == 'normal':
            bg = "#214F4C"
        elif selected == 'quit':
            bg = "#844943"
        elif selected == 'special':
            bg = "#874F40"
        elif selected == 'clear':
            bg = "#653B30"
        elif selected == 'transparent':
            bg = "#E1CFBC"
            fg = afg = "#3F2320"
            font = ('JetBrains Mono', font_size, 'normal')
        elif selected == 'transparent2':
            bg = "#E1CFBC"
            fg = afg = "#874F40"
            font = ('Song Myung', font_size, 'normal')

        abg = bg
        btn_op = {"borderwidth": 0,
                  "highlightthickness": 0,
                  "relief": "flat",
                  "cursor": "heart",
                  "font": font,
                  "bg": bg,
                  "activebackground": abg,
                  "fg": fg,
                  "activeforeground": afg
                  }
        return btn_op

    @staticmethod
    def entry_style(selected='normal'):
        font = ('Angsana New', 16, 'normal')
        if selected == 'normal':
            font = ('Angsana New', 20, 'normal')

        bg = "#F9F1EF"
        entry_op = {"font": font,
                    "bg": bg,
                    "fg": "#3F2320",
                    "cursor": "xterm",
                    "relief": "flat",
                    "bd": 0,
                    "selectbackground": "#EDD6D0",
                    "selectforeground": "#874F40",
                    "justify": "left"}
        return entry_op

    @staticmethod
    def label_style(style='normal', size=16, shape='normal'):
        font_style = 'Song Myung'
        bg = "#E1CFBC"
        fg = "#214F4C"
        anchor = 'center'
        if style == 'special':
            fg = "#874F40"
        if style == 'formal':
            fg = "#874F40"
            anchor = 'w'
        label_op = {"font": (font_style, size, shape),
                    "bg": bg,
                    "fg": fg,
                    "anchor": anchor}
        return label_op

    @staticmethod
    def combobox_style():
        font = ('Song Myung', 14, 'normal')
        combo_op = {"font": font,
                    "background": "#F9F1EF",
                    "foreground": "#214F4C",
                    "state": 'readonly'}
        return combo_op

    @staticmethod
    def check_button_style():
        font = ('Song Myung', 16, 'normal')
        check_op = {"font": font,
                    "bg": "#E1CFBC",
                    "fg": "#214F4C",
                    "bd": 1,
                    "activebackground": "#E1CFBC",
                    "activeforeground": "#214F4C",
                    "cursor": "hand2",
                    "justify": "left",
                    "padx": 1,
                    "pady": 1,
                    "relief": 'flat',
                    "selectcolor": "#F9F1EF",
                    "anchor": "w"}
        return check_op

    @staticmethod
    def radio_style():
        font = ('Song Myung', 16, 'normal')
        radio_op = {"font": font,
                    "bg": "#E1CFBC",
                    "fg": "#214F4C",
                    "bd": 1,
                    "activebackground": "#E1CFBC",
                    "activeforeground": "#214F4C",
                    "anchor": "w",
                    "cursor": "hand2"}

        return radio_op

    def run(self):
        self.tkraise()


class HomePage(Page):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.init_background(r"picApp/home_bg.png")
        self.init_components()

    def init_components(self):
        about_btn = Button(self, text="❤ About me",
                           command=lambda: self.controller.show_frame(AboutAppPage),
                           **self.button_style('special'))
        menu_btn = Button(self, text="☰ Menu",
                          command=lambda: self.controller.show_frame(MenuPage),
                          **self.button_style('normal'))
        change_btn = Button(self, text="✎ Change sheet's name",
                            command=lambda: self.controller.show_frame(ChangeSheetPage),
                            **self.button_style('normal'))
        quit_btn = Button(self, text="➜| Quit",
                          command=self.quit,
                          **self.button_style('quit'))

        place_option = {"anchor": "n", "width": 255, "height": 39}
        about_btn.place(relx=0.181, rely=0, **place_option)
        menu_btn.place(relx=0.395, rely=0, **place_option)
        change_btn.place(relx=0.608, rely=0, **place_option)
        quit_btn.place(relx=0.822, rely=0, **place_option)

        learn_more = Button(self, text="Tab here to learn more",
                            command=lambda: open_new("https://youtu.be/WovQxGF6CLU"),
                            **self.button_style('transparent', 20))
        learn_more.place(relx=0.5, rely=0.8, anchor='center')


class ChangeSheetPage(Page):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.init_background(r"picApp/change_bg.png")
        self.spread_text = StringVar()
        self.work_text = StringVar()
        self.spread_name = StringVar()
        self.work_name = StringVar()
        self.spread_en = Entry(self)
        self.work_en = Entry(self)
        self.spread_text.set(self.database.spreadsheet_name)
        self.work_text.set(self.database.worksheet_name)
        self.init_components()
        self.init_reset_btn("Reload data",
                            lambda: self.progress_task
                            (self.database.update_df))

    def init_components(self):
        menu_btn = Button(self, text="☰ Menu",
                          command=lambda: self.controller.show_frame(MenuPage),
                          **self.button_style('normal'))
        home_btn = Button(self, text="🏠 Home",
                          command=lambda: self.controller.show_frame(HomePage),
                          **self.button_style('normal'))
        quit_btn = Button(self, text="➜| Quit",
                          command=self.quit,
                          **self.button_style('quit'))

        place_option = {"anchor": "n", "width": 339, "height": 39}
        home_btn.place(relx=0.216, rely=0, **place_option)
        menu_btn.place(relx=0.5, rely=0, **place_option)
        quit_btn.place(relx=0.783, rely=0, **place_option)

        spreadsheet_btn = Button(self, text="Change spreadsheet",
                                 command=lambda: self.progress_task
                                 (self.change_spreadsheet),
                                 **self.button_style('normal'))
        worksheet_btn = Button(self, text="Change worksheet",
                               command=lambda: self.progress_task
                               (self.change_worksheet),
                               **self.button_style('special'))
        self.spread_en.config(textvariable=self.spread_name, **self.entry_style())
        self.work_en.config(textvariable=self.work_name, **self.entry_style())

        place_option1 = {"anchor": "n", "width": 216, "height": 45}
        place_option2 = {"anchor": "n", "width": 310, "height": 30}
        spreadsheet_btn.place(relx=0.837, rely=0.561, **place_option1)
        worksheet_btn.place(relx=0.837, rely=0.648, **place_option1)
        self.spread_en.place(relx=0.612, rely=0.570, **place_option2)
        self.work_en.place(relx=0.612, rely=0.658, **place_option2)

        spread_label = Label(self, textvariable=self.spread_text,
                             **self.label_style('normal', 36, 'bold'))
        work_label = Label(self, textvariable=self.work_text,
                           **self.label_style('special', 30, 'bold'))
        spread_label.place(relx=0.26, rely=0.75, anchor='center')
        work_label.place(relx=0.26, rely=0.85, anchor='center')

    def change_spreadsheet(self):
        try:
            spreadsheet = self.spread_en.get()
            self.database.update_sheet(spreadsheet=spreadsheet)
            self.spread_text.set(spreadsheet)
            self.spread_name.set("")
        except Exception:
            self.spread_name.set("")

    def change_worksheet(self):
        try:
            worksheet = self.work_en.get()
            self.database.update_sheet(worksheet=worksheet)
            self.work_text.set(worksheet)
            self.work_name.set("")
        except Exception:
            self.work_name.set("")


class MenuPage(Page):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.init_background(r"picApp/menu_bg.png")
        self.init_components()

    def init_components(self):
        change_btn = Button(self, text="✎ Change sheet's name",
                            command=lambda: self.controller.show_frame(ChangeSheetPage),
                            **self.button_style('normal'))
        home_btn = Button(self, text="🏠 Home",
                          command=lambda: self.controller.show_frame(HomePage),
                          **self.button_style('normal'))
        quit_btn = Button(self, text="➜| Quit",
                          command=self.quit,
                          **self.button_style('quit'))

        place_option = {"anchor": "n", "width": 339, "height": 39}
        home_btn.place(relx=0.216, rely=0, **place_option)
        change_btn.place(relx=0.5, rely=0, **place_option)
        quit_btn.place(relx=0.783, rely=0, **place_option)

        menu_style = self.button_style('transparent2', 30)
        add_menu = Button(self, text="Add a new book",
                          command=lambda: self.controller.show_frame(AddBookPage),
                          **menu_style)
        find_menu = Button(self, text="Find a book",
                           command=lambda: self.controller.show_frame(FindBookPage),
                           **menu_style)
        filter_menu = Button(self, text="Filter books",
                             command=lambda: self.controller.show_frame(FilterBookPage),
                             **menu_style)
        edit_menu = Button(self, text="Edit book’s detail",
                           command=lambda: self.controller.show_frame(EditBookPage),
                           **menu_style)
        show_menu = Button(self, text="Show all book",
                           command=lambda: self.controller.show_frame(ShowBooksPage),
                           **menu_style)
        statis_menu = Button(self, text="Book’s statistic",
                             command=lambda: self.controller.show_frame(
                                 BookStatisticPage),
                             **menu_style)

        place_option2 = {"anchor": "center", "width": 339, "height": 39}
        add_menu.place(relx=0.242, rely=0.427, **place_option2)
        find_menu.place(relx=0.242, rely=0.624, **place_option2)
        filter_menu.place(relx=0.242, rely=0.820, **place_option2)
        edit_menu.place(relx=0.645, rely=0.427, **place_option2)
        show_menu.place(relx=0.645, rely=0.624, **place_option2)
        statis_menu.place(relx=0.645, rely=0.820, **place_option2)


class AddBookPage(Page):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.init_background(r"picApp/add_book_bg.png")
        self.init_command_bar()
        self.nameTH = Entry(self)
        self.nameEN = Entry(self)
        self.author = Entry(self)
        self.publisher = Entry(self)
        self.isbn = Entry(self)
        self.cover = Entry(self)
        self.category = Entry(self)
        self.rating = Entry(self)
        self.status = Entry(self)
        self.location = Entry(self)
        self.init_components()
        self.default_pic = r"picApp/cover/default_cover.png"
        self.change_pic(self.default_pic)
        self.init_reset_btn('Reset', self.clear)

    def init_components(self):
        confirm_btn = Button(self, text="Confirm",
                             command=lambda: self.progress_task(self.confirm_add_book),
                             **self.button_style('normal'))
        place_op = {"rely": 0.86, "anchor": 'center', "width": 250, "height": 53}
        confirm_btn.place(relx=0.291, **place_op)

        input_style = self.entry_style('normal')
        self.nameTH.config(**input_style)
        self.nameEN.config(**input_style)
        self.author.config(**input_style)
        self.publisher.config(**input_style)
        self.isbn.config(**input_style)
        self.cover.config(**input_style)
        self.category.config(**input_style)
        self.rating.config(**input_style)
        self.status.config(**input_style)
        self.location.config(**input_style)
        check_pic = Button(self, text="Browse",
                           command=self.browse_pic,
                           **self.button_style('normal'))

        place_op2 = {"anchor": 'center', "relx": 0.77, "width": 360, "height": 25}
        self.nameTH.place(rely=0.281, **place_op2)
        self.nameEN.place(rely=0.354, **place_op2)
        self.author.place(rely=0.427, **place_op2)
        self.publisher.place(rely=0.500, **place_op2)
        self.isbn.place(rely=0.574, **place_op2)
        self.cover.place(rely=0.647, relx=0.732,
                         width=260, height=25, anchor='center')
        check_pic.place(rely=0.647, relx=0.885,
                        width=90, height=35, anchor='center')

        place_op3 = {"anchor": 'center', "width": 210, "height": 25}
        self.category.place(relx=0.638, rely=0.77, **place_op3)
        self.rating.place(relx=0.83, rely=0.77, **place_op3)
        self.status.place(relx=0.638, rely=0.879, **place_op3)
        self.location.place(relx=0.83, rely=0.879, **place_op3)

    def clear(self):
        self.nameTH.delete(0, END)
        self.nameEN.delete(0, END)
        self.author.delete(0, END)
        self.publisher.delete(0, END)
        self.isbn.delete(0, END)
        self.cover.delete(0, END)
        self.category.delete(0, END)
        self.rating.delete(0, END)
        self.status.delete(0, END)
        self.location.delete(0, END)
        self.change_pic(self.default_pic)

    def confirm_add_book(self):
        nameTH = self.nameTH.get()
        nameEN = self.nameEN.get()
        author = self.author.get()
        publisher = self.publisher.get()
        isbn = self.isbn.get()
        cover = self.cover.get()
        category = self.category.get()
        rating = self.rating.get()
        status = self.status.get()
        location = self.location.get()
        try:
            cover = cover[cover.index('picApp'):]
        except Exception:
            cover = "picApp/cover/default_cover.png"
        Book(self.database, nameTH, nameEN, author, publisher,
             isbn, category, rating, status, location, cover)
        self.clear()
        self.change_pic(self.default_pic)

    def browse_pic(self):
        filename = askopenfilename(
            filetypes=(("png file", '*.png'), ("All files", "*.*")))
        self.cover.delete(0, END)
        self.cover.insert(END, filename)
        if filename[-3:] == 'png':
            self.change_pic(filename)
        else:
            self.change_pic(self.default_pic)
            self.cover.delete(0, END)

    def change_pic(self, cover=r"picApp/cover/default_cover.png"):
        size = {"width": 533, "height": 356}
        if not cover:
            cover = r"picApp/cover/default_cover.png"
        try:
            cover_pic = PhotoImage(file=cover)
        except EXCEPTION:
            cover_pic = PhotoImage(file=r"picApp/cover/default_cover.png")
        cover_lb = Label(self, image=cover_pic, **size)
        cover_lb.img = cover_pic
        cover_lb.place(relx=0.291, rely=0.515, anchor='center', **size)


class FindBookPage(Page):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.init_background(r"picApp/find_book_bg.png")
        self.init_command_bar()

        # for display book data'
        self.bookid = StringVar()
        self.nameTH = StringVar()
        self.nameEN = StringVar()
        self.author = StringVar()
        self.publisher = StringVar()
        self.isbn = StringVar()
        self.category = StringVar()
        self.rating = StringVar()
        self.status = StringVar()
        self.location = StringVar()
        self.cover = StringVar()
        self.change_pic(r"picApp/cover/default_cover.png")

        # for get a book
        self.findby_box = Combobox(self)
        self.detail_box = Combobox(self)
        self.findby = StringVar()
        self.detail = StringVar()
        self.findby.set(self.database.findable_list[0])
        self.load_findable_book(self.findby.get())
        self.init_components()
        self.init_reset_btn('Reset', lambda: self.progress_task(self.reset))

    def init_components(self):
        self.findby_box.config(textvariable=self.findby,
                               values=self.database.findable_list,
                               **self.combobox_style())
        self.detail_box.config(textvariable=self.detail,
                               **self.combobox_style())
        self.findby.trace("w", lambda *args: self.load_findable_book(self.findby.get()))
        self.detail.trace("w", lambda *args: self.load_book(self.findby.get(),
                                                            self.detail.get()))

        place_op = {"anchor": 'center', "height": 40, "rely": 0.285}
        self.findby_box.place(relx=0.35, width=200, **place_op)
        self.detail_box.place(relx=0.61, width=440, **place_op)

        lb_style = self.label_style('formal', 16, 'normal')
        nameTH_lb = Label(self, textvariable=self.nameTH, **lb_style)
        nameEN_lb = Label(self, textvariable=self.nameEN, **lb_style)
        author_lb = Label(self, textvariable=self.author, **lb_style)
        publisher_lb = Label(self, textvariable=self.publisher, **lb_style)
        isbn_lb = Label(self, textvariable=self.isbn, **lb_style)
        bookid_lb = Label(self, textvariable=self.bookid, **lb_style)
        category_lb = Label(self, textvariable=self.category, **lb_style)
        rating_lb = Label(self, textvariable=self.rating, **lb_style)
        status_lb = Label(self, textvariable=self.status, **lb_style)
        location_lb = Label(self, textvariable=self.location, **lb_style)

        place_op2 = {"anchor": 'center', "width": 345, "height": 30, "relx": 0.79}
        bookid_lb.place(rely=0.40, **place_op2)
        nameTH_lb.place(rely=0.465, **place_op2)
        nameEN_lb.place(rely=0.531, **place_op2)
        author_lb.place(rely=0.595, **place_op2)
        publisher_lb.place(rely=0.660, **place_op2)
        isbn_lb.place(rely=0.725, **place_op2)
        place_op2 = {"anchor": 'center', "width": 120, "height": 30}
        category_lb.place(rely=0.790, relx=0.705, **place_op2)
        rating_lb.place(rely=0.790, relx=0.88, **place_op2)
        status_lb.place(rely=0.856, relx=0.705, **place_op2)
        location_lb.place(rely=0.856, relx=0.88, **place_op2)

    def load_findable_book(self, findby):
        if self.detail.get():
            self.detail.set("")
            self.clear_book()
        all_book = self.database.all_findable_book(findby)
        self.detail_box.config(values=all_book)

    def load_book(self, findable, detail):
        if detail and findable == "BookID":
            detail = int(detail)
        book = self.database.find_book(findable, detail)
        try:
            self.bookid.set(book["BookID"])
            self.nameTH.set(book["Manga's Name (TH.)"])
            self.nameEN.set(book["Manga's Name (ENG.)"])
            self.author.set(book["Author"])
            self.publisher.set(book["Publisher"])
            self.isbn.set(book["ISBN"])
            self.category.set(book["Category"])
            self.rating.set(book["Rating"])
            self.status.set(book["Status"])
            self.location.set(book["Location"])
            self.cover.set(book["Cover"])
            self.change_pic(self.cover.get())
        except Exception:
            self.clear_book()

    def clear_book(self):
        self.bookid.set("")
        self.nameTH.set("")
        self.nameEN.set("")
        self.author.set("")
        self.publisher.set("")
        self.isbn.set("")
        self.category.set("")
        self.rating.set("")
        self.status.set("")
        self.location.set("")
        self.cover.set("")
        self.change_pic(self.cover.get())

    def reset(self):
        self.detail.set("")
        self.findby.set(self.database.findable_list[0])
        self.clear_book()

    def change_pic(self, cover=r"picApp/cover/default_cover.png"):
        size = {"width": 533, "height": 356}
        if not cover:
            cover = r"picApp/cover/default_cover.png"
        try:
            cover_pic = PhotoImage(file=cover)
        except EXCEPTION:
            cover_pic = PhotoImage(file=r"picApp/cover/default_cover.png")
        cover_lb = Label(self, image=cover_pic, **size)
        cover_lb.img = cover_pic
        cover_lb.place(relx=0.31, rely=0.629, anchor='center', **size)


class EditBookPage(Page):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.init_background(r"picApp/edit_book_bg.png")
        self.default_pic = r"picApp/cover/default_cover.png"
        self.init_command_bar()
        self.bookid_box = Combobox(self)
        self.bookid = IntVar()
        self.nameTH = Entry(self)
        self.nameEN = Entry(self)
        self.author = Entry(self)
        self.publisher = Entry(self)
        self.isbn = Entry(self)
        self.cover = Entry(self)
        self.category = Entry(self)
        self.rating = Entry(self)
        self.status = Entry(self)
        self.location = Entry(self)
        self.init_components()
        self.change_pic(self.default_pic)
        self.init_reset_btn('Reset', lambda: self.progress_task(self.reset))

    def init_components(self):
        edit_btn = Button(self, text="Confirm edit",
                          command=lambda: self.progress_task(self.confirm_edit_book),
                          **self.button_style('normal'))

        edit_btn.place(relx=0.294, rely=0.882, anchor='center',
                       width=230, height=45)

        self.bookid_box.config(textvariable=self.bookid,
                               values=self.database.all_findable_book("BookID"),
                               **self.combobox_style())
        self.bookid.trace("w", lambda *args: self.load_book("BookID", self.bookid.get()))

        self.bookid_box.place(relx=0.32, rely=0.272, anchor='center',
                              width=100, height=35)

        input_style = self.entry_style('normal')
        self.nameTH.config(**input_style)
        self.nameEN.config(**input_style)
        self.author.config(**input_style)
        self.publisher.config(**input_style)
        self.isbn.config(**input_style)
        self.cover.config(**input_style)
        self.category.config(**input_style)
        self.rating.config(**input_style)
        self.status.config(**input_style)
        self.location.config(**input_style)
        check_pic = Button(self, text="Browse",
                           command=self.browse_pic,
                           **self.button_style('normal'))

        place_op2 = {"anchor": 'center', "relx": 0.77, "width": 360, "height": 25}
        self.nameTH.place(rely=0.281, **place_op2)
        self.nameEN.place(rely=0.354, **place_op2)
        self.author.place(rely=0.427, **place_op2)
        self.publisher.place(rely=0.500, **place_op2)
        self.isbn.place(rely=0.574, **place_op2)
        self.cover.place(rely=0.647, relx=0.732,
                         width=260, height=25, anchor='center')
        check_pic.place(rely=0.647, relx=0.885,
                        width=90, height=35, anchor='center')

        place_op3 = {"anchor": 'center', "width": 210, "height": 25}
        self.category.place(relx=0.638, rely=0.77, **place_op3)
        self.rating.place(relx=0.83, rely=0.77, **place_op3)
        self.status.place(relx=0.638, rely=0.879, **place_op3)
        self.location.place(relx=0.83, rely=0.879, **place_op3)

    def load_book(self, findable, detail):
        self.clear()
        if detail:
            book = self.database.find_book(findable, detail)
            self.nameTH.insert(0, book["Manga's Name (TH.)"])
            self.nameEN.insert(0, book["Manga's Name (ENG.)"])
            self.author.insert(0, book["Author"])
            self.publisher.insert(0, book["Publisher"])
            self.isbn.insert(0, book["ISBN"])
            self.category.insert(0, book["Category"])
            self.rating.insert(0, book["Rating"])
            self.status.insert(0, book["Status"])
            self.location.insert(0, book["Location"])
            self.cover.insert(0, book["Cover"])
            self.change_pic(self.cover.get())

    def clear(self):
        self.nameTH.delete(0, END)
        self.nameEN.delete(0, END)
        self.author.delete(0, END)
        self.publisher.delete(0, END)
        self.isbn.delete(0, END)
        self.cover.delete(0, END)
        self.category.delete(0, END)
        self.rating.delete(0, END)
        self.status.delete(0, END)
        self.location.delete(0, END)
        self.change_pic(self.default_pic)

    def confirm_edit_book(self):
        if not self.bookid.get():
            messagebox.showwarning(title="Input error",
                                   message="Please selected bookID to edit")
        else:
            nameTH = self.nameTH.get()
            nameEN = self.nameEN.get()
            author = self.author.get()
            publisher = self.publisher.get()
            isbn = self.isbn.get()
            cover = self.cover.get()
            category = self.category.get()
            rating = self.rating.get()
            status = self.status.get()
            location = self.location.get()
            try:
                rating = float(rating)
            except ValueError:
                rating = 0

            try:
                cover = cover[cover.index('picApp'):]
            except:
                cover = "picApp/cover/default_cover.png"
            self.database.edit_book(self.bookid.get(),
                                    [self.bookid.get(), nameTH,
                                     nameEN, author, publisher,
                                     isbn, category, rating,
                                     status, location, cover])
            self.clear()
            self.reset()
            self.change_pic(self.default_pic)

    def browse_pic(self):
        filename = askopenfilename(
            filetypes=(("png file", '*.png'), ("All files", "*.*")))
        self.cover.delete(0, END)
        self.cover.insert(END, filename)
        if filename[-3:] == 'png':
            self.change_pic(filename)
        else:
            self.change_pic(self.default_pic)
            self.cover.delete(0, END)

    def change_pic(self, cover=r"picApp/cover/default_cover.png"):
        size = {"width": 533, "height": 356}
        if not cover:
            cover = r"picApp/cover/default_cover.png"
        try:
            cover_pic = PhotoImage(file=cover)
        except:
            cover_pic = PhotoImage(file=r"picApp/cover/default_cover.png")
        cover_lb = Label(self, image=cover_pic, **size)
        cover_lb.img = cover_pic
        cover_lb.place(relx=0.291, rely=0.576, anchor='center', **size)

    def reset(self):
        self.database.update_df()
        self.bookid_box.config(values=self.database.all_findable_book("BookID"))
        self.bookid.set(0)


class ShowBooksPage(Page):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.init_background(r"picApp/show_books_bg.png")
        self.init_command_bar()
        self.all_col = self.database.all_col()
        self.selected_cols = copy(self.all_col)
        self.nameTH_status = StringVar()
        self.nameEN_status = StringVar()
        self.author_status = StringVar()
        self.publisher_status = StringVar()
        self.isbn_status = StringVar()
        self.category_status = StringVar()
        self.rating_status = StringVar()
        self.status_status = StringVar()
        self.location_status = StringVar()
        self.cover_status = StringVar()
        self.sort_by = StringVar()
        self.sort_to = StringVar()
        self.sortby_box = Combobox(self)

        self.check_nameTH = Checkbutton(self)
        self.check_nameEN = Checkbutton(self)
        self.check_author = Checkbutton(self)
        self.check_publisher = Checkbutton(self)
        self.check_isbn = Checkbutton(self)
        self.check_category = Checkbutton(self)
        self.check_rating = Checkbutton(self)
        self.check_status = Checkbutton(self)
        self.check_location = Checkbutton(self)
        self.check_cover = Checkbutton(self)

        self.atoz = Radiobutton(self)
        self.ztoa = Radiobutton(self)

        self.table_frame = Frame(self)
        self.table = Table(self.table_frame)

        self.all_check_box = [(self.check_nameTH, self.nameTH_status),
                              (self.check_nameEN, self.nameEN_status),
                              (self.check_author, self.author_status),
                              (self.check_publisher, self.publisher_status),
                              (self.check_isbn, self.isbn_status),
                              (self.check_category, self.category_status),
                              (self.check_rating, self.rating_status),
                              (self.check_status, self.status_status),
                              (self.check_location, self.location_status),
                              (self.check_cover, self.cover_status)]
        self.sort_by.set("BookID")
        self.sort_to.set("a")
        self.init_components()
        self.init_table()
        self.init_reset_btn("Reset", lambda: self.progress_task(self.reset))
        self.trace_checkbox()

    def init_components(self):
        check_style = self.check_button_style()
        self.check_nameTH.config(text="Name-TH",
                                 variable=self.nameTH_status,
                                 onvalue="Manga's Name (TH.)",
                                 offvalue="-Manga's Name (TH.)",
                                 **check_style)
        self.check_nameEN.config(text="Name_EN",
                                 variable=self.nameEN_status,
                                 onvalue="Manga's Name (ENG.)",
                                 offvalue="-Manga's Name (ENG.)",
                                 **check_style)
        self.check_author.config(text="Author",
                                 variable=self.author_status,
                                 onvalue="Author",
                                 offvalue="-Author",
                                 **check_style)
        self.check_publisher.config(text="Publisher",
                                    variable=self.publisher_status,
                                    onvalue="Publisher",
                                    offvalue="-Publisher",
                                    **check_style)
        self.check_isbn.config(text="ISBN",
                               variable=self.isbn_status,
                               onvalue="ISBN",
                               offvalue="-ISBN",
                               **check_style)
        self.check_category.config(text="Category",
                                   variable=self.category_status,
                                   onvalue="Category",
                                   offvalue="-Category",
                                   **check_style)
        self.check_rating.config(text="Rating",
                                 variable=self.rating_status,
                                 onvalue="Rating",
                                 offvalue="-Rating",
                                 **check_style)
        self.check_status.config(text="Status",
                                 variable=self.status_status,
                                 onvalue="Status",
                                 offvalue="-Status",
                                 **check_style)
        self.check_location.config(text="Location",
                                   variable=self.location_status,
                                   onvalue="Location",
                                   offvalue="-Location",
                                   **check_style)
        self.check_cover.config(text="Cover",
                                variable=self.cover_status,
                                onvalue="Cover",
                                offvalue="-Cover",
                                **check_style)

        self.check_all_box()

        place_op = {"anchor": "e", "width": 150, "height": 30}
        self.check_nameTH.place(relx=0.76, rely=0.38, **place_op)
        self.check_nameEN.place(relx=0.76, rely=0.44, **place_op)
        self.check_author.place(relx=0.76, rely=0.50, **place_op)
        self.check_publisher.place(relx=0.76, rely=0.56, **place_op)
        self.check_isbn.place(relx=0.76, rely=0.62, **place_op)
        self.check_category.place(relx=0.89, rely=0.38, **place_op)
        self.check_rating.place(relx=0.89, rely=0.44, **place_op)
        self.check_status.place(relx=0.89, rely=0.50, **place_op)
        self.check_location.place(relx=0.89, rely=0.56, **place_op)
        self.check_cover.place(relx=0.89, rely=0.62, **place_op)

        self.sortby_box.config(textvariable=self.sort_by,
                               values=self.selected_cols,
                               **self.combobox_style())
        self.sortby_box.place(relx=0.815, rely=0.756, anchor='center',
                              width=250, height=35)

        self.atoz.config(text="A to Z", value="a",
                         variable=self.sort_to,
                         command=self.update_sort_to,
                         **self.radio_style())
        self.ztoa.config(text="Z to A", value="z",
                         variable=self.sort_to,
                         command=self.update_sort_to,
                         **self.radio_style())

        place_op2 = {"rely": 0.85, "anchor": "e", "width": 150, "height": 30}
        self.atoz.place(relx=0.76, **place_op2)
        self.ztoa.place(relx=0.89, **place_op2)
        self.sort_to.trace("w", lambda *args: self.update_sort_to())
        self.sort_by.trace("w", lambda *args: self.update_table())

    def update_sort_to(self):
        try:
            col = self.sort_by.get()
            index = self.selected_cols.index(col)
            if self.sort_to.get() == "a":
                self.table.sortTable(columnIndex=index, ascending=1)
            if self.sort_to.get() == "z":
                self.table.sortTable(columnIndex=index, ascending=0)
        except ValueError:
            self.reset()

    def reset(self):
        self.sort_to.set("a")
        self.sort_by.set("BookID")
        self.database.update_df()
        self.check_all_box()

    def check_all_box(self):
        for check in self.all_check_box:
            box = check[0]
            status = check[1]
            if "-" in status.get() or not status.get():
                box.select()

    def trace_checkbox(self):
        self.nameTH_status.trace("w",
                                 lambda *args: self.update_df_table(self.nameTH_status))
        self.nameEN_status.trace("w",
                                 lambda *args: self.update_df_table(self.nameEN_status))
        self.author_status.trace("w",
                                 lambda *args: self.update_df_table(self.author_status))
        self.publisher_status.trace("w", lambda *args: self.update_df_table(
            self.publisher_status))
        self.isbn_status.trace("w", lambda *args: self.update_df_table(self.isbn_status))
        self.category_status.trace("w", lambda *args: self.update_df_table(
            self.category_status))
        self.rating_status.trace("w",
                                 lambda *args: self.update_df_table(self.rating_status))
        self.status_status.trace("w",
                                 lambda *args: self.update_df_table(self.status_status))
        self.location_status.trace("w", lambda *args: self.update_df_table(
            self.location_status))
        self.cover_status.trace("w",
                                lambda *args: self.update_df_table(self.cover_status))

    def init_table(self):
        self.table_frame = Frame(self, width=643, height=463)
        self.table_frame.place(relx=0.339, rely=0.575, anchor="center")
        self.show_table(self.database.selected_column(self.all_col))

    def show_table(self, df):
        self.table = Table(self.table_frame, dataframe=df,
                           width=570, height=390,
                           showstatusbar=True)
        self.table.show()

    def update_df_table(self, value):
        val = value.get()
        if '-' not in val:
            self.selected_cols.append(val)
        else:
            if f"{self.sort_by.get()}" == val[1:]:
                self.sort_by.set("BookID")
                self.sort_to.set("a")
            self.selected_cols.remove(val[1:])
        self.selected_cols.sort(key=lambda x: self.all_col.index(x))
        self.update_table()

    def update_table(self):
        df = self.database.selected_column(self.selected_cols)
        self.sortby_box.config(values=self.selected_cols)
        self.show_table(df)
        self.update_sort_to()


class FilterBookPage(Page):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.init_background(r"picApp/filter_book_bg.png")
        self.init_command_bar()
        self.filterby_box = Combobox(self)
        self.detail_box = Combobox(self)
        self.filterby = StringVar()
        self.detail = StringVar()
        self.table_frame = Frame(self)
        self.table = Table(self.table_frame)
        self.detail.set("")
        self.filterby.set("")
        self.init_components()
        self.init_table()
        self.init_reset_btn("Reset", lambda: self.progress_task(self.reset))

    def init_components(self):
        self.filterby_box.config(textvariable=self.filterby,
                                 values=self.database.filterable_list,
                                 **self.combobox_style())
        self.detail_box.config(textvariable=self.detail,
                               **self.combobox_style())
        self.filterby.trace("w",
                            lambda *args: self.load_filterable_book(self.filterby.get()))
        self.detail.trace("w", lambda *args: self.load_table(self.filterby.get(),
                                                             self.detail.get()))

        place_op = {"anchor": 'center', "height": 40, "rely": 0.285}
        self.filterby_box.place(relx=0.41, width=200, **place_op)
        self.detail_box.place(relx=0.61, width=280, **place_op)

    def load_filterable_book(self, filterby):
        if self.detail.get():
            self.detail.set("")
            self.show_table(self.database.bookdf)
        all_detail = self.database.all_filterable_book(filterby)

        self.detail_box.config(values=sorted(all_detail))

    def init_table(self):
        self.table_frame = Frame(self, width=1040, height=390)
        self.table_frame.place(relx=0.5, rely=0.618, anchor="center")
        self.show_table(self.database.bookdf)

    def show_table(self, df):
        self.table = Table(self.table_frame, dataframe=df,
                           width=970, height=320,
                           showstatusbar=True)
        self.table.show()
        self.table.sortTable(columnIndex=0, ascending=1)

    def load_table(self, filterable, detail):
        if detail and filterable == "Rating":
            detail = float(detail)
        df = self.database.filter_books(filterable, detail)
        self.show_table(df)

    def reset(self):
        self.filterby.set('Author')


class BookStatisticPage(Page):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.init_background(r"picApp/book_statistic_bg.png")
        self.graph_box = Combobox(self)
        self.detail_box = Combobox(self)
        self.graph_name_type = ["total number of books", "average of rating"]
        self.plotable_list = ["Publisher", "Category", "Status", "Location"]
        self.graph_name = StringVar()
        self.detail_name = StringVar()
        self.init_graph()
        self.init_command_bar()
        self.init_components()
        self.reset()
        self.init_reset_btn("Reset", self.reset)

    def init_components(self):
        self.graph_box.config(textvariable=self.graph_name,
                              values=self.graph_name_type,
                              **self.combobox_style())
        self.detail_box.config(textvariable=self.detail_name,
                               values=self.plotable_list,
                               **self.combobox_style())

        place_op = {"anchor": 'e', "height": 40, "rely": 0.285}
        self.graph_box.place(relx=0.535, width=290, **place_op)
        self.detail_box.place(relx=0.775, width=200, **place_op)
        self.graph_name.trace("w",
                              lambda *args: self.change_graph_type(self.graph_name.get()))
        self.detail_name.trace("w", lambda *args: self.change_graph_type(
            self.graph_name.get()))

    def change_graph_type(self, graph_name):
        if graph_name == "total number of books":
            self.plot_total_graph(self.detail_name.get())
        elif graph_name == "average of rating":
            self.plot_rating_graph(self.detail_name.get())

    def init_graph(self):
        self.graph_frame = Frame(self, width=560, height=400)
        self.graph_frame.place(relx=0.5, rely=0.626, anchor="center")
        self.fig = Figure()
        self.axes = self.fig.add_subplot()
        self.fig_canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        graph_place = {"anchor": 'center',
                       "width": 560, "height": 400,
                       "rely": 0.5, "relx": 0.5}
        self.fig_canvas.get_tk_widget().place(**graph_place)

    def plot_rating_graph(self, detail):
        self.axes.clear()
        df = self.database.bookdf[['Rating', detail]].groupby(detail).mean()
        sns.set(style="darkgrid")
        sns.set_palette("BrBG_r")
        df.plot.bar(title=f'The graph of average of rating in each '
                          f'{detail.lower()}',
                    ylim=[self.database.bookdf.Rating.min() - 0.3, 5],
                    ax=self.axes)
        self.fig.autofmt_xdate(ha="center", rotation=30)
        self.fig_canvas.draw()

    def plot_total_graph(self, detail):
        self.axes.clear()
        df = self.database.bookdf.groupby(detail).size()
        sns.set()
        sns.set_palette("BrBG_r")
        df.plot(kind='pie',
                title=f'The graph of total number of books in each {detail.lower()}',
                label="",
                autopct=lambda p: f'{p:.2f}%({(p / 100) * df.sum():.0f})',
                ax=self.axes)
        self.fig.autofmt_xdate(rotation=30)
        self.fig_canvas.draw()

    def reset(self):
        self.detail_name.set(self.plotable_list[0])
        self.graph_name.set(self.graph_name_type[-1])


class AboutAppPage(Page):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.init_background(r"picApp/about_me_bg.png")
        self.service_account = "id-book-collection@book-collection-347121.iam.gserviceaccount.com"
        self.init_command_bar()
        self.init_components()

    def init_components(self):
        service_name = Button(self, text="Copy service account!",
                              command=lambda: self.copy_txt(self.service_account),
                              **self.button_style('normal'))
        service_name.place(relx=0.5, rely=0.94, anchor="center",
                           width=255, height=36)

        github_pic = PhotoImage(file=r"picApp/github_icon.png")
        instagram_pic = PhotoImage(file=r"picApp/ig_icon.png")
        youtube_pic = PhotoImage(file=r"picApp/youtube_icon.png")
        github = Button(self, image=github_pic,
                        command=lambda: open_new("https://github.com/ProudHokori"),
                        **self.button_style('transparent'))
        instagram = Button(self, image=instagram_pic,
                           command=lambda: open_new(
                               "https://www.instagram.com/proud_hokori/"),
                           **self.button_style('transparent'))
        youtube = Button(self, image=youtube_pic,
                         command=lambda: open_new(
                             "https://www.youtube.com/channel/UCIg7iklB_TLDZ1C7m5iYS0Q"),
                         **self.button_style('transparent'))
        github.img = github_pic
        instagram.img = instagram_pic
        youtube.img = youtube_pic

        place_op = {"width": 55, "height": 55, "anchor": "center", "rely": 0.85}
        github.place(relx=0.695, **place_op)
        instagram.place(relx=0.75, **place_op)
        youtube.place(relx=0.805, **place_op)

    def copy_txt(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)


if __name__ == '__main__':
    app = BookApp()
    app.run()

