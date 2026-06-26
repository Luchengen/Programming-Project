from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from urllib.parse import urljoin
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import json
import re
import os
import requests
import time

load_dotenv()

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL") or "sqlite:///instance/todo.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/garena_aov_news")
def garena_aov_news():
    url = "https://moba.garena.tw/"

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)

    news_list = []

    try:
        driver.get(url)

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        news_items = soup.select(".tab_list li a")

        for item in news_items:
            icon = item.select_one(".tab_icon")
            title = item.select_one(".tab_title")
            date = item.select_one(".tab_date")
            link = item.get("href")

            news_list.append({
                "icon": icon.get_text(strip=True) if icon else "",
                "title": title.get_text(strip=True) if title else "",
                "date": date.get_text(strip=True) if date else "",
                "link": urljoin(url, link) if link else "#"
            })

    finally:
        driver.quit()

    return render_template("garena_aov_news.html", news_list=news_list)

@app.route("/garena_delta_news")
def garena_delta_news():

    url = "https://deltaforce.garena.com/zh_tw/news/all"

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0")

    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        time.sleep(3)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        news_items = soup.select("a.category-list-item")

        news_list = [
            {
                "title": item.select_one(".info__title").get_text(strip=True)
                if item.select_one(".info__title") else "",

                "date": item.select_one(".info__date").get_text(strip=True)
                if item.select_one(".info__date") else "",

                "summary": item.select_one(".info__summary").get_text(strip=True)
                if item.select_one(".info__summary") else "",

                "image": item.select_one("img").get("src")
                if item.select_one("img") else "",

                "link": urljoin(
                    url,
                    item.get("href") if item.get("href") else ""
                )
            }
            for item in news_items
        ]

    finally:
        driver.quit()

    return render_template("garena_delta_news.html", news_list=news_list)

@app.route("/garena_codm_news")
def garena_codm_news():
    url = "https://codm.garena.tw/"

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)

    news_list = []

    try:
        driver.get(url)

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        container = soup.select_one("#news_list")

        if container:
            links = container.find_all("a")
            dates = container.find_all("span", class_="news_date")

            for a, d in zip(links, dates):
                title = a.get_text(strip=True)
                href = a.get("href")
                date = d.get_text(strip=True)

                news_list.append({
                    "title": title,
                    "date": date,
                    "link": urljoin(url, href)
                })

        seen = set()
        unique_news = []

        for item in news_list:
            if item["link"] not in seen:
                unique_news.append(item)
                seen.add(item["link"])

        news_list = unique_news

    finally:
        driver.quit()

    return render_template("garena_codm_news.html", news_list=news_list)

@app.route("/garena_ff_news")
def garena_ff_news():
    url = "https://ff.garena.com/zh/news/"

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)

    news_list = []

    try:
        driver.get(url)

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        items = soup.select(".news-list .news-item")

        for item in items:
            a_tag = item.select_one("a.news-link")

            if not a_tag:
                continue

            title = item.select_one(".news-title")
            date = item.select_one(".news-time")
            category = item.select_one(".news-category")
            img = item.select_one("img")

            link = a_tag.get("href")

            news_list.append({
                "title": title.get_text(strip=True) if title else "",
                "date": date.get_text(strip=True) if date else "",
                "category": category.get_text(strip=True) if category else "",
                "img": img.get("src") if img else "",
                "link": urljoin(url, link) if link else "#"
            })

        seen = set()
        unique = []

        for n in news_list:
            if n["link"] not in seen:
                unique.append(n)
                seen.add(n["link"])

        news_list = unique

    finally:
        driver.quit()

    return render_template("garena_ff_news.html", news_list=news_list)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)