---
# pandoc dokumentacja-wstepne-wyniki.md --citeproc -o dokumentacja-wstepne-wyniki.pdf
lang: pl
bibliography: references.bib
nocite: "@*"
csl: ieee.csl
link-citations: true
---

# Dokumentacja - wstępne wyniki

* Mikołaj Garbowski
* Mariusz Pakulski
* Paweł Łasica

## Definicja problemu

Badane zagadnienie to agent oparty na wielkim modelu językowym przeznaczony do konwersacyjnej analizy danych ustrukturyzowanych.
Kluczowym komponentem takiego systemu jest zadanie text-to-SQL, czyli tłumaczenie zapytania użytkownika w języku naturalnym na zapytanie SQL.
Agent ma możliwość wykonywania zapytań SQL w samej bazie danych, a także mechanizmy dostępu do informacji na temat analizowanej bazy danych (np. schemat, przykładowe dane).

W ramach projektu porównamy skuteczność różnych strategii agenta oraz różnych LLM na benchmarku Spider [@yu2018spider]

## Studia literaturowe

Zagadnienie wykorzystania modeli językowych do zastosowań z zakresu analizy danych i zadań BI dla baz relacyjnych jest szeroko badane.
Typowe rozwiązania obejmują podejścia typu text-to-sql, a także text-to-python i text-to-dsl jako popularne alternatywy do obrabiania ustrukturyzowanych danych [@tian2025tableagents].

W celu zrozumienia struktury tabeli, typowo dane tabelaryczne są serializowane do jakiejś postaci tekstowej (markdown, json, itp.) co pozwala na bezpośrednie umieszczenie danych w prompcie, natomiast wyzwaniem jest ograniczony rozmiar kontekstu.
Badane są także alternatywne podejścia, np. przetwarzanie obrazu tabeli modelami typu VLM, przetwarzanie tabeli w postaci struktur grafowych, a także szczególnie interesujące: traktowanie danych tableraycznych jako odrędnej modalności.
Przykładem takiego rozwiązania jest TableGPT2 [@su2024tablegpt2], które łączy koder danych tabelarycznych, produkujący semantyczne osadzenia dla kolumn tabeli, połączony z modelem językowym typu tylko-dekoder wykorzystującym te osadzenia oraz prompt użytkownika.

Sposobem na rozwiązanie problemu z rozmiarem kontekstu, wzbogacenie promptu użytkownika o wiedzę domenową, a także wydobycie informacji o schemacie bazy danych, stosowane są metody znane z zastosowań typu RAG, zadania *retrieval*.

### Zbiory danych

Popularny zbiór WikiSQL [@zhong2017seq2sql] obejmuje proste zapytania SQL dotyczące pojedynczych tabel.

Bardziej złożone zapytania SQL (obejmujące złączenia, agregacje itp.) zawierają, znacznie większe zbiory, Spider [@yu2018spider] i bardziej obszerny BIRD [@li2023bird].
rny Spider [@shi2024survey].

### Miary jakości

W literaturze stosowane są następujące miary jakości do oceny rozwiązań typu text-to-SQL:

- Execution accuracy [@shi2024survey] - Określa zgodność wyników zapytania wygenerowanego przez model z wynikami zapytania referencyjnego. Zapytanie uznaje się za poprawne, jeśli po wykonaniu na bazie danych zwraca taki sam rezultat jak zapytanie wzorcowe. 

- Exact set match accuracy [@shi2024survey] - Polega na porównaniu struktury zapytania SQL wygenerowanego przez model z zapytaniem referencyjnym. Zapytanie uznaje się za poprawne, jeżeli wszystkie jego komponenty, takie jak SELECT, WHERE, GROUP BY czy ORDER BY, odpowiadają komponentom zapytania wzorcowego. 

- Execution Accuracy per SQL Hardness [@yu2018spider] - Dzieli zapytania SQL według poziomu złożoności na cztery kategorie:

    * easy,
    * medium,
    * hard,
    * extra hard.

    Klasyfikacja ta opiera się na analizie struktury zapytania SQL, w szczególności na obecności:
    
    * złączeń tabel (JOIN),
    * grupowania danych (GROUP BY),
    * zapytań zagnieżdżonych,
    * operacji zbiorowych,
    * liczby warunków i agregacji.

- Component matching [@yu2018spider], [@pourreza2023dinsql] - Umożliwia analizę poprawności poszczególnych komponentów zapytania SQL takich jak:
    * SELECT,
    * WHERE,
    * GROUP BY,
    * ORDER BY,
    * JOIN,
    * nested SQL.


### Strategie agentów

Istnieje wiele strategii działania agenta, które różnią się sposobem generowania zapytań SQL, interakcją z bazą danych oraz mechanizmami weryfikacji i poprawy błędów.
Niektóre z nich to:

- Plan and Solve [@wang2023planandsolve] - polega na rozdzieleniu procesu rozwiązywania problemu na dwa etapy - utworzenie planu rozwiązania i wykonanie zaplanowanych kroków. Model językowy najpierw generuje strukturę działania opisującą sposób rozwiązania zadania, a następnie realizuje kolejne kroki prowadzące do wygenerowania zapytania SQL.

- Chain-of-thought [@yao2022react] - polega na generowaniu rozwiązania poprzez sekwencję kroków rozumowania, bez bezpośredniej interakcji z narzędziami lub środowiskiem wykonawczym w trakcie procesu wnioskowania. Model językowy analizuje zapytanie użytkownika i generuje końcowe zapytanie SQL w jednym przebiegu.

- ReAct - Strategia ReAct (Reason and Act) [@yao2022react] łączy proces rozumowania z wykonywaniem akcji w środowisku zewnętrznym. Model językowy generuje kolejne kroki działania, wykonuje zapytania SQL lub operacje pomocnicze, analizuje wyniki ich wykonania oraz w razie potrzeby modyfikuje swoje decyzje. 
W implementacji systemu wykorzystany zostanie komponent SQL Agent frameworka LangChain [@langchainsqlagent], który domyślnie realizuje logikę działania zgodną z podejściem ReAct. Strategia ta stanowi zatem naturalny wariant bazowy dla systemów konwersacyjnych operujących na bazach danych.


### Strategie tworzenia promptów self-correction

- Gentle self-correction prompt [@pourreza2023dinsql] - nie zakłada błędu, lecz prosi model o sprawdzenie zapytania i ewentualne wskazanie problemów, podając wskazówki dotyczące elementów SQL do weryfikacji.
- Generic prompt [@pourreza2023dinsql] - Zakłada, że zapytanie jest błędne i poleca modelowi zidentyfikować oraz poprawić błędy.

Obie strategie zostały zaimplementowane w strategii zero-shot, czyli bez dodatkowego trenowania modelu na danych specyficznych dla zadania.

## Opis rozwiązania

Projekt obejmuje implementację agentów wykorzystujących różne strategie oraz porównanie ich skuteczności.

### Zbiór danych

Do ewaluacji jakości wykorzystamy zbiór Spider.
WikiSQL uznajemy za nieodpowiedni dla naszego projektu, skoncentrowanego na bardziej złożonych zapytaniach analitycznych.
BIRD byłby również dobrym wyborem, natomiast decydujemy się na Spider: również bardzo popularny i mniejszy, co ułatwi nam pracę na ograniczonych zasobach sprzętowych.

### Baza danych

Integrujemy agenta z SQLite: uruchamianią lokalnie, relacyjną bazą danych.
Jest to typowy wybór przy tego typu zadaniach, używana w popularnych zbiorach danych [@yu2018spider], [@zhong2017seq2sql], [@li2023bird].

### Plan eksperymentów

Planujemy porównać skuteczność opisanych powyżej strategii Plan and Solve, Chain-of-thought oraz ReAct.
Planujemy również porównać skuteczność modeli o otwartych wagach dostępne na HuggingFace, wstępnie model z rodziny Llama [@touvron2024llama3] oraz Bielika [@ociepa2025bielik].


## Implementacja

### Platforma
Za platformę roboczą przyjmujemy środowisko uruchomieniowe Google Colab. Dostarcza ona możliwość korzystania z dedykownych kart TPU/GPU oraz uruchamiania notatników Jupyter. W przypadku chęci rozwoju projektu o GUI dopuszczamy możliwość skonteneryzowania aplikacji i uruchamiania jej lokalnie.

### Narzędzia
- langchain/langgraph [@langchainsqlagent], [@langgraphsqlagent] - biblioteki dostarczaczające rozwiązania dotyczące budowania promptów, agentów oraz zdolności rozumowania
- transformers - biblioteka ułatwiająca pracę z wielkimi modelami językowymi
- pytorch - biblioteka ogólnego przeznaczona do działań głębokiego uczenia oraz tensorów

## Instrukcja obsługi

* Do zarządzania projektem Python, zależnościami: [uv](https://docs.astral.sh/uv/)
* Do wykonywania komend: [just](https://github.com/casey/just)
* Wszystkie komendy opisane w `Justfile`
  * lista wszystkich dostępnych `just -l`
  * opis skryptów `just <komenda> --help`
  * komendy uruchamiane np. `just test`
* Instalacja zależności: `just install`
* Pobranie zbiorów danych `just datasets`
* Przeprowadzenie ewaluacji
  * `just make_predictions` - generuje za pomocą agenta zapytania SQL dla zapytań w języku naturalnym i baz danych ze zbioru Spider.
  * `just evaluate` - oblicza miary jakości porównując wygenerowane i wzorcowe zapytania SQL

## Testy

Wykorzystujemy zaadaptowany skrypt do ewaluacji na zbiorze Spider z repozytorium https://github.com/taoyds/spider.

### Wstępne wyniki

TODO - ułożyć to jakoś składniej przed oddaniem (opisać z jakimi parametrami, temperatura itp)
TODO - zrobić żeby się mieściło na stronie PDFa

Poniżej wstępne wyniki dla agenta realizującego wariant podejścia ReAct, wykorzystującego model `Qwen/Qwen2.5-1.5B-Instruct`

#### Dla zbioru testowego, bez mechanizmu self-correction
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

#### Rezultaty dla 336 przykładów na zbiorze dev, z mechanizmem self-correction
```
                     easy                 medium               hard                 extra                all                 
count                76                   141                  57                   62                   336                 
=====================   EXECUTION ACCURACY     =====================
execution            0.211                0.142                0.088                0.065                0.134               

====================== EXACT MATCHING ACCURACY =====================
exact match          0.145                0.071                0.035                0.000                0.068               

---------------------PARTIAL MATCHING ACCURACY----------------------
select               0.783                0.647                1.000                0.800                0.759               
select(no AGG)       0.783                0.647                1.000                0.800                0.759               
where                0.750                0.423                0.375                0.400                0.509               
where(no OP)         0.750                0.423                0.375                0.400                0.509               
group(no Having)     1.000                0.000                1.000                0.800                0.800               
group                0.000                0.000                1.000                0.800                0.733               
order                1.000                1.000                0.667                0.417                0.619               
and/or               1.000                0.915                0.825                0.836                0.904               
IUEN                 0.000                0.000                0.000                0.000                0.000               
keywords             0.842                0.733                0.727                0.800                0.773               
---------------------- PARTIAL MATCHING RECALL ----------------------
select               0.237                0.156                0.193                0.194                0.188               
select(no AGG)       0.237                0.156                0.193                0.194                0.188               
where                0.300                0.172                0.086                0.053                0.158               
where(no OP)         0.300                0.172                0.086                0.053                0.158               
group(no Having)     0.250                0.000                0.375                0.286                0.133               
group                0.000                0.000                0.375                0.286                0.122               
order                1.000                0.250                0.167                0.179                0.224               
and/or               0.987                1.000                1.000                0.981                0.993               
IUEN                 0.000                0.000                0.000                0.000                0.000               
keywords             0.348                0.172                0.140                0.194                0.198               
---------------------- PARTIAL MATCHING F1 --------------------------
select               0.364                0.251                0.324                0.312                0.301               
select(no AGG)       0.364                0.251                0.324                0.312                0.301               
where                0.429                0.244                0.140                0.093                0.241               
where(no OP)         0.429                0.244                0.140                0.093                0.241               
group(no Having)     0.400                1.000                0.545                0.421                0.229               
group                1.000                1.000                0.545                0.421                0.210               
order                1.000                0.400                0.267                0.250                0.329               
and/or               0.993                0.956                0.904                0.903                0.947               
IUEN                 1.000                1.000                1.000                1.000                1.000               
keywords             0.492                0.278                0.235                0.312                0.315   
```

## Wnioski

TODO: w kolejnych iteracjach projektu.

## Bibliografia
