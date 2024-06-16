from sqlalchemy import Column, Integer, Float, Date, Boolean, String, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy_utils import create_database, database_exists
import datetime
import loader
import Post
from sqlalchemy.orm import declarative_base

# Базовый класс для моделей SQLAlchemy
Base = declarative_base()

# Модель "Акция" (Stock)
class Stock(Base):
    __tablename__ = 'stocks'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    begin_date = Column(Date)
    end_date = Column(Date)

    def __init__(self, name, begin_date, end_date):
        self.name = name
        self.begin_date = begin_date
        self.end_date = end_date

    def __repr__(self):
        return f"<Stock(name='{self.name}', begin_date='{self.begin_date}', end_date='{self.end_date}')>"

# Модель "База данных" (Database)
class Database(Base):
    __tablename__ = 'database'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))

    from_date = Column(Date)
    till_date = Column(Date)

    def __init__(self, name, from_date, till_date):
        self.name = name

        self.from_date = from_date
        self.till_date = till_date

    def __repr__(self):
        return f"<Database(name='{self.name}', from_date='{self.from_date}', till_date='{self.till_date}')>"

# Модель "Торги" (Trading)
class Trading(Base):
    __tablename__ = 'tradings'

    id = Column(Integer, primary_key=True)
    name_st = Column(String(100))
    all_period_st = Column(Boolean)
    date = Column(Date)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)

    def __init__(self, name_st, all_period_st, date, open, high, low, close):
        self.name_st = name_st
        self.all_period_st = all_period_st
        self.date = date
        self.open = open
        self.high = high
        self.low = low
        self.close = close

    def __repr__(self):
        return f"<Trading(name_st='{self.name_st}', all_period_st={self.all_period_st}, date='{self.date}', open={self.open}, high={self.high}, low={self.low}, close={self.close})>"

# Загрузка данных о подключении к БД из файла Post.py
user = Post.user
password = Post.password
name_of_db = Post.name
ip = Post.ip
port = Post.port

# Строка подключения к БД
connection_string = f'postgresql+psycopg2://{user}:{password}@{ip}:{port}/{name_of_db}'
engine = create_engine(connection_string, echo=False)  # Включено echo=False

# Создание БД, если она не существует
if database_exists(connection_string):
    print(f'Database exists: {database_exists(engine.url)}')
else:
    create_database(engine.url)
    print(f'Database created: {database_exists(engine.url)}')

# Создание сессии для работы с БД
Session = sessionmaker(bind=engine, autoflush=False)
session = Session(bind=engine, autoflush=False)

# Функция создания таблиц в БД
def create_db():
    Base.metadata.create_all(engine)

# Функция удаления таблиц из БД
def del_t():
    session.commit()
    Trading.__table__.drop(engine, checkfirst=True)
    Database.__table__.drop(engine, checkfirst=True)

# Функция обновления списка акций в БД
def upd_l_stocks():
    stock_data = loader.form_dict_of_stocks()
    for stock_name, dates in stock_data.items():
        session.add(Stock(name=stock_name, begin_date=dates[0], end_date=dates[1]))
        session.commit()

# Функция очистки таблицы "stocks"
def t_stocks():
    session.query(Stock).delete()
    session.commit()

# Функция получения текущего списка акций из БД
def cur_l_stock():
    stock_names = [stock.name for stock in session.query(Stock).all()]
    return stock_names

# Функция получения начальной и конечной даты для заданной акции
def period_end_date(stock_name: str):
    stock = session.query(Stock).filter_by(name=stock_name).first()
    if stock:
        return stock.begin_date, stock.end_date
    else:
        return None, None

# Функция получения текущего списка баз данных из БД
def cur_l_database():
    database_list = []
    for db in session.query(Database).all():
        database_list.append([
            db.id,
            db.name,
            db.all_period,
            db.from_date.isoformat(),
            db.till_date.isoformat()
        ])
    return database_list

# Функция получения текущего словаря торгов из БД
def cur_d_tradings():
    tradings_data = {}
    tradings_data['Date'] = []
    stock_names = []
    for trading in session.query(Trading).all():
        if trading.date not in tradings_data['Date']:
            tradings_data['Date'].append(trading.date)
        if trading.name_st not in stock_names:
            stock_names.append(trading.name_st)
            tradings_data[trading.name_st] = [None] * len(tradings_data['Date'])
        tradings_data[trading.name_st][tradings_data['Date'].index(trading.date)] = trading.close
    session.commit()
    return tradings_data

# Функция расчета прибыли от торгов
def t_profit():
    tradings_data = cur_d_tradings()
    for stock_name, prices in tradings_data.items():
        if stock_name != 'Date':
            for i, price in enumerate(prices):
                if i == 0 or (i > 1 and prices[i - 1] is None and price is not None):
                    first_point = price
                    prices[i] = 0
                else:
                    if price is not None:
                        prices[i] -= first_point
    session.commit()
    return tradings_data

# Функция добавления данных в БД
def add_to_db(name: str, all_period: bool, from_date: datetime.date, to_date: datetime.date):
    print(f"Добавление данных в БД: name={name}, all_period={all_period}, from_date={from_date}, to_date={to_date}")
    stock_data = loader.download_stock(name, from_date, to_date)
    if stock_data[-1] is False:
        return False
    else:
        session.add(Database(name=name, all_period=all_period, from_date=from_date, till_date=to_date))
        session.commit()
        del stock_data[-1]
        addtradings(name, all_period, from_date, to_date)
        return True

# Функция добавления данных о торгах в БД
def addtradings(name: str, all_period: bool, from_date, to_date):
    print(f"Добавление данных о торгах: name={name}, all_period={all_period}, from_date={from_date}, to_date={to_date}")
    stock_data = loader.download_stock(name, from_date, to_date)
    del stock_data[-1]
    for i in range(1, len(stock_data)):
        print(f"Добавление строки торгов: {stock_data[i]}")
        session.add(Trading(
            name_st=name,
            all_period_st=all_period,
            date=stock_data[i][0],
            open=stock_data[i][1],
            high=stock_data[i][2],
            low=stock_data[i][3],
            close=stock_data[i][4]
        ))
        session.commit()

# Функция обновления БД новыми данными
def actualize():
    for db_record in cur_l_database():
        if db_record[2] == 1:
            begin_date, end_date = period_end_date(db_record[1])
            if db_record[4] != str(end_date):
                new_begin_date = datetime.datetime.strptime(db_record[4], "%Y-%m-%d") + datetime.timedelta(days=1)
                addtradings(db_record[1], db_record[2], new_begin_date, end_date)
                db_row = session.query(Database).filter_by(
                    name=db_record[1],
                    all_period=db_record[2],
                    from_date=db_record[3],
                    till_date=db_record[4]
                ).first()
                db_row.till_date = end_date
                session.add(db_row)
                session.commit()




