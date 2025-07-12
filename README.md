🛒 Online Retail Product Recommendation System
This application is an interactive and intelligent retail recommender system built using Python and Tkinter that analyzes customer transaction data and helps users discover top-selling products, country-wise trends, and monthly performance. It also offers search-based product recommendations based on partial keywords, with sorting options and insightful visualizations.

📌 Features
🧠 Intelligent Product Recommender
Enter any partial or full product name to receive top-N similar product suggestions.

Automatically handles plural/singular variations for flexible querying.

Sort recommendations by:

Popularity (based on total quantity sold)

Price (Low to High / High to Low)

📊 Visual Analytics
Top 10 Global Products: Visualizes the most sold items globally.

Top 3 Products per Country: Choose any country to explore its best-selling items.

Monthly Sales Trends: Line chart of top 5 product sales across months.

🖥️ Interactive GUI (Tkinter)
User-friendly and professional interface styled like a modern retail tool.

Clean layout with dropdowns, tables, and dialogs.

Clickable product rows to see detailed info (name, price, quantity).

📚 Libraries & Technologies Used
Library	Purpose
pandas	Data loading, cleaning, manipulation
matplotlib, seaborn	Plotting and visual analytics
tkinter / ttk	GUI interface and styling
warnings	Ignoring harmless runtime warnings

📂 Dataset Used
File: OnlineRetail.xlsx (needs to be placed in the same directory)

Contains historical transaction data from an online UK-based retail store with fields like:

InvoiceDate, Description, Quantity, UnitPrice, CustomerID, Country

🧩 Code Structure
load_data(): Loads and cleans the dataset

describe_data(): Shows info and missing values

find_popular_items(): Prints global/country/monthly top items

get_recommendations(query, items, top_n): Main recommendation logic

launch_gui(items, df): Builds and launches the complete GUI

