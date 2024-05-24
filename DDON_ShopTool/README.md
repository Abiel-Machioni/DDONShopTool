# DDON_ShopTool
DDON ShopTool is a utility tool designed for managing shops in Dragon's Dogma Online, built with Python and Tkinter.
It allows you to add, modify, and remove items or entire shops from the Shop.json file.

## Functionality

- Reads or writes from scratch the shop data from Shop.json to display and modify shop inventories.
- Supports adding, modifying, and removing items and shops.
- Reads item sell prices and suggested prices from CSV files (itemlist.csv, ShopPrice.csv) to suggest item sell and shop prices dynamically as you write the item ID in the tool.
- Supports adding, removing or modfying items Unk7 parameters in the shop inventory.

## Usage

- If you just want to use the tool, you can download a compiled version in releases, you don't need to compile yourself, but if you do, i'll list the steps below.


## Requirements

- Python 3.8 or higher.
- Required Python packages listed in `requirements.txt`

## How to download from source and compile

1. Download and install Python: [Link](https://www.python.org/downloads/)

2. Download git: [Link](https://git-scm.com/download/win)

3. Clone the repository:

- Using bash:

    ```bash
    git clone https://github.com/Abiel-Machioni/DDON_ShopTool.git
    cd DDON_ShopTool
    ```
- Using cmd:

```git clone https://github.com/Abiel-Machioni/DDON_ShopTool```

3. Install PyInstaller:

    ```bash
    pip install pyinstaller
    ```

 ```pip install pyinstaller```

4. Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

 ```pip install -r requirements.txt```

 5. Run PyInstaller to compile into executable:

    ```bash
    pyinstaller --onefile DDON_ShopTool.py
    ```

 ```pyinstaller --onefile DDON_ShopTool.py```

6. The executable will be located in the `dist` directory.

7. Make sure itemlist.csv is in the same folder as the executable to read sell prices from it, Shop.json and ShopPrice.csv will be auto generated if there's none in the same folder, but the tool will also read from existing ones, so if you want already filled Shops and Prices, move them to the same folder.