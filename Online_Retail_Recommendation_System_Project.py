import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from tkinter import Tk, Toplevel, messagebox
import tkinter.ttk as ttk
import warnings
warnings.filterwarnings("ignore")

# 1. Load the Retail Dataset
def load_data():
    df = pd.read_excel('OnlineRetail.xlsx')
    df.dropna(subset=['CustomerID', 'Description'], inplace=True)
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    df['Month'] = df['InvoiceDate'].dt.month
    df['Description'] = df['Description'].str.strip()
    return df

# 2. Data Description
def describe_data(df):
    print("\n--- DATA DESCRIPTION ---\n")
    print(df.info())
    print("\nHead of the data:\n")
    print(df.head())
    print("\nMissing Values:\n")
    print(df.isnull().sum())

# 3. Visualization Functions
def top_selling_global(df):
    top_global = df.groupby('Description')['Quantity'].sum().nlargest(10)
    plt.figure(figsize=(10, 6))
    sns.barplot(x=top_global.values, y=top_global.index, palette="coolwarm")
    plt.title("Top 10 Most Sold Products Globally")
    plt.xlabel("Quantity Sold")
    plt.ylabel("Product")
    plt.tight_layout()
    plt.show()


def top_selling_country_for(df, country):
    popular = df.groupby(['Country', 'Description'])['Quantity'].sum().reset_index()
    data = popular[popular['Country'] == country].sort_values('Quantity', ascending=False).head(3)
    if data.empty:
        messagebox.showinfo("No Data", f"No sales data found for {country}.")
        return
    plt.figure(figsize=(8, 4))
    sns.barplot(x='Quantity', y='Description', data=data, palette='magma')
    plt.title(f"Top 3 Products in {country}", fontsize=14)
    plt.xlabel("Quantity Sold")
    plt.ylabel("Product")
    plt.tight_layout()
    plt.show()


def top_selling_monthwise(df):
    top_products = df.groupby('Description')['Quantity'].sum().nlargest(5).index
    pivot = df[df['Description'].isin(top_products)].pivot_table(
        index='Month', columns='Description', values='Quantity', aggfunc='sum').fillna(0)
    pivot.plot(marker='o', figsize=(10, 6))
    plt.title("Monthly Sales Trends for Top Products")
    plt.ylabel("Quantity Sold")
    plt.xlabel("Month")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# 4. Print Popular Items Summary
def find_popular_items(df):
    print("\n--- TOP PRODUCTS GLOBALLY ---\n")
    print(df.groupby('Description')['Quantity'].sum().nlargest(10))
    print("\n--- TOP PRODUCTS BY COUNTRY ---\n")
    pc = df.groupby(['Country', 'Description'])['Quantity'].sum().reset_index()
    print(pc.sort_values(['Country', 'Quantity'], ascending=[True, False]).groupby('Country').head(3))
    print("\n--- TOP PRODUCTS BY MONTH ---\n")
    pm = df.groupby(['Month', 'Description'])['Quantity'].sum().reset_index()
    print(pm.sort_values(['Month', 'Quantity'], ascending=[True, False]).groupby('Month').head(3))

# 5. Build items table
def build_items(df):
    items = df[['Description', 'UnitPrice']].drop_duplicates().reset_index(drop=True)
    qty = df.groupby('Description')['Quantity'].sum().reset_index()
    return pd.merge(items, qty, on='Description', how='left').fillna(0)

# 6. Recommendation Logic (omit exact matches)
def get_recommendations(query, items, top_n=5):
    q = query.lower().strip()
    # Find all containing the query
    matched = items[items['Description'].str.lower().str.contains(q, na=False)]
    # Exclude exact match (strip spaces and lower)
    matched = matched[matched['Description'].str.lower().str.strip() != q]
    if matched.empty:
        return matched
    # Prioritize endswith 's' or not
    if q.endswith('s'):
        primary = matched[matched['Description'].str.lower().str.endswith('s')]
        secondary = matched.drop(primary.index)
    else:
        secondary = matched[matched['Description'].str.lower().str.endswith('s')]
        primary = matched.drop(secondary.index)
    combined = pd.concat([primary, secondary]).sort_values('Quantity', ascending=False)
    return combined.head(top_n)

# 7. GUI Interface
def launch_gui(items, df):
    def search_product():
        query = entry.get()
        try:
            n = int(entry_count.get())
        except ValueError:
            messagebox.showerror("Input Error", "Enter a valid number.")
            return
        if not query:
            messagebox.showwarning("Input Error", "Please enter a product name.")
            return
        results = get_recommendations(query, items, n)
        for row in tree.get_children():
            tree.delete(row)
        if results.empty:
            messagebox.showinfo("No Results", "No similar products found.")
        else:
            for _, r in results.iterrows():
                tree.insert('', 'end', values=(r['Description'], f"${r['UnitPrice']:.2f}", int(r['Quantity'])))

    def sort_products():
        if not tree.get_children():
            messagebox.showwarning("No results", "First search a product.")
            return
        tbl = [tree.item(i)['values'] for i in tree.get_children()]
        df_tbl = pd.DataFrame(tbl, columns=['Description', 'UnitPrice', 'Quantity'])
        df_tbl['Quantity'] = df_tbl['Quantity'].astype(int)
        df_tbl['UnitPrice'] = df_tbl['UnitPrice'].replace('[$,]', '', regex=True).astype(float)
        choice = sort_box.get()
        if choice == "Popularity":
            df_tbl.sort_values('Quantity', ascending=False, inplace=True)
        elif choice == "Price Ascending":
            df_tbl.sort_values('UnitPrice', ascending=True, inplace=True)
        elif choice == "Price Descending":
            df_tbl.sort_values('UnitPrice', ascending=False, inplace=True)
        for row in tree.get_children():
            tree.delete(row)
        for _, r in df_tbl.iterrows():
            tree.insert('', 'end', values=(r['Description'], f"${r['UnitPrice']:.2f}", int(r['Quantity'])))

    def on_product_click(event):
        sel = tree.focus()
        if not sel:
            return
        d, p, q = tree.item(sel)['values']
        messagebox.showinfo("Product Details", f"Product: {d}\nUnit Price: {p}\nTotal Quantity Sold: {q}")

    def choose_country():
        dlg = Toplevel(root)
        dlg.title("Select Country")
        dlg.geometry("300x100")
        ttk.Label(dlg, text="Choose Country:").pack(pady=5)
        countries = sorted(df['Country'].dropna().unique())
        cb = ttk.Combobox(dlg, values=countries, state='readonly')
        cb.pack()
        cb.set(countries[0])
        def view():
            selected = cb.get()
            dlg.destroy()
            top_selling_country_for(df, selected)
        ttk.Button(dlg, text="View", command=view).pack(pady=5)

    root = Tk()
    root.title("Online Retail Recommender")
    root.geometry("800x700")
    root.configure(bg='#f9f9f9')

    style = ttk.Style(root)
    style.theme_use('clam')
    style.configure('TFrame', background='#f9f9f9')
    style.configure('Header.TLabel', font=('Arial', 24, 'bold'), background='#004aad', foreground='white')
    style.configure('TLabel', background='#f9f9f9', font=('Arial', 12))
    style.configure('TEntry', padding=5)
    style.configure('TButton', font=('Arial', 12), padding=5)
    style.map('TButton', background=[('!disabled', '#0066CC'), ('active', '#004AAD')])
    style.configure('Treeview', rowheight=25, font=('Arial', 11))
    style.configure('Treeview.Heading', font=('Arial', 12, 'bold'))

    header = ttk.Frame(root)
    header.pack(fill='x')
    ttk.Label(header, text="Online Retail Product Recommender", style='Header.TLabel').pack(fill='x')

    main_frame = ttk.Frame(root, padding=20)
    main_frame.pack(fill='both', expand=True)

    search_frame = ttk.Frame(main_frame)
    search_frame.pack(fill='x', pady=10)
    ttk.Label(search_frame, text="Product Name:").grid(row=0, column=0, sticky='w')
    entry = ttk.Entry(search_frame, width=40)
    entry.grid(row=0, column=1, padx=10)
    ttk.Label(search_frame, text="Recommendations:").grid(row=1, column=0, sticky='w', pady=5)
    entry_count = ttk.Entry(search_frame, width=5)
    entry_count.insert(0, '5')
    entry_count.grid(row=1, column=1, sticky='w')
    ttk.Button(search_frame, text="Search", command=search_product).grid(row=2, column=0, columnspan=2, pady=10)

    ttk.Label(search_frame, text="Sort By:").grid(row=3, column=0, sticky='w', pady=5)
    sort_box = ttk.Combobox(search_frame, values=["Popularity", "Price Ascending", "Price Descending"], state='readonly')
    sort_box.set("Popularity")
    sort_box.grid(row=3, column=1, sticky='w')
    ttk.Button(search_frame, text="Sort", command=sort_products).grid(row=3, column=2, padx=10)

    table_frame = ttk.Frame(main_frame)
    table_frame.pack(fill='both', expand=True, pady=10)
    cols = ('Description', 'UnitPrice', 'Quantity Sold')
    tree = ttk.Treeview(table_frame, columns=cols, show='headings')
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, anchor='w')
    tree.pack(fill='both', expand=True)
    tree.bind('<<TreeviewSelect>>', on_product_click)

    viz_frame = ttk.LabelFrame(main_frame, text='Visualize Popular Items')
    viz_frame.pack(fill='x', pady=10)
    ttk.Button(viz_frame, text="Top Global Products", command=lambda: top_selling_global(df)).pack(side='left', padx=10, pady=5)
    ttk.Button(viz_frame, text="Countrywise", command=choose_country).pack(side='left', padx=10, pady=5)
    ttk.Button(viz_frame, text="Monthly Trends", command=lambda: top_selling_monthwise(df)).pack(side='left', padx=10, pady=5)

    root.mainloop()

if __name__ == '__main__':
    df = load_data()
    describe_data(df)
    find_popular_items(df)
    items = build_items(df)
    launch_gui(items, df)
