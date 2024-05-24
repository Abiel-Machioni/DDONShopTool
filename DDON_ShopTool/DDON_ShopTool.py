import tkinter as tk
from tkinter import *
from tkinter import messagebox
import tkinter.ttk as ttk
from tkinter.ttk import *
import json
import os
import csv
import configparser

#Check required files exist
def check_file_exists(filename, content):
    if not os.path.isfile(filename):
        with open(filename, 'w', newline='') as file:
            if filename.endswith('.csv'):
                writer = csv.writer(file)
                writer.writerow(content)
            else:
                json.dump(content, file)

check_file_exists('ShopPrice.csv', ['ItemId', 'Price'])
check_file_exists('Shop.json', [])

#Read shop data from Shop.json
def load_shop_data():
    shop_data = []
    if os.path.isfile('Shop.json') and os.path.getsize('Shop.json') > 0:
        with open('Shop.json', 'r') as file:
            shop_data = json.load(file)
    return shop_data

#Load shop data on startup
shop_data = load_shop_data()


#Reload shop data
def reload_shop_data():
    global shop_data
    shop_data = load_shop_data()

#Read item prices from CSV
def read_prices_from_csv(filename, item_id_column, price_column):
    prices = {}
    if os.path.isfile(filename):
        with open(filename, 'r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    item_id = int(row.get(item_id_column, ''))
                    price = int(row.get(price_column, 0))
                    if item_id != '':
                        prices[item_id] = price
                except ValueError:
                    pass
    return prices

#Retrieve price from CSV
def get_price(item_id, filename, item_id_column, price_column):
    prices = read_prices_from_csv(filename, item_id_column, price_column)
    return prices.get(item_id, 0)

#Export data from JSON to CSV
def export_json_to_csv():
    reload_shop_data()

    check_file_exists('ShopPrice.csv', ['ItemId', 'Price'])
    existing_item_prices = read_prices_from_csv('ShopPrice.csv', 'ItemId', 'Price')
    updated_items = set()
    
    for shop in shop_data:
        for item in shop['Data']['GoodsParamList']:
            item_id = item['ItemId']
            price = item['Price']
            if item_id not in updated_items:
                existing_item_prices[item_id] = price
                updated_items.add(item_id)
    
    with open('ShopPrice.csv', 'w', newline='') as csvfile:
        fieldnames = ['ItemId', 'Price']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for item_id, price in existing_item_prices.items():
            writer.writerow({'ItemId': item_id, 'Price': price})

#Update the Shop.json file
def update_json():
    with open('Shop.json', 'w') as file:
        json.dump(shop_data, file, indent=4)

#Add item and update index as necessary
def add_item():
    reload_shop_data()

    item_id = int(entry_item_id.get())
    user_price = entry_price.get()
    price = int(user_price) if user_price else 0
    stock = int(entry_stock.get()) if entry_stock.get() else 255
    shop_id = int(entry_shop_id.get())
    wallet_type = int(entry_wallet_type.get()) if entry_wallet_type.get() else 0
    insert_index = entry_insert_index.get() if entry_insert_index.get() else None
    insert_index = int(insert_index) if insert_index else None

    existing_shop_data = next((shop for shop in shop_data if shop["ShopId"] == shop_id), None)
    if not existing_shop_data:
        existing_shop_data = {
            "ShopId": shop_id, 
            "Data": {"Unk0": 0, "Unk1": 0, "WalletType": wallet_type, "GoodsParamList": []}
        }
        shop_data.append(existing_shop_data)
    
    item = {
        "Index": insert_index, 
        "ItemId": item_id, 
        "Price": price, 
        "Stock": stock, 
        "Unk4": False, 
        "Unk5": 0, 
        "Unk6": 0, 
        "Unk7": []
    }
    
    goods_list = existing_shop_data["Data"]["GoodsParamList"]
    if insert_index is None:
        item["Index"] = len(goods_list)
        goods_list.append(item)
    else:
        goods_list.insert(insert_index, item)
        for i in range(insert_index, len(goods_list)):
            goods_list[i]["Index"] = i
    
    update_json()

#Update specific fields of an item or a shop
def update_item_or_shop():
    reload_shop_data()

    shop_id = int(entry_update_shop_id.get()) if entry_update_shop_id.get() else None
    new_shop_id = int(entry_update_new_shop_id.get()) if entry_update_new_shop_id.get() else None
    wallet_type = int(entry_update_wallet_type.get()) if entry_update_wallet_type.get() else None
    item_id = int(entry_update_item_id.get()) if entry_update_item_id.get() else None
    new_item_id = int(entry_update_new_item_id.get()) if entry_update_new_item_id.get() else None
    price = int(entry_update_price.get()) if entry_update_price.get() else None
    stock = int(entry_update_stock.get()) if entry_update_stock.get() else None
    index = int(entry_update_index.get()) if entry_update_index.get() else None

    shop = next((shop for shop in shop_data if shop["ShopId"] == shop_id), None)
    if shop:
        if new_shop_id is not None:
            shop["ShopId"] = new_shop_id
        if wallet_type is not None:
            shop["Data"]["WalletType"] = wallet_type
        if item_id is not None:
            for item in shop["Data"]["GoodsParamList"]:
                if item["ItemId"] == item_id:
                    if new_item_id is not None:
                        item["ItemId"] = new_item_id
                    if price is not None:
                        item["Price"] = price
                    if stock is not None:
                        item["Stock"] = stock
                    if index is not None:
                        goods_list = shop["Data"]["GoodsParamList"]
                        if 0 <= index < len(goods_list):
                            old_index = goods_list.index(item)
                            goods_list.insert(index, goods_list.pop(old_index))
                            for i, item in enumerate(goods_list):
                                item["Index"] = i
    
    update_json()

#Remove item or shop
def remove_item_or_shop():
    reload_shop_data()

    shop_id = int(entry_update_shop_id.get()) if entry_update_shop_id.get() else None
    item_id = int(entry_update_item_id.get()) if entry_update_item_id.get() else None

    if checkbox_state.get() or messagebox.askyesno("Confirmation", get_confirmation_message(shop_id, item_id)):
        if shop_id is not None:
            if item_id is not None:
                for shop in shop_data:
                    if shop["ShopId"] == shop_id:
                        shop["Data"]["GoodsParamList"] = [item for item in shop["Data"]["GoodsParamList"] if item["ItemId"] != item_id]
                        for index, item in enumerate(shop["Data"]["GoodsParamList"]):
                            item["Index"] = index
                        break
            else:
                shop_data[:] = [shop for shop in shop_data if shop["ShopId"] != shop_id]

        update_json()

def get_confirmation_message(shop_id, item_id):
    if item_id is not None:
        return f"Are you sure you want to remove item {item_id} from shop {shop_id}?"
    elif shop_id is not None:
        return f"Are you sure you want to remove shop {shop_id}?"
    else:
        return "Are you sure you want to remove?"

#Update suggested and sell price dynamically
def update_prices(*args):
    reload_shop_data()

    item_id = entry_item_id.get()
    if item_id.isdigit():
        item_id = int(item_id)
        suggested_price = get_price(item_id, 'ShopPrice.csv', 'ItemId', 'Price')
        sell_price = get_price(item_id, 'itemlist.csv', '#ItemId', 'Price')
        entry_suggested_price.config(text=str(suggested_price))
        entry_sell_price.config(text=str(sell_price))
        entry_price.delete(0, tk.END)
        entry_price.insert(0, str(suggested_price) if suggested_price != 0 else "")
    else:
        entry_suggested_price.config(text="Invalid Item ID")
        entry_sell_price.config(text="Invalid Item ID")
        entry_price.delete(0, tk.END)

#Tkinter Main Window and coordinates to open the tool center screen
root = Tk()
root.title("DDON_ShopTool")
root.configure(bg='#373737')
root.update_idletasks()
root.minsize(root.winfo_width(), root.winfo_height())
x_cordinate = int((root.winfo_screenwidth() / 2) - (root.winfo_width() / 2))
y_cordinate = int((root.winfo_screenheight() / 2) - (root.winfo_height() / 2))
root.geometry("+{}+{}".format(x_cordinate-150, y_cordinate-150))
root.resizable(False, False)
root.update()

#Save the state of the checkbox
checkbox_state = tk.BooleanVar()
def on_checkbox_change():
    save_checkbox_state(checkbox_state.get())

#Notebook and frames
notebook = ttk.Notebook(root, width=330, height=341)
notebook.grid(row=0, column=0, padx=1, pady=1, sticky='nsew')

frame_add = ttk.Frame(notebook, padding=(10, 10))
frame_update = ttk.Frame(notebook, padding=(10, 10))
frame_buttons = ttk.Frame(notebook, padding=(10, 10))
frame_add_unk7 = ttk.Frame(notebook, padding=(10, 10))
frame_update_unk7 = ttk.Frame(notebook, padding=(10, 10))

notebook.add(frame_add, text="Add Item")
notebook.add(frame_update, text="Update Item/Shop")
notebook.add(frame_add_unk7, text="Add Unk7")
notebook.add(frame_update_unk7, text="Update Unk7")

#Set theme and style
style = ttk.Style()
style.theme_use('clam')
style.configure('.', background='#2e2e2e', foreground='#ffffff', fieldbackground='#434343', focuscolor=[('#2e2e2e', '#2e2e2e')])
style.configure('TNotebook', background='darkgrey', tabmargins=[0, -1, 0, 0], borderwidth=0)
style.configure('TNotebook.Tab', background='#343434', foreground='white', padding=[7, 7], focuscolor=[('#2e2e2e', '#2e2e2e')])
style.configure('TButton', background = '#2e2e2e')
style.map('TButton', background=[('active', '#515151')])
style.map('TCheckbutton', background=[('active', '#2e2e2e')])
style.map('TNotebook.Tab', background=[('active', '#515151'), ('selected', '#2e2e2e')], expand=[('selected', [0, 7, 5, -1])])
font_style = ('Helvetica', 9)

#Labels and Entry fields for Adding Items
labels_add = ["Shop ID:", "Wallet Type:", "Item ID:", "Price:", "Sell Price:", "Suggested Price:", "Stock:", "Choose Index (optional):"]
entries_add = []
for idx, label in enumerate(labels_add):
    ttk.Label(frame_add, text=label, font=font_style, justify='center').grid(row=idx, column=0, padx=5, pady=5, sticky='w')

entry_shop_id = ttk.Entry(frame_add, font=font_style, width=20, justify='center')
entry_wallet_type = ttk.Entry(frame_add, font=font_style, width=20, justify='center')
entry_item_id = ttk.Entry(frame_add, font=font_style, width=20, justify='center')
entry_price = ttk.Entry(frame_add, font=font_style, width=20, justify='center')
entry_sell_price = ttk.Label(frame_add, font=font_style, width=20, anchor='center')
entry_suggested_price = ttk.Label(frame_add, font=font_style, width=20, anchor='center')
entry_stock = ttk.Entry(frame_add, font=font_style, width=20, justify='center')
entry_insert_index = ttk.Entry(frame_add, font=font_style, width=20, justify='center')

entries_add = [entry_shop_id, entry_wallet_type, entry_item_id, entry_price, entry_sell_price, entry_suggested_price, entry_stock, entry_insert_index]
for idx, entry in enumerate(entries_add):
    entry.grid(row=idx, column=1, padx=(16, 5), pady=(4, 4), ipadx=0, ipady=0, sticky='w')

entry_item_id.bind("<KeyRelease>", update_prices)

#Labels and Entry fields for Updating Items/Shops
labels_update = ["Shop ID:", "New Shop ID:", "New Wallet Type:", "Item ID:", "New Item ID:", "New Price:", "New Stock:", "New Index:"]
entries_update = []
for idx, label in enumerate(labels_update):
    ttk.Label(frame_update, text=label, font=font_style, justify='center').grid(row=idx, column=0, columnspan=1, padx=5, pady=5, sticky='w')

entry_update_shop_id = ttk.Entry(frame_update, font=font_style, width=20, justify='center')
entry_update_new_shop_id = ttk.Entry(frame_update, font=font_style, width=20, justify='center')
entry_update_wallet_type = ttk.Entry(frame_update, font=font_style, width=20, justify='center')
entry_update_item_id = ttk.Entry(frame_update, font=font_style, width=20, justify='center')
entry_update_new_item_id = ttk.Entry(frame_update, font=font_style, width=20, justify='center')
entry_update_price = ttk.Entry(frame_update, font=font_style, width=20, justify='center')
entry_update_stock = ttk.Entry(frame_update, font=font_style, width=20, justify='center')
entry_update_index = ttk.Entry(frame_update, font=font_style, width=20, justify='center')

entries_update = [entry_update_shop_id, entry_update_new_shop_id, entry_update_wallet_type, entry_update_item_id, entry_update_new_item_id, entry_update_price, entry_update_stock, entry_update_index]
for idx, entry in enumerate(entries_update):
    entry.grid(row=idx, column=1, padx=(29, 16), pady=(4, 4), sticky='n')

#Divide labels and entries into two columns for Adding Unk7 Params
labels_add_unk7 = ["Shop ID:", "Item ID:", "Unk0:", "Unk1:", "Unk2:", "Unk3:", "Unk4:", "Unk5:", "Unk6:", "Unk7:", "Unk8:", "Unk9:", "Unk10:", "Unk11:"]
entries_add_unk7 = [ttk.Entry(frame_add_unk7, font=font_style, width=14, justify='center') for _ in range(len(labels_add_unk7))]

for idx, (label, entry) in enumerate(zip(labels_add_unk7, entries_add_unk7)):
    col = idx // 7
    row = idx % 7
    if col == 0:
        ttk.Label(frame_add_unk7, text=label, font=font_style).place(x=5, y=5 + row*31)
        entry.place(x=55, y=4 + row*31, width=100)
    else:
        ttk.Label(frame_add_unk7, text=label, font=font_style).place(x=164, y=5 + (idx-7)*31)
        entry.place(x=210, y=4 + (idx-7)*31, width=100)

labels_update_unk7 = ["Shop ID:", "Item ID:", "Unk0:", "Unk1:", "Unk2:", "Unk3:", "Unk4:", "Unk5:", "Unk6:", "Unk7:", "Unk8:", "Unk9:", "Unk10:", "Unk11:"]
entries_update_unk7 = [ttk.Entry(frame_update_unk7, font=font_style, width=14, justify='center') for _ in range(len(labels_update_unk7))]

for idx, (label, entry) in enumerate(zip(labels_update_unk7, entries_update_unk7)):
    col = idx // 7
    row = idx % 7
    if col == 0:
        ttk.Label(frame_update_unk7, text=label, font=font_style).place(x=5, y=5 + row*31)
        entry.place(x=55, y=4 + row*31, width=100)
    else:
        ttk.Label(frame_update_unk7, text=label, font=font_style).place(x=164, y=5 + (idx-7)*31)
        entry.place(x=210, y=4 + (idx-7)*31, width=100)

#Add Unk7 Params
def add_unk7_params():
    reload_shop_data()

    shop_id = int(entries_add_unk7[0].get())
    item_id = int(entries_add_unk7[1].get())

    unk7_params = {
        "Unk0": int(entries_add_unk7[2].get()) if entries_add_unk7[2].get() else 0,
        "Unk1": int(entries_add_unk7[3].get()) if entries_add_unk7[3].get() else 0,
        "Unk2": bool(int(entries_add_unk7[4].get())) if entries_add_unk7[4].get() else False,
        "Unk3": int(entries_add_unk7[5].get()) if entries_add_unk7[5].get() else 0,
        "Unk4": bool(int(entries_add_unk7[6].get())) if entries_add_unk7[6].get() else False,
        "Unk5": int(entries_add_unk7[7].get()) if entries_add_unk7[7].get() else 0,
        "Unk6": int(entries_add_unk7[8].get()) if entries_add_unk7[8].get() else 0,
        "Unk7": int(entries_add_unk7[9].get()) if entries_add_unk7[9].get() else 0,
        "Unk8": int(entries_add_unk7[10].get()) if entries_add_unk7[10].get() else 0,
        "Unk9": int(entries_add_unk7[11].get()) if entries_add_unk7[11].get() else 0,
        "Unk10": int(entries_add_unk7[12].get()) if entries_add_unk7[12].get() else 0,
        "Unk11": int(entries_add_unk7[13].get()) if entries_add_unk7[13].get() else 0
    }

    for shop in shop_data:
        if shop["ShopId"] == shop_id:
            for item in shop["Data"]["GoodsParamList"]:
                if item["ItemId"] == item_id:
                    if item["Unk7"]:
                        return
                    else:
                        item["Unk7"].append(unk7_params)
                        break

    update_json()

#Update Unk7 Params
def update_unk7_params():
    reload_shop_data()

    shop_id = int(entries_update_unk7[0].get())
    item_id = int(entries_update_unk7[1].get())

    unk7_params = {
        "Unk0": int(entries_update_unk7[2].get()) if entries_update_unk7[2].get() else None,
        "Unk1": int(entries_update_unk7[3].get()) if entries_update_unk7[3].get() else None,
        "Unk2": bool(int(entries_update_unk7[4].get())) if entries_update_unk7[4].get() else None,
        "Unk3": int(entries_update_unk7[5].get()) if entries_update_unk7[5].get() else None,
        "Unk4": bool(int(entries_update_unk7[6].get())) if entries_update_unk7[6].get() else None,
        "Unk5": int(entries_update_unk7[7].get()) if entries_update_unk7[7].get() else None,
        "Unk6": int(entries_update_unk7[8].get()) if entries_update_unk7[8].get() else None,
        "Unk7": int(entries_update_unk7[9].get()) if entries_update_unk7[9].get() else None,
        "Unk8": int(entries_update_unk7[10].get()) if entries_update_unk7[10].get() else None,
        "Unk9": int(entries_update_unk7[11].get()) if entries_update_unk7[11].get() else None,
        "Unk10": int(entries_update_unk7[12].get()) if entries_update_unk7[12].get() else None,
        "Unk11": int(entries_update_unk7[13].get()) if entries_update_unk7[13].get() else None
    }

    for shop in shop_data:
        if shop["ShopId"] == shop_id:
            for item in shop["Data"]["GoodsParamList"]:
                if item["ItemId"] == item_id:
                    unk7_list = item.get("Unk7", [])
                    if not isinstance(unk7_list, list):
                        unk7_list = [unk7_list]
                    for unk7_item in unk7_list:
                        for key, value in unk7_params.items():
                            if value is not None:
                                unk7_item[key] = value
                    item["Unk7"] = unk7_list
                    break

    update_json()

#Remove Unk7 Params
def remove_unk7_params():
    reload_shop_data()

    shop_id = int(entries_update_unk7[0].get())
    item_id = int(entries_update_unk7[1].get())

    for shop in shop_data:
        if shop["ShopId"] == shop_id:
            for item in shop["Data"]["GoodsParamList"]:
                if item["ItemId"] == item_id:
                    item["Unk7"] = []
                    break

    update_json()

#Bind Enter key to only trigger the button function of the active tab
def press_enter(event):
    reload_shop_data()

    current_tab = notebook.index(notebook.select())
    if current_tab == 0:
        add_item()
    elif current_tab == 1:
        update_item_or_shop()
    elif current_tab == 2:
        add_unk7_params()
    elif current_tab == 3:
        update_unk7_params()

root.bind("<Return>", press_enter)

#Buttons
ttk.Button(frame_add, text="Add Item", command=add_item, style='TButton').place(x=-10, y=260, width=336, height=35)
ttk.Button(frame_add, text="Export to ShopPrice.csv", command=export_json_to_csv).place(x=-10, y=295, width=336, height=35)

ttk.Button(frame_update, text="Update Item/Shop", command=update_item_or_shop, style='TButton').place(x=-10, y=260, width=336, height=35)
ttk.Button(frame_update, text="Remove Item/Shop", command=remove_item_or_shop).place(x=-10, y=295, width=336, height=35)
ttk.Checkbutton(frame_update, text="Skip all confirmations", variable=checkbox_state, command=on_checkbox_change).grid(row=8, column=0, columnspan=1, padx=(2, 0), pady=(0, 70), ipadx=0, ipady=4, sticky='ew')

ttk.Button(frame_add_unk7, text="Add Unk7", command=add_unk7_params).place(x=-10, y=295, width=336, height=35)

ttk.Button(frame_update_unk7, text="Update Unk7", command=update_unk7_params).place(x=-10, y=260, width=336, height=35)
ttk.Button(frame_update_unk7, text="Remove Unk7", command=remove_unk7_params).place(x=-10, y=295, width=336, height=35)

#Directory of the script
script_dir = os.path.dirname(os.path.realpath(__file__))
config_file_path = os.path.join(script_dir, 'config.ini')

#Save checkbox state to config.ini
def save_checkbox_state(state):
    try:
        config = configparser.ConfigParser()
        config['Settings'] = {'SkipConfirmation': str(state)}
        with open(config_file_path, 'w') as configfile:
            config.write(configfile)
    except Exception as e:
        print("Error saving configuration:", e)

#Load checkbox state from config.ini
def load_checkbox_state():
    try:
        if not os.path.exists(config_file_path):
            save_checkbox_state(False)
        config = configparser.ConfigParser()
        config.read(config_file_path)
        return config['Settings'].getboolean('SkipConfirmation')
    except Exception as e:
        print("Error loading configuration:", e)
        return False

#Create config.ini with default state if it doesn't exist
checkbox_state.set(load_checkbox_state())
save_checkbox_state(False)

reload_shop_data()

root.mainloop()