# nlp-projekt

## Terminy

* do 9 IV 2026 - przekazanie dokumentacji wstępnej - drogą mailową
* do 28 IV 2026 - przekazanie dokumentacji ze wstępnymi wynikami - drogą mailową
* do 19 V 2026 - ostateczny termin oddania-przekazania projektów

## Temat projektiu

Opracowanie Agenta SQL do konwersacyjnej analizy danych ustrukturyzowanych.

Zadania:

* Zaprojektować architekturę i zaimplementować konwersacyjnego agenta SQL z mechanizmami planowania (np. ReAct, MRKL,
  Plan-and-Solve) w zakresie konwersji języka naturalnego na zapytania SQL (LLM-as-SQL-translator)
* Zintegrować system z wybraną bazą danych (np. PostgreSQL, MySQL, SQLite)
* Porównać skuteczność różnych modeli LLM (self-hosted lub/i poprzez API) w generowaniu zapytań SQL oraz generowanych
  odpowiedzi (np. porównanie 2 modeli)
* Zaplanować oraz przeprowadzić ewaluację na wybranych danych ustrukturyzowanych
* Zbadać zdolność systemu do mechanizmów self-correction błędnych zapytań na podstawie weryfikacji wyników

### Koncepcja

Mamy opracować agenta, więc nie musimy teoretycznie implementować niczego od zera. Tylko z architektury jakiś popeline
stworzyć, żeby pytania użytkowników, LLM, generowanie SQL, baza danych i odpowiedź ze sobą współpracowały. Najważniejsze
będą eksperymenty. Można dać takie jak analiza błędów jakie pojawiły się w zapytaniu zanim system je ewentualnie
poprawił, jak dobrze je poprawił poprzez self-correction, jakie jest mu najciężej poprawić, najdłuzej lub w ogóle nie
udało mu się ich poprawić. Można też porównać system z self-correction i bez. Tutaj można dać 2 modele do przetestowania
i self-correction od LangChain automatycznego, przez prompty albo może zewnętrzny parser.

### Uwagi

Potwierdzam wybór tematu oraz możliwość rozpoczęcia przez Państwa prac. Dziękuję również za przesłanie konceptu
realizacji zadania. Dodatkowo z uwagi, na to iż projekt został wybrany przez jedną z grup, prosiłbym w przypadku Państwa
realizacji zadania o zbadanie zdolności systemu do obsługi złożonych zapytań analitycznych (agregacje, podzapytania,
złączenia)

W ramach projektu, proszę o przestrzeganie nn. terminów:

* do 9 IV 2026 - przekazanie dokumentacji wstępnej - drogą mailową
* do 28 IV 2026 - przekazanie dokumentacji ze wstępnymi wynikami - drogą mailową
* do 19 V 2026 - ostateczny termin oddania-przekazania projektów (oddanie projektu obejmuje prezentację projektu) -
  przesłanie finalnej dokumentacji + kodu źródłowego(drogą mailową) wraz z wcześniejszym umówieniem się na prezentację
  projektu.

Prosiłbym również o zapoznanie się z generalnymi kryteriami realizacji oraz oceny projektu w ramach
przedmiotu: https://staff.elka.pw.edu.pl/~pandrusz/nlp.html

## Instalacja, uruchomienie

* [uv](https://docs.astral.sh/uv/)
* [just](https://github.com/casey/just)
* Wszystkie komendy opisane w [Justfile](./Justfile)
    * lista `just -l`
    * komendy uruchamiane np. `just test`

## Wyniki dla wszystkich 2148 przykładów ze zbioru testowego

```

                     easy                 medium               hard                 extra                all                 
count                470                  857                  463                  357                  2147                
=====================   EXECUTION ACCURACY     =====================
execution            0.240                0.156                0.065                0.050                0.137               

====================== EXACT MATCHING ACCURACY =====================
exact match          0.170                0.095                0.037                0.025                0.087               

---------------------PARTIAL MATCHING ACCURACY----------------------
select               0.851                0.823                0.840                0.912                0.843               
select(no AGG)       0.862                0.827                0.840                0.912                0.849               
where                0.844                0.696                0.338                0.350                0.603               
where(no OP)         0.844                0.717                0.485                0.450                0.658               
group(no Having)     1.000                0.444                0.840                0.625                0.710               
group                0.100                0.389                0.840                0.562                0.551               
order                0.250                0.500                0.622                0.450                0.441               
and/or               1.000                0.943                0.940                0.869                0.943               
IUEN                 0.000                0.000                0.000                0.000                0.000               
keywords             0.531                0.481                0.460                0.439                0.485               
---------------------- PARTIAL MATCHING RECALL ----------------------
select               0.328                0.233                0.181                0.146                0.228               
select(no AGG)       0.332                0.235                0.181                0.146                0.230               
where                0.372                0.311                0.089                0.064                0.200               
where(no OP)         0.372                0.320                0.127                0.082                0.219               
group(no Having)     0.263                0.028                0.162                0.074                0.084               
group                0.026                0.025                0.162                0.066                0.065               
order                0.159                0.203                0.160                0.063                0.143               
and/or               0.996                0.996                0.977                0.984                0.990               
IUEN                 0.000                0.000                0.000                0.000                0.000               
keywords             0.260                0.147                0.101                0.070                0.137               
---------------------- PARTIAL MATCHING F1 --------------------------
select               0.473                0.364                0.298                0.251                0.359               
select(no AGG)       0.479                0.365                0.298                0.251                0.361               
where                0.517                0.430                0.141                0.108                0.301               
where(no OP)         0.517                0.443                0.202                0.138                0.328               
group(no Having)     0.417                0.053                0.271                0.132                0.150               
group                0.042                0.047                0.271                0.118                0.116               
order                0.194                0.289                0.254                0.111                0.216               
and/or               0.998                0.969                0.958                0.923                0.966               
IUEN                 1.000                1.000                1.000                1.000                1.000               
keywords             0.349                0.225                0.166                0.121                0.213  
```

## Wyniki dla zbioru walidacyjnego - wariant COT

```
                  easy                 medium               hard                 extra                all                 
count                248                  446                  174                  166                  1034                
=====================   EXECUTION ACCURACY     =====================
execution            0.238                0.175                0.098                0.060                0.159               

====================== EXACT MATCHING ACCURACY =====================
exact match          0.206                0.123                0.075                0.012                0.117               

---------------------PARTIAL MATCHING ACCURACY----------------------
select               0.854                0.813                0.953                0.727                0.840               
select(no AGG)       0.876                0.813                0.953                0.727                0.847               
where                0.717                0.528                0.379                0.100                0.529               
where(no OP)         0.717                0.528                0.414                0.200                0.541               
group(no Having)     0.714                0.750                1.000                0.750                0.788               
group                0.143                0.708                1.000                0.667                0.673               
order                0.909                0.625                0.800                0.286                0.643               
and/or               1.000                0.919                0.912                0.884                0.932               
IUEN                 0.000                0.000                0.000                0.000                0.000               
keywords             0.885                0.689                0.575                0.636                0.716               
---------------------- PARTIAL MATCHING RECALL ----------------------
select               0.306                0.244                0.236                0.096                0.234               
select(no AGG)       0.315                0.244                0.236                0.096                0.236               
where                0.306                0.209                0.117                0.011                0.174               
where(no OP)         0.306                0.209                0.128                0.021                0.178               
group(no Having)     0.250                0.135                0.231                0.114                0.151               
group                0.050                0.128                0.231                0.101                0.129               
order                0.455                0.133                0.218                0.051                0.156               
and/or               0.992                0.993                0.975                0.986                0.989               
IUEN                 0.000                0.000                0.000                0.000                0.000               
keywords             0.360                0.193                0.132                0.084                0.189               
---------------------- PARTIAL MATCHING F1 --------------------------
select               0.451                0.376                0.378                0.170                0.366               
select(no AGG)       0.463                0.376                0.378                0.170                0.369               
where                0.429                0.299                0.179                0.019                0.261               
where(no OP)         0.429                0.299                0.195                0.038                0.268               
group(no Having)     0.370                0.229                0.375                0.198                0.254               
group                0.074                0.217                0.375                0.176                0.217               
order                0.606                0.220                0.343                0.086                0.251               
and/or               0.996                0.954                0.942                0.932                0.959               
IUEN                 1.000                1.000                1.000                1.000                1.000               
keywords             0.512                0.302                0.215                0.149                0.299 
```