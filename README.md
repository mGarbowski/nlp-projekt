# nlp-projekt

## Terminy
* do 9 IV 2026 - przekazanie dokumentacji wstępnej - drogą mailową
* do 28 IV 2026 - przekazanie dokumentacji ze wstępnymi wynikami - drogą mailową
* do 19 V 2026 - ostateczny termin oddania-przekazania projektów

## Temat projektiu

Opracowanie Agenta SQL do konwersacyjnej analizy danych ustrukturyzowanych.

Zadania:

* Zaprojektować architekturę i zaimplementować konwersacyjnego agenta SQL z mechanizmami planowania (np. ReAct, MRKL, Plan-and-Solve) w zakresie konwersji języka naturalnego na zapytania SQL (LLM-as-SQL-translator)
* Zintegrować system z wybraną bazą danych (np. PostgreSQL, MySQL, SQLite)
* Porównać skuteczność różnych modeli LLM (self-hosted lub/i poprzez API) w generowaniu zapytań SQL oraz generowanych odpowiedzi (np. porównanie 2 modeli)
* Zaplanować oraz przeprowadzić ewaluację na wybranych danych ustrukturyzowanych
* Zbadać zdolność systemu do mechanizmów self-correction błędnych zapytań na podstawie weryfikacji wyników

### Koncepcja

Mamy opracować agenta, więc nie musimy teoretycznie implementować niczego od zera. Tylko z architektury jakiś popeline stworzyć, żeby pytania użytkowników, LLM, generowanie SQL, baza danych i odpowiedź ze sobą współpracowały. Najważniejsze będą eksperymenty. Można dać takie jak analiza błędów jakie pojawiły się w zapytaniu zanim system je ewentualnie poprawił, jak dobrze je poprawił poprzez self-correction,  jakie jest mu najciężej poprawić, najdłuzej lub w ogóle nie udało mu się ich poprawić. Można też porównać system z self-correction i bez. Tutaj można dać 2 modele do przetestowania i self-correction od LangChain automatycznego, przez prompty albo może zewnętrzny parser.

### Uwagi

Potwierdzam wybór tematu oraz możliwość rozpoczęcia przez Państwa prac. Dziękuję również za przesłanie konceptu realizacji zadania. Dodatkowo z uwagi, na to iż projekt został wybrany przez jedną z grup, prosiłbym w przypadku Państwa realizacji zadania o zbadanie zdolności systemu do obsługi złożonych zapytań analitycznych (agregacje, podzapytania, złączenia)

W ramach projektu, proszę o przestrzeganie nn. terminów:
* do 9 IV 2026 - przekazanie dokumentacji wstępnej - drogą mailową
* do 28 IV 2026 - przekazanie dokumentacji ze wstępnymi wynikami - drogą mailową
* do 19 V 2026 - ostateczny termin oddania-przekazania projektów (oddanie projektu obejmuje prezentację projektu) - przesłanie finalnej dokumentacji + kodu źródłowego(drogą mailową) wraz z wcześniejszym umówieniem się na prezentację projektu.

Prosiłbym również o zapoznanie się z generalnymi kryteriami realizacji oraz oceny projektu w ramach przedmiotu: https://staff.elka.pw.edu.pl/~pandrusz/nlp.html 
