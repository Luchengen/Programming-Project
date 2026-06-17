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

import os
import requests

load_dotenv()

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")

db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    content = db.Column(
        db.String(200),
        nullable=False
    )

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/todo")
def todo():

    todos = Todo.query.all()

    return render_template(
        "todo.html",
        todos=todos
    )

@app.route("/add", methods=["POST"])
def add_todo():

    content = request.form.get("content")

    if content:

        new_todo = Todo(content=content)

        db.session.add(new_todo)

        db.session.commit()

    return redirect("/todo")

@app.route("/update/<int:id>", methods=["POST"])
def update_todo(id):

    todo = Todo.query.get(id)

    if todo:

        new_content = request.form.get("content")

        if new_content:

            todo.content = new_content

            db.session.commit()

    return redirect("/todo")

@app.route("/news")
def news():

    url = "https://news.ycombinator.com/"

    response = requests.get(url)

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    titles = soup.select(".titleline a")

    result = ""

    news_list = []

    for title in titles:

        news_list.append({
            "title": title.text,
            "url": title["href"]
        })

    return render_template(
        "news.html",
        news_list=news_list
    )

@app.route("/quotes")
def quotes():
    options = Options()
    options.binary_location = "/usr/bin/chromium"
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=options)

    try:
        driver.get("https://quotes.toscrape.com/js/")

        quote_elements = driver.find_elements(
            By.CLASS_NAME,
            "quote"
        )

        quote_list = []

        for quote in quote_elements:

            text = quote.find_element(
                By.CLASS_NAME,
                "text"
            ).text

            author = quote.find_element(
                By.CLASS_NAME,
                "author"
            ).text

            quote_list.append({
                "text": text,
                "author": author
            })
    finally:
        driver.quit()

        return render_template(
        "quotes.html",
        quote_list=quote_list
    )

@app.route("/garena-news")
def garena_news():
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

    return render_template("garena_news.html", news_list=news_list)

@app.route("/aov-skins")
def aov_skins():
    url = "https://aovweb.azurewebsites.net/HeroSkin/News"

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0")

    driver = webdriver.Chrome(options=options)

    skins = []

    try:
        driver.get(url)

        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".skin-card"))
            )
        except:
            driver.refresh()
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".skin-card"))
            )

        soup = BeautifulSoup(driver.page_source, "html.parser")

        for card in soup.select(".skin-card"):
            img = card.select_one("img")

            skin = {
                "image": img.get("src") if img else "",
                "hero": "",
                "skin_name": "",
                "first_time": "",
                "method": "",
                "promotion": []
            }

            promotion_detail = card.select_one(".promotion-detail")

            for div in card.find_all("div", recursive=False):
                if div == promotion_detail:
                    continue

                text = div.get_text(strip=True)

                if text.startswith("英雄："):
                    skin["hero"] = text.replace("英雄：", "")
                elif text.startswith("造型："):
                    skin["skin_name"] = text.replace("造型：", "")
                elif text.startswith("首次上架時間："):
                    skin["first_time"] = text.replace("首次上架時間：", "")
                elif text.startswith("獲取方式："):
                    skin["method"] = text.replace("獲取方式：", "")

            if promotion_detail:
                skin["promotion"] = [
                    div.get_text(strip=True)
                    for div in promotion_detail.select("div")
                ]

            skins.append(skin)

    finally:
        driver.quit()

    return render_template("aov_skins.html", skins=skins)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)