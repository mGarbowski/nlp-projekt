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

## Instalacja, uruchomienie

* [uv](https://docs.astral.sh/uv/)
* [just](https://github.com/casey/just)
* Wszystkie komendy opisane w [Justfile](./Justfile)
  * lista `just -l`
  * komendy uruchamiane np. `just test`


## Wyniki dla pierwszych 100 przykładów

```
                     easy                 medium               hard                 extra                all                 
count                22                   34                   27                   17                   100                 
=====================   EXECUTION ACCURACY     =====================
execution            0.227                0.088                0.074                0.059                0.110               

====================== EXACT MATCHING ACCURACY =====================
exact match          0.136                0.118                0.000                0.059                0.080               

---------------------PARTIAL MATCHING ACCURACY----------------------
select               0.800                1.000                1.000                1.000                0.917               
select(no AGG)       0.800                1.000                1.000                1.000                0.917               
where                1.000                1.000                0.400                1.000                0.727               
where(no OP)         1.000                1.000                0.400                1.000                0.727               
group(no Having)     1.000                0.000                1.000                0.000                1.000               
group                0.000                0.000                1.000                0.000                0.333               
order                0.000                0.000                0.667                0.000                0.286               
and/or               1.000                0.941                1.000                1.000                0.980               
IUEN                 0.000                0.000                0.000                0.000                0.000               
keywords             0.500                0.333                0.429                1.000                0.474               
---------------------- PARTIAL MATCHING RECALL ----------------------
select               0.364                0.176                0.259                0.059                0.220               
select(no AGG)       0.364                0.176                0.259                0.059                0.220               
where                0.500                0.250                0.250                0.125                0.250               
where(no OP)         0.500                0.250                0.250                0.125                0.250               
group(no Having)     0.500                0.000                0.091                0.000                0.103               
group                0.000                0.000                0.091                0.000                0.034               
order                0.000                0.000                0.250                0.000                0.111               
and/or               1.000                1.000                0.926                1.000                0.980               
IUEN                 0.000                0.000                0.000                0.000                0.000               
keywords             0.333                0.045                0.143                0.059                0.125               
---------------------- PARTIAL MATCHING F1 --------------------------
select               0.500                0.300                0.412                0.111                0.355               
select(no AGG)       0.500                0.300                0.412                0.111                0.355               
where                0.667                0.400                0.308                0.222                0.372               
where(no OP)         0.667                0.400                0.308                0.222                0.372               
group(no Having)     0.667                1.000                0.167                1.000                0.188               
group                1.000                1.000                0.167                1.000                0.062               
order                1.000                1.000                0.364                1.000                0.160               
and/or               1.000                0.970                0.962                1.000                0.980               
IUEN                 1.000                1.000                1.000                1.000                1.000               
keywords             0.400                0.080                0.214                0.111                0.198      
```