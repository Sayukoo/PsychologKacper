# Kacper Kulesza – Psycholog | Strona internetowa

Oficjalny serwis internetowy psychologa Kacpra Kuleszy ([psychologkacper.pl](https://psychologkacper.pl)).
Serwis zawiera prezentację oferty, kalendarz rezerwacji 15-minutowych konsultacji online (Calendly) oraz interaktywny moduł 4 certyfikowanych testów psychologicznych (ASRS, GAD-7, PHQ-9, WHO-5) z generatorem raportów PDF.

---

## 📁 Architektura i struktura plików

Strona została zbudowana w nowoczesnej, modułowej architekturze opartej na czystym HTML5, CSS3 i JavaScript (ES6+), bez ciężkich zależności i frameworków, co gwarantuje błyskawiczne ładowanie i 100/100 w PageSpeed Insights.

### 🌐 Podstrony HTML
- [`index.html`](index.html) – Strona główna: Hero, Dla kogo, O mnie, Jak pracujemy, Cennik, FAQ, Rezerwacja Calendly.
- [`testy.html`](testy.html) – Centrum testów psychologicznych: interaktywny quiz, wskaźniki punktacji i eksport do PDF.
- [`kontakt.html`](kontakt.html) – Podstrona bezpośredniego kontaktu, formularz wiadomości i dane teleadresowe.

### 🧩 Podstrony generowane (`tools/build.py`)
Strona usługi, strony „W czym pomagam”, opisy testów i artykuły poradnika powstają z fragmentów w [`tools/content/`](tools/content) i wspólnego szablonu. **Nie edytuj wygenerowanych plików ręcznie** – zmień fragment i uruchom:

```bash
python tools/build.py
```

Skrypt zapisuje podstrony (katalog główny i `poradnik/`), odświeża `sitemap.xml`, `llms.txt` oraz mapę linków w stopkach stron pisanych ręcznie.

- **Nowy artykuł:** skopiuj dowolny plik `tools/content/a*.html`, zmień pola w nagłówku `<!--META {...} -->` (`slug`, `title`, `description`, `h1`, `lead`, `card`, `updated`, `faq`, `related`) i treść. Linki w treści pisz względem katalogu głównego (np. `href="natlok-mysli.html"`).
- **Zasada treści:** pierwsze dwa zdania (`lead`) odpowiadają na pytanie z tytułu; fakty i liczby zamiast przymiotników; źródła na końcu.
- **Po wdrożeniu:** `python tools/indexnow.py` zgłasza adresy z mapy strony do Binga (IndexNow).

### 🔎 Widoczność w wyszukiwarkach i asystentach AI
- [`robots.txt`](robots.txt) – jawna zgoda dla wyszukiwarek i botów wyszukiwania AI (m.in. `OAI-SearchBot`, od którego zależy obecność w wyszukiwaniu ChatGPT); boty trenujące modele (`GPTBot`, `ClaudeBot`, `Google-Extended` i inne) oraz katalogi robocze są zablokowane.
- [`sitemap.xml`](sitemap.xml), [`llms.txt`](llms.txt) – generowane przez `tools/build.py`.
- Dane strukturalne schema.org (JSON-LD) na każdej stronie: `ProfessionalService`, `Person`, `Service`, `FAQPage`, `Article`, `BreadcrumbList`.

### 🎨 Style CSS (`/css/`)
Plik główny [`css/style.css`](css/style.css) importuje dedykowane, lekkie moduły:
- [`css/variables.css`](css/variables.css) – Zmienne CSS, paleta barw (Brand Blue, Orange, Yellow), cienie, gradienty.
- [`css/base.css`](css/base.css) – Reset, typografia bazowa, kontenery, sekcje, aury tła (`.bg-blob`), system animacji (keyframes, `.reveal-on-scroll`, pasek postępu, przycisk „na górę”, `prefers-reduced-motion`).
- [`css/navigation.css`](css/navigation.css) – Pasek nawigacji, sticky header, menu mobilne (fullscreen drawer).
- [`css/components.css`](css/components.css) – Przyciski CTA (`.btn-cta`), pigułki, pasek cookie (`.cookie-bar`).
- [`css/sections.css`](css/sections.css) – Sekcje strony głównej (Hero, O mnie, Cennik, FAQ) i reguły RWD.
- [`css/tests.css`](css/tests.css) – Kafelki testów, widok pytań quizu, okrągłe wskaźniki wyniku, styl raportu PDF.
- [`css/contact.css`](css/contact.css) – Kafelki kontaktowe, formularz i pola tekstowe.
- [`css/article.css`](css/article.css) – Układ podstron treściowych (okruszki, ramka z odpowiedzią, tabele, FAQ, stopka z mapą linków).
- [`css/footer.css`](css/footer.css) – Stopka strony i globalne media queries.

### 🖼️ Grafiki (`/images/`)
- `kacper-760.webp`, `kacper-1140.webp` – zoptymalizowany portret w hero (`srcset`), 79 KB zamiast 1,8 MB oryginału PNG.
- `og-image.png` – grafika do podglądu w mediach społecznościowych.

### ⚙️ Skrypty JavaScript (`/js/`)
- [`js/main.js`](js/main.js) – Menu mobilne, akordeon FAQ, rozwijana polityka prywatności, pasek cookie, efekt spotlight, pasek postępu przewijania, podświetlanie aktywnej sekcji w nawigacji, przycisk „na górę” oraz silnik animacji wejścia (IntersectionObserver + zabezpieczenia).
- [`js/tests-data.js`](js/tests-data.js) – Słownik pytań, skale punktacji i przedziały interpretacyjne testów (ASRS, GAD-7, PHQ-9, WHO-5).
- [`js/tests.js`](js/tests.js) – Silnik quizu (przejścia pytań, obliczanie punktów, generowanie raportu PDF do druku).
- [`js/contact.js`](js/contact.js) – Walidacja formularza kontaktowego i obsługa wysyłki wiadomości.

---

## 🚀 Wdrożenie (GitHub Pages)

Każdy `git push origin main` automatycznie buduje i publikuje najnowszą wersję strony na GitHub Pages z podpiętą domeną `psychologkacper.pl` (zgodnie z plikiem `CNAME`).

---

## 🎬 Warstwa animacji

Cała motoryka strony żyje w CSS; JavaScript wyłącznie przełącza klasy.

- **Wejście sekcji** – `IntersectionObserver` nadaje `.is-revealed` z kaskadowym opóźnieniem (`--reveal-delay`). Silnik ma trzy niezależne zabezpieczenia (obserwator, przemiatanie przy przewijaniu/zmianie rozmiaru oraz twardy limit czasu), żeby szybkie przewinięcie albo wejście z kotwicą `#faq` nigdy nie zostawiło pustej strony.
- **Hero** – sekwencyjne wejście nagłówka, obracający się pierścień, oddychająca poświata i unoszący się portret.
- **Nawigacja** – pasek zagęszcza się po przewinięciu, podkreślenia linków wjeżdżają z boku, aktywna sekcja podświetla się automatycznie.
- **Reakcja na kursor** – „spotlight” na kafelkach, płynne uniesienia i połysk na przyciskach CTA.
- **`prefers-reduced-motion`** – jeden blok w `base.css` wyłącza cały ruch dla osób, które sobie tego życzą.
