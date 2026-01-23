import os

def generate_waterloo_page():
    content = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="Find the best cannabis dispensary near you in Waterloo. Located next to Tim Hortons on Erb St.">
  <title>Cannabis Dispensary Near Me | Waterloo | Reserved Cannabis</title>
  <link rel="stylesheet" href="../style.css">
</head>
<body>
  <h1>Reserved Cannabis | Waterloo Dispensary</h1>
  <p>Looking for a <strong>cannabis store near you in Waterloo</strong>? Reserved Cannabis is your trusted source for top-quality cannabis products.</p>
  <p>📍 Located at <strong>646 Erb St W #101</strong>, next to Canadian Tire and Tim Hortons.</p>
  <iframe src="https://www.google.com/maps/embed?pb=!1m18!..." width="100%" height="300" style="border:0;" allowfullscreen></iframe>
  <p><a href="tel:+15192085999">Call Now</a> or <a href="https://www.reservedcannabis.ca/?utm_source=google&utm_medium=gmb&utm_campaign=waterloo_location">Shop Online</a></p>
</body>
</html>'''

    os.makedirs("posts/locations", exist_ok=True)
    with open("posts/locations/waterloo.html", "w") as f:
        f.write(content)

if __name__ == '__main__':
    generate_waterloo_page()
