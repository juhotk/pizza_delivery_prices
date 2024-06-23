import pandas as pd
from sqlite3 import connect
import matplotlib.pyplot as plt
import seaborn as sns


def main():
    sqlite_conn = connect("db_pizza.sqlite")
    df_pizza = pd.read_sql(
        sql="""SELECT Restaurant, Price, Time_stamp
               FROM delivery_prices""",
        con=sqlite_conn
    )

    df_pizza['Time_stamp'] = pd.to_datetime(df_pizza['Time_stamp'])
    df_pizza['Hour'] = df_pizza['Time_stamp'].dt.hour
    df_pizza['Weekday'] = df_pizza['Time_stamp'].dt.day_name()

    plot_price_per_hour(df_pizza)
    plot_price_per_weekday(df_pizza)


def plot_price_per_hour(df):
    avg_price_per_hour = df.groupby(['Restaurant', 'Hour']).Price.mean().reset_index()

    plt.figure(figsize=(14, 8))
    sns.lineplot(data=avg_price_per_hour, x='Hour', y='Price', hue='Restaurant', marker='o')
    plt.title('Average Price per Hour')
    plt.xlabel('Hour of the Day')
    plt.ylabel('Average Price')
    plt.xticks(range(11, 21))
    plt.grid(True)
    plt.legend(title='Restaurant')
    plt.show()


def plot_price_per_weekday(df):
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    avg_price_per_weekday = df.groupby(['Restaurant', 'Weekday']).Price.mean().reset_index()
    avg_price_per_weekday['Weekday'] = pd.Categorical(avg_price_per_weekday['Weekday'], categories=days_order, ordered=True)

    plt.figure(figsize=(14, 8))
    sns.lineplot(data=avg_price_per_weekday, x='Weekday', y='Price', hue='Restaurant', marker='o')
    plt.title('Average Price per Weekday')
    plt.xlabel('Weekday')
    plt.ylabel('Average Price')
    plt.grid(True)
    plt.legend(title='Restaurant')
    plt.show()


if __name__ == '__main__':
    main()
