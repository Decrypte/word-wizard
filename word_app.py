from flask import Flask, render_template, request
from collections import Counter
from typing import List, Set
import os
import requests
import time

app = Flask(__name__)


def load_dictionary(min_word_length: int = 2) -> Set[str]:
    sowpods_path = "sowpods.txt"
    if not os.path.exists(sowpods_path):
        url = "https://www.wordgamedictionary.com/sowpods/download/sowpods.txt"
        r = requests.get(url)
        with open(sowpods_path, "wb") as f:
            f.write(r.content)
    with open(sowpods_path, "r") as f:
        return {
            word.strip().lower()
            for word in f
            if len(word.strip()) >= min_word_length and word.strip().isalpha()
        }


def can_form_word(word: str, available_letters: Counter) -> bool:
    word_counter = Counter(word.lower())
    return all(
        count <= available_letters.get(char, 0) for char, count in word_counter.items()
    )


def find_words(letters: str, dictionary: Set[str]) -> List[str]:
    available_letters = Counter(letters.lower())
    valid_words = [
        word for word in dictionary if can_form_word(word, available_letters)
    ]
    valid_words.sort(key=lambda w: (-len(w), w))
    return valid_words


def group_by_length(words: List[str]):
    grouped = {}
    for word in words:
        grouped.setdefault(len(word), []).append(word)
    return grouped


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        letters = request.form.get("letters", "").strip().lower()
        min_length = int(request.form.get("min_length", 2))

        start_time = time.time()
        dictionary = load_dictionary(min_word_length=min_length)
        words = find_words(letters, dictionary)
        elapsed_time = round(time.time() - start_time, 2)

        words_by_length = group_by_length(words)
        return render_template(
            "word_wizard.html",
            letters=letters,
            min_length=min_length,
            words_by_length=words_by_length,
            total_words=len(words),
            elapsed_time=elapsed_time,
        )
    return render_template("word_wizard.html", words_by_length=None)


if __name__ == "__main__":
    app.run(debug=True)
