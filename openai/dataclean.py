import re

with open("title.txt", "r") as f:
    file_text = f.read()

# Extract title
title = re.search(r"Save\n\d+\n(.+)\n", file_text)

# Extract author(s)
authors = re.findall(r"Authors(.+)\n", file_text)[0]
authors = re.sub(r"\(Author\)|\(Translator\)|\(Writer of introduction\)|\(Producer\)|\(Director\)|\(Writer of foreword\)|,+", "", authors)
authors = re.split(r"\s+", authors.strip())

# Extract summary
summary = re.search(r"Summary(.+)\n", file_text, re.DOTALL).group(1)

    
print(title)
print(authors)
print(summary)
