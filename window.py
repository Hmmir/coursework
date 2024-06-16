
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mb
from tkcalendar import DateEntry, Calendar
import pandas as pd
import datetime
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import db_maker as dbm
import random
import os
class StockApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # Window configuration
        self.title("MOEX Stocks Tracker")
        self.configure(background="#3729A3")
        self.geometry("600x350")
        self.resizable(False, False)

        # Create frames
        self.add_stock_frame = tk.Frame(self, bg="#3729A3")
        self.statistics_frame = tk.Frame(self, bg="red")
        self.database_frame = tk.Frame(self)

        # Initialize variables
        self.all_period_var = tk.BooleanVar()
        self.selected_stock = ""
        self.start_date = datetime.datetime.now().date()
        self.end_date = datetime.datetime.now().date()

        # Run the application
        self.run_app()

    def run_app(self):
        # Arrange frames
        self.place_frames()

        # Create widgets for the "Add Stock" frame
        self.create_add_stock_widgets()

        # Create widgets for the "Statistics" frame
        self.create_statistics_widgets()

        # Create widgets for the "Database" frame
        self.create_database_widgets()

    def place_frames(self):
        # Place frames on the window
        self.add_stock_frame.grid(row=0, column=0, sticky='nesw')
        self.statistics_frame.grid(row=0, column=1, sticky='nesw')
        self.database_frame.grid(row=1, column=0, columnspan=2, sticky='nesw')

    def create_add_stock_widgets(self):
        # Get the current list of stocks
        self.stock_list = dbm.cur_l_stoc()

        # Create widgets
        self.stock_combobox = ttk.Combobox(self.add_stock_frame,
                                           values=self.stock_list,
                                           justify=tk.CENTER,
                                           state='readonly')
        self.update_stocks_button = tk.Button(self.add_stock_frame,
                                             text='Update Stocks',
                                             command=self.refresh_stock_list)
        self.all_period_checkbox = tk.Checkbutton(self.add_stock_frame,
                                                text='All period',
                                                variable=self.all_period_var,
                                                command=self.toggle_all_period)
        self.start_date_entry = DateEntry(self.add_stock_frame,
                                          foreground='black',
                                          normalforeground='black',
                                          selectforeground='red',
                                          background='white',
                                          date_pattern='YYYY-mm-dd',
                                          state='readonly')
        self.end_date_entry = DateEntry(self.add_stock_frame,
                                        foreground='black',
                                        normalforeground='black',
                                        selectforeground='red',
                                        background='white',
                                        date_pattern='YYYY-mm-dd',
                                        state='readonly')
        self.add_button = tk.Button(self.add_stock_frame, text='Add', command=self.add_stock)
        self.delete_all_button = tk.Button(self.add_stock_frame, text='Delete All', command=self.delete_all_data)
        self.actualize_button = tk.Button(self.add_stock_frame, text='Actualize', command=self.actualize_data)

        # Style buttons
        for button in [self.add_button, self.delete_all_button, self.actualize_button, self.update_stocks_button]:
            button.configure(activebackground='lightgreen', activeforeground='black')

        # Place widgets
        self.stock_combobox.grid(row=0, column=1, columnspan=2, sticky='w', padx=10, pady=10)
        self.update_stocks_button.grid(row=0, column=2, columnspan=3, padx=10, pady=10, sticky='e')
        self.all_period_checkbox.grid(row=1, column=1, padx=10, pady=10)
        self.start_date_entry.grid(row=1, column=2, padx=10, pady=10)
        self.end_date_entry.grid(row=2, column=2, padx=10, pady=10)
        self.add_button.grid(row=3, column=3, padx=10, pady=10, sticky='w')
        self.delete_all_button.grid(row=3, column=2, padx=10, pady=10)
        self.actualize_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky='e')

        # Bind events
        self.stock_combobox.bind('<<ComboboxSelected>>', self.stock_selected)
        self.start_date_entry.bind('<<DateEntrySelected>>', self.start_date_selected)
        self.end_date_entry.bind('<<DateEntrySelected>>', self.end_date_selected)

    def create_statistics_widgets(self):
        # Buttons for statistics
        self.cost_dynamics_button = tk.Button(self.statistics_frame, text='Cost dynamics', command=self.open_cost_dynamics)
        self.profit_dynamics_button = tk.Button(self.statistics_frame, text='Profit dynamics', command=self.open_profit_dynamics)

        # Place buttons
        self.profit_dynamics_button.grid(row=0, column=0, padx=10, pady=10)
        self.cost_dynamics_button.grid(row=1, column=0, padx=10, pady=10)

        # Style buttons
        for button in [self.cost_dynamics_button, self.profit_dynamics_button]:
            button.configure(activebackground='lightgreen', activeforeground='black')

    def create_database_widgets(self):
        # Create database table
        self.database_list = dbm.cur_l_database()
        self.database_table = ttk.Treeview(self.database_frame, show='headings')
        self.database_table['columns'] = ('Номер', 'Акция', 'С', 'До')
        for column in self.database_table['columns']:
            self.database_table.heading(column, text=column, anchor='center')
            self.database_table.column(column, anchor='center', width=145)
        for row in self.database_list:
            self.database_table.insert('', tk.END, values=row)

        # Add scrollbar
        self.scrollbar = ttk.Scrollbar(self.database_frame, command=self.database_table.yview)
        self.database_table.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tk.RIGHT, fill='y')
        self.database_table.pack(expand=tk.YES, fill='both')

    # --- Event handlers ---

    def stock_selected(self, event):
        self.selected_stock = self.stock_combobox.get()
        self.update_date_range()

    def start_date_selected(self, event):
        self.start_date = self.start_date_entry.get_date()
        self.end_date = self.end_date_entry.get_date()
        self.update_all_period_flag()

    def end_date_selected(self, event):
        self.start_date = self.start_date_entry.get_date()
        self.end_date = self.end_date_entry.get_date()
        self.update_all_period_flag()

    def update_all_period_flag(self):
        if self.start_date == self.begin_end_date[0] and self.end_date == self.begin_end_date[1]:
            self.all_period_var.set(True)
        else:
            self.all_period_var.set(False)

    def toggle_all_period(self):
        if self.all_period_var.get():
            self.start_date_entry.set_date(self.begin_end_date[0])
            self.end_date_entry.set_date(self.begin_end_date[1])
            self.start_date = self.begin_end_date[0]
            self.end_date = self.begin_end_date[1]
        else:
            self.start_date = self.begin_end_date[0] + datetime.timedelta(days=1)
            self.start_date_entry.set_date(self.start_date)

    def update_date_range(self):
        self.begin_end_date = dbm.period_end_date(self.selected_stock)
        if self.all_period_var.get():
            self.start_date_entry.set_date(self.begin_end_date[0])
            self.end_date_entry.set_date(self.begin_end_date[1])
        self.start_date = self.start_date_entry.get_date()
        self.end_date = self.end_date_entry.get_date()

    def refresh_stock_list(self):
        dbm.tab_stocks()
        dbm.upd_l_stocks()
        self.stock_list = dbm.cur_l_stoc()
        self.stock_combobox.configure(values=self.stock_list)

    def add_stock(self):
        if self.selected_stock:
            if self.start_date < self.begin_end_date[0] and self.end_date > self.begin_end_date[1]:
                self.update_date_range()
                self.show_warning()
            elif self.start_date < self.begin_end_date[0]:
                self.update_date_range()
                self.show_warning()
            elif self.end_date > self.begin_end_date[1]:
                self.update_date_range()
                self.show_warning()
            else:
                result = dbm.add_to_db(self.selected_stock,
                                        self.all_period_var.get(),
                                        self.start_date,
                                        self.end_date)
                if not result:
                    mb.showwarning('Warning', 'Stock data was not downloaded')
                else:
                    self.database_list = dbm.cur_l_database()
                    self.database_table.insert('', tk.END, values=self.database_list[-1])
        else:
            mb.showwarning('Warning', 'Select a stock')

    def delete_all_data(self):
        for item in self.database_table.get_children():
            self.database_table.delete(item)
        dbm.del_t()
        dbm.create_db()

    def actualize_data(self):
        pass  # Replace with your data actualization logic

    def show_warning(self):
        warning_message = f"The stock is traded from {self.begin_end_date[0]} to {self.begin_end_date[1]}.\nTo update the information, click 'Update Stocks'."
        mb.showwarning('Attention', warning_message)

    def open_cost_dynamics(self):
        CostDynamicsWindow(self)

    def open_profit_dynamics(self):
        ProfitDynamicsWindow(self)


class ChartWindow(tk.Toplevel):
    def __init__(self, parent, data_type):
        super().__init__(parent)

        if data_type == 0:
            self.title('Cost Dynamics')
            self.data = dbm.cur_d_tradings()
        else:
            self.title('Yield Dynamics')
            self.data = dbm.t_profit()

        self.configure(background='#EBEBEB')
        self.geometry("700x400+0+0")
        self.resizable(False, False)

        self.frame_settings = tk.Frame(self)
        self.frame_graphic = tk.Frame(self)

        self.frame_settings.pack(side='left', fill='y')
        self.frame_graphic.pack(side='right')

        self.create_settings_widgets()
        self.draw_chart()

    def create_settings_widgets(self):
        self.btn_graphic = tk.Button(self.frame_settings, text='Graph', command=self.draw_chart)
        self.btn_excel = tk.Button(self.frame_settings, text='Download to Excel', command=self.download_to_excel)
        self.btn_graphic.grid(row=0, column=0, padx=10, pady=10, sticky='we')
        self.btn_excel.grid(row=1, column=0, padx=10, pady=10, sticky='we')

    def draw_chart(self):
        self.df = pd.DataFrame(self.data)
        fig = plt.Figure(figsize=(5.5, 4), dpi=100)
        ax = fig.add_subplot(111)
        line = FigureCanvasTkAgg(fig, master=self.frame_graphic)
        line.get_tk_widget().grid(row=0, column=0)

        colors = [f'#{random.randint(0, 255):02x}{random.randint(0, 255):02x}{random.randint(0, 255):02x}'
                  for _ in range(len(self.df.axes[1][1:]))]
        # Используйте `color=colors` при первом вызове `self.df.plot`
        self.df.plot(x='Date', y=self.df.axes[1][1:], ax=ax, kind='line', color=colors)
        ax.set_xlabel('Years')
        if self.title == 'Cost Dynamics':
            ax.set_ylabel('Costs')
        else:
            ax.set_ylabel('Yield')

    def download_to_excel(self):
        if not hasattr(self, 'df'):
            mb.showwarning('Attention', 'Click the "Chart" button before downloading the report')
            return

        if self.title == 'Cost Dynamics':
            file_name = "cost.xlsx"
        else:
            file_name = "profit.xlsx"

        self.df.to_excel(file_name)

        progress_bar = ttk.Progressbar(self.frame_settings,
                                       orient='horizontal',
                                       mode='determinate',
                                       maximum=100,
                                       value=0)
        label = tk.Label(self.frame_settings, text='Loading')
        label.grid(row=2, column=0, padx=10, pady=10, sticky='we')
        progress_bar.grid(row=3, column=0, padx=10, pady=10, sticky='we')
        self.update()
        progress_bar['value'] = 0
        self.update()
        while progress_bar['value'] < 100:
            progress_bar['value'] += 5
            self.update()
            time.sleep(0.1)

        # Откройте файл с помощью ОС
        os.startfile(file_name)
class CostDynamicsWindow(ChartWindow):
    def __init__(self, parent):
        super().__init__(parent, 0)

class ProfitDynamicsWindow(ChartWindow):
    def __init__(self, parent):
        super().__init__(parent, 1)

def create_app():
    app = StockApp()
    app.mainloop()