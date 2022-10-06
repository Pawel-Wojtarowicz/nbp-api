import json
import urllib.request
import sqlite3
import datetime
import os
from credentials import access_key, secret_access_key
import boto3


def preapre_db(mydate):
    if os.path.exists("nbp.db"):
        while True:
            db = sqlite3.connect("nbp.db")
            cursor = db.cursor()
            cursor.execute(f"drop table if exists [{str(mydate)}]")
            cursor.execute(
                f'Create Table if not exists [{str(mydate)}] (currency string, code string, mid float)')
            url = (
                f"http://api.nbp.pl/api/exchangerates/tables/A/{str(mydate)}/?format=json")
            try:
                response = urllib.request.urlopen(url).read().decode()
                break
            except urllib.error.HTTPError as e:
                print(f"{e}\nThere is no rates from {mydate} checking day before.")
                mydate = datetime.datetime.strptime(
                    str(mydate), "%Y-%m-%d").date()
                mydate = (mydate - datetime.timedelta(1))
                continue
            except urllib.error.URLError as e:
                print(e,"\nI'm trying again.")
                continue
            except Exception as e:
                print(e,"\nI'm trying again.")
                continue

        response = urllib.request.urlopen(url).read().decode()
        my_data = json.loads(response)

        for i in my_data[0]['rates']:
            cursor.execute(f"Insert into [{str(mydate)}] values (?, ?, ?)",
                           (i['currency'], i['code'], i['mid']))

            db.commit()
        db.close()
    else:
        while True:
            db = sqlite3.connect("nbp.db")
            cursor = db.cursor()
            cursor.execute(f"drop table if exists [{str(mydate)}]")
            cursor.execute(
                f'Create Table if not exists [{str(mydate)}] (currency string, code string, mid float)')
            url = (
                f"http://api.nbp.pl/api/exchangerates/tables/A/?format=json")
            try:
                response = urllib.request.urlopen(url).read().decode()
                break
            except urllib.error.HTTPError as e:
                print(f"{e}, There is no rates from {mydate} checking day before.")
                mydate = datetime.datetime.strptime(
                    str(mydate), "%Y-%m-%d").date()
                mydate = (mydate - datetime.timedelta(1))
                continue
            except urllib.error.URLError as e:
                print(e,"\nI'm trying again.")
                continue
            except Exception as e:
                print(e,"\nI'm trying again.")
                continue

        response = urllib.request.urlopen(url).read().decode()
        my_data = json.loads(response)

        for i in my_data[0]['rates']:
            cursor.execute(f"Insert into [{str(mydate)}] values (?, ?, ?)",
                           (i['currency'], i['code'], i['mid']))

            db.commit()

    return mydate


def rate_check(from_currency, to_currency, mydate):
    db = sqlite3.connect('nbp.db')
    if from_currency == "PLN":
        from_currency = 1
    else:
        cursor = db.execute(
            f"select mid from [{mydate}] where code = '{from_currency}'")
        results = cursor.fetchall()
        for result in results:
            from_currency = result[0]

    if to_currency == "PLN":
        to_currency = 1
    else:
        cursor = db.execute(
            f"select mid from [{mydate}] where code = '{to_currency}'")
        results = cursor.fetchall()
        for result in results:
            to_currency = result[0]

    db.close()
    return from_currency, to_currency


def user_inputs():
    while True:
        try:
            amount = float(
                input("Enter the amount to be exchanged: ").replace(",", "."))
            if amount > 0:
                break
            else:
                print("Amount must be grater then 0")
        except ValueError:
            print("Please enter a number")

    while True:
        currencies = ["THB", "USD", "AUD", "HKD", "CAD", "NZD", "SGD", "EUR", "HUF", "CHF", "GBP", "UAH", "JPY", "CZK",
                      "DKK", "ISK", "NOK", "SEK", "HRK", "RON", "BGN", "TRY", "ILS", "CLP", "PHP", "MXN", "ZAR", "BRL", "MYR", "IDR", "INR", "KRW", "CNY", "XDR"]
        from_currency = input(
            "Enter 1st currency you would like to convert to: ").upper().strip()
        to_currency = input(
            "Enter 2nd currency you would like to convert to: ").upper().strip()
        if from_currency not in currencies and from_currency != str("PLN") or to_currency not in currencies and to_currency != str("PLN"):
            print("---" * 10)
            print("Provided currencies: ", from_currency, to_currency)
            print(
                f"At least one currency not exist, please try again. Choose from the list below: \n{currencies}")

        else:
            while True:
                mydate = str(
                    input("Which day's currency exchange rate? (YYYY-MM-DD): "))
                format = "%Y-%m-%d"

                try:
                    datetime.datetime.strptime(mydate, format)
                    mydate = preapre_db(mydate)
                    break
                except ValueError:
                    print(
                        "This is the incorrect date string format. It should be YYYY-MM-DD")
            break
    return amount, from_currency, to_currency, mydate


def calculate_the_exchange_rate(amount, from_currency_rate, to_currency_rate):
    result = 0
    if from_currency_rate == 1 and to_currency_rate == 1:
        result = amount * 1
    if from_currency_rate == 1 and to_currency_rate != 1:
        result = amount / to_currency_rate
    if from_currency_rate != 1 and to_currency_rate == 1:
        result = amount * from_currency_rate
    if from_currency_rate != 1 and to_currency_rate != 1:
        result = (from_currency_rate / to_currency_rate) * amount

    result = float("{:.2f}".format(result))
    return result


def export_to_json(from_currency_rate, to_currency_rate, amount, from_currency, calculated_amount, to_currency, mydate):

    mydict = {
        "Amounty: ": amount,
        "Input currency: ": from_currency,
        "Input currency rate: ": from_currency_rate,
        "Calculated amount: ": calculated_amount,
        "Output currency: ": to_currency,
        "Output currency rate: ": to_currency_rate,
        "date of the currency exchange rate: ": str(mydate),
    }
    if os.path.exists("result.json"):
        listObj = []
        with open('result.json') as file:
            listObj = json.load(file)
        listObj.append(mydict)
        with open("result.json", "r+") as jsonFile:
            json.dump(listObj, jsonFile)
    else:
        listObj = []
        with open("result.json", "w") as jsonFile:
            listObj.append(mydict)
            json.dump(listObj, jsonFile)


def export_to_s3():
    client = boto3.client('s3', aws_access_key_id=access_key,
                          aws_secret_access_key=secret_access_key)

    for file in os.listdir():
        if '.json' in file:
            upload_file_bucket = "recruitment.pe47vgtcan"
            upload_file_key = file
            try:
                client.upload_file(file, upload_file_bucket, upload_file_key)
            except Exception as e:
                print(e)
                
    s3 = boto3.resource('s3', aws_access_key_id=access_key,
                          aws_secret_access_key=secret_access_key)

    my_bucket = s3.Bucket('recruitment.pe47vgtcan')
    for my_bucket_object in my_bucket.objects.all():
        if my_bucket_object.key != "result.json":
            pass
        else:
            print("The file has been uploaded to AWS Bucket")

def main():
    preapre_db(datetime.date.today())
    amount, from_currency, to_currency, mydate = user_inputs()
    from_currency_rate, to_currency_rate = rate_check(
        from_currency, to_currency, mydate)
    calculated_amount = calculate_the_exchange_rate(
        amount, from_currency_rate, to_currency_rate)

    print(
        f"Result: For {amount} {from_currency}(s) you can buy: {calculated_amount:.2f} {to_currency}(s) at the exchange rate of: {mydate}")

    export_to_json(from_currency_rate, to_currency_rate, amount,
                   from_currency, calculated_amount, to_currency, mydate)
    export_to_s3()


if __name__ == '__main__':
    main()
