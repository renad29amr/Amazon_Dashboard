import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px

conn = sqlite3.connect("amazon.db")

st.set_page_config(page_title="Amazon Products Dashboard", layout="wide")
st.title("📊 Amazon Products Dashboard")

categories = pd.read_sql("SELECT category_name FROM categories", conn)
categories_list = categories["category_name"].tolist()
selected_category = st.sidebar.multiselect("Select Category", categories_list, default=categories_list)

max_price = pd.read_sql("SELECT MAX(actual_price) AS max_price FROM products", conn)["max_price"].iloc[0]
min_rating, max_rating = st.sidebar.slider("Filter by Rating", 0.0, 5.0, (0.0, 5.0))
min_price, max_price = st.sidebar.slider("Filter by Actual Price", 0.0, float(max_price), (0.0, float(max_price)))

where_clause = f"""
WHERE c.category_name IN ({','.join(['?']*len(selected_category))})
AND p.rating BETWEEN ? AND ?
AND p.actual_price BETWEEN ? AND ?
"""

params = selected_category + [min_rating, max_rating, min_price, max_price]


query_main = f"""
SELECT 
    p.product_name,
    c.category_name,
    p.actual_price,
    p.discounted_price,
    p.discount_percent,
    p.rating,
    p.rating_count
FROM products p
JOIN categories c ON p.category_id = c.category_id
{where_clause}
"""
df = pd.read_sql(query_main, conn, params=params)
st.markdown(f"### Showing {len(df)} products")


query_category_count = f"""
SELECT c.category_name, COUNT(p.product_id) AS product_count
FROM products p
JOIN categories c ON p.category_id = c.category_id
{where_clause}
GROUP BY c.category_name
ORDER BY product_count DESC
"""
category_count = pd.read_sql(query_category_count, conn, params=params)
fig1 = px.bar(category_count, x="category_name", y="product_count", color="product_count",
              title="Products per Category", text="product_count")
st.plotly_chart(fig1, use_container_width=True)


query_avg_discount = f"""
SELECT c.category_name, ROUND(AVG(p.discount_percent), 2) AS avg_discount
FROM products p
JOIN categories c ON p.category_id = c.category_id
{where_clause}
GROUP BY c.category_name
ORDER BY avg_discount DESC
"""
avg_discount = pd.read_sql(query_avg_discount, conn, params=params)
fig2 = px.bar(avg_discount, x="category_name", y="avg_discount", color="avg_discount",
              title="Average Discount per Category", text="avg_discount")
st.plotly_chart(fig2, use_container_width=True)

query_top_rated = f"""
SELECT p.product_name, c.category_name, p.rating, p.rating_count, 
       p.actual_price, p.discount_percent
FROM products p
JOIN categories c ON p.category_id = c.category_id
{where_clause}
ORDER BY p.rating DESC, p.rating_count DESC
LIMIT 10
"""
top_rated = pd.read_sql(query_top_rated, conn, params=params)
st.markdown("### ⭐ Top Rated Products")
st.dataframe(top_rated)


fig3 = px.histogram(df, x="actual_price", nbins=50, title="Price Distribution of Products")
st.plotly_chart(fig3, use_container_width=True)


fig4 = px.scatter(df, x="discount_percent", y="rating", color="category_name",
                  size="rating_count", hover_data=["product_name"],
                  title="Discount % vs Rating by Category")
st.plotly_chart(fig4, use_container_width=True)

conn.close()
