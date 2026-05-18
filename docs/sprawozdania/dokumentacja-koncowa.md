---
# pandoc dokumentacja-koncowa.md --citeproc -o dokumentacja-koncowa.pdf
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

Badane zagadnienie to agent oparty na wielkim modelu językowym przeznaczony do konwersacyjnej analizy danych
ustrukturyzowanych.
Kluczowym komponentem takiego systemu jest zadanie text-to-SQL, czyli tłumaczenie zapytania użytkownika w języku
naturalnym na zapytanie SQL.
Agent ma możliwość wykonywania zapytań SQL w samej bazie danych, a także mechanizmy dostępu do informacji na temat
analizowanej bazy danych (np. schemat, przykładowe dane).

W ramach projektu porównujemy skuteczność różnych strategii agenta oraz różnych LLM na benchmarku Spider [@yu2018spider]

## Studia literaturowe

Zagadnienie wykorzystania modeli językowych do zastosowań z zakresu analizy danych i zadań BI dla baz relacyjnych jest
szeroko badane.
Typowe rozwiązania obejmują podejścia typu text-to-sql, a także text-to-python i text-to-dsl jako popularne alternatywy
do obrabiania ustrukturyzowanych danych [@tian2025tableagents].

W celu zrozumienia struktury tabeli, typowo dane tabelaryczne są serializowane do jakiejś postaci tekstowej (markdown,
json, itp.) co pozwala na bezpośrednie umieszczenie danych w prompcie, natomiast wyzwaniem jest ograniczony rozmiar
kontekstu.
Badane są także alternatywne podejścia, np. przetwarzanie obrazu tabeli modelami typu VLM, przetwarzanie tabeli w
postaci struktur grafowych, a także szczególnie interesujące: traktowanie danych tableraycznych jako odrędnej
modalności.
Przykładem takiego rozwiązania jest TableGPT2 [@su2024tablegpt2], które łączy koder danych tabelarycznych, produkujący
semantyczne osadzenia dla kolumn tabeli, połączony z modelem językowym typu tylko-dekoder wykorzystującym te osadzenia
oraz prompt użytkownika.

Sposobem na rozwiązanie problemu z rozmiarem kontekstu, wzbogacenie promptu użytkownika o wiedzę domenową, a także
wydobycie informacji o schemacie bazy danych, stosowane są metody znane z zastosowań typu RAG, zadania *retrieval*.

### Zbiory danych

Popularny zbiór WikiSQL [@zhong2017seq2sql] obejmuje proste zapytania SQL dotyczące pojedynczych tabel.

Bardziej złożone zapytania SQL (obejmujące złączenia, agregacje itp.) zawierają, znacznie większe zbiory,
Spider [@yu2018spider] i bardziej obszerny BIRD [@li2023bird].
rny Spider [@shi2024survey].

### Miary jakości

W literaturze stosowane są następujące miary jakości do oceny rozwiązań typu text-to-SQL:

- Execution accuracy [@shi2024survey] - Określa zgodność wyników zapytania wygenerowanego przez model z wynikami
  zapytania referencyjnego. Zapytanie uznaje się za poprawne, jeśli po wykonaniu na bazie danych zwraca taki sam
  rezultat jak zapytanie wzorcowe.

- Exact set match accuracy [@shi2024survey] - Polega na porównaniu struktury zapytania SQL wygenerowanego przez model z
  zapytaniem referencyjnym. Zapytanie uznaje się za poprawne, jeżeli wszystkie jego komponenty, takie jak SELECT, WHERE,
  GROUP BY czy ORDER BY, odpowiadają komponentom zapytania wzorcowego.

- Execution Accuracy per SQL Hardness [@yu2018spider] - Dzieli zapytania SQL według poziomu złożoności na cztery
  kategorie:

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

- Component matching [@yu2018spider], [@pourreza2023dinsql] - Umożliwia analizę poprawności poszczególnych komponentów
  zapytania SQL takich jak:
    * SELECT,
    * WHERE,
    * GROUP BY,
    * ORDER BY,
    * JOIN,
    * nested SQL.

### Strategie agentów

Istnieje wiele strategii działania agenta, które różnią się sposobem generowania zapytań SQL, interakcją z bazą danych
oraz mechanizmami weryfikacji i poprawy błędów.
Niektóre z nich to:

- Plan and Solve [@wang2023planandsolve] - polega na rozdzieleniu procesu rozwiązywania problemu na dwa etapy -
  utworzenie planu rozwiązania i wykonanie zaplanowanych kroków. Model językowy najpierw generuje strukturę działania
  opisującą sposób rozwiązania zadania, a następnie realizuje kolejne kroki prowadzące do wygenerowania zapytania SQL.

- Chain-of-thought [@yao2022react] - polega na generowaniu rozwiązania poprzez sekwencję kroków rozumowania, bez
  bezpośredniej interakcji z narzędziami lub środowiskiem wykonawczym w trakcie procesu wnioskowania. Model językowy
  analizuje zapytanie użytkownika i generuje końcowe zapytanie SQL w jednym przebiegu.

- ReAct - Strategia ReAct (Reason and Act) [@yao2022react] łączy proces rozumowania z wykonywaniem akcji w środowisku
  zewnętrznym. Model językowy generuje kolejne kroki działania, wykonuje zapytania SQL lub operacje pomocnicze,
  analizuje wyniki ich wykonania oraz w razie potrzeby modyfikuje swoje decyzje.
  W implementacji systemu wykorzystany zostanie komponent SQL Agent frameworka LangChain [@langchainsqlagent], który
  domyślnie realizuje logikę działania zgodną z podejściem ReAct. Strategia ta stanowi zatem naturalny wariant bazowy
  dla systemów konwersacyjnych operujących na bazach danych.

### Strategie tworzenia promptów self-correction

- Gentle self-correction prompt [@pourreza2023dinsql] - nie zakłada błędu, lecz prosi model o sprawdzenie zapytania i
  ewentualne wskazanie problemów, podając wskazówki dotyczące elementów SQL do weryfikacji.
- Generic prompt [@pourreza2023dinsql] - Zakłada, że zapytanie jest błędne i poleca modelowi zidentyfikować oraz
  poprawić błędy.

Obie strategie zostały zaimplementowane w strategii zero-shot, czyli bez dodatkowego trenowania modelu na danych
specyficznych dla zadania.

## Opis rozwiązania

Projekt obejmuje implementację agentów wykorzystujących różne strategie oraz porównanie ich skuteczności.

### Zbiór danych

Do ewaluacji jakości wykorzystujemy zbiór Spider.
WikiSQL uznajemy za nieodpowiedni dla naszego projektu, skoncentrowanego na bardziej złożonych zapytaniach
analitycznych.
BIRD byłby również dobrym wyborem, natomiast decydujemy się na Spider: również bardzo popularny i mniejszy, co ułatwi
nam pracę na ograniczonych zasobach sprzętowych.

### Baza danych

Integrujemy agenta z SQLite: uruchamianią lokalnie, relacyjną bazą danych.
Jest to typowy wybór przy tego typu zadaniach, używana w popularnych zbiorach
danych [@yu2018spider], [@zhong2017seq2sql], [@li2023bird].

### Plan eksperymentów
TODO @Mariusz

Porównujemy skuteczność opisanych powyżej strategii Plan and Solve, Chain-of-thought oraz ReAct.
Dla każdego wariantu porównujemy także skuteczność różnych modeli językowych, wybraliśmy 2, stosunkowo małe modele,
aby być w stanie przeprowadzić czasochłonne eksperymenty na własnych zasobach sprzętowych:

* [Qwen/Qwen2.5-1.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct)
* [meta-llama/Llama-3.2-1B-Instruct](https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct)

## Implementacja

### Platforma

Uruchamiamy lokalnie modele dostępne na HuggingFace, korzystając z biblioteki transformers.
TODO @Mariusz

### Narzędzia

- langchain/langgraph [@langchainsqlagent], [@langgraphsqlagent] - biblioteki dostarczaczające rozwiązania dotyczące
  budowania promptów, agentów oraz zdolności rozumowania
- transformers - biblioteka ułatwiająca pracę z wielkimi modelami językowymi
- pytorch - biblioteka ogólnego przeznaczona do działań głębokiego uczenia oraz tensorów

### Przepływ działania agenta
TODO to chyba oddzielnie dla każdego wariantu

| Krok | Komponent         | Rola                                                          |
|-----:|-------------------|---------------------------------------------------------------|
|    1 | `list_tables`     | Pobranie listy tabel dostępnych w bazie danych.               |
|    2 | `select_tables`   | Wybór tabel istotnych dla pytania użytkownika.                |
|    3 | `get_schema`      | Pobranie schematu wybranych tabel.                            |
|    4 | `generate_query`  | Wygenerowanie zapytania SQLite `SELECT`.                      |
|    5 | `execute_query`   | Sprawdzenie bezpieczeństwa i wykonanie zapytania.             |
|    6 | `use_all_tables`  | Awaryjne użycie pełnego schematu, jeżeli wcześniejszy wybór tabel był niewystarczający. |
|    7 | `correct_query`   | Korekta zapytania na podstawie błędu.                         |
|    8 | `generate_answer` | Wygenerowanie krótkiej odpowiedzi dla użytkownika.            |

W trybie ewaluacyjnym agent może kończyć działanie po wygenerowaniu i ewentualnej korekcie SQL. Jest to potrzebne,
ponieważ metryki Spider oceniają zapytania oraz wyniki ich wykonania, a nie opisową odpowiedź w języku naturalnym.

### Wariant Chain-of-Thought
![Graf agenta Chain-of-Thought](img/cot.png)

Wariant Chain-of-Thought dodaje do generowania SQL krótki plan zapisany w bloku `<think>...</think>`. Plan ma zawierać
maksymalnie kilka krótkich informacji:

- istotne tabele,
- potrzebne złączenia,
- filtry, grupowanie, sortowanie lub agregacje,
- kolumny zwracane w wyniku.

Po planie model zwraca jedno zapytanie SQL `SELECT`. Implementacja wyodrębnia plan do osobnego pola diagnostycznego,
usuwa go z odpowiedzi modelu i zapisuje samo zapytanie SQL do ewaluacji. Dzięki temu można analizować sposób planowania
modelu, ale format predykcji pozostaje zgodny z wymaganiami benchmarku.

Tryb generowania może być wybierany z poziomu argumentów uruchomieniowych, na przykład jako tryb bazowy albo `cot`.

### Wariant Plan and Solve
![Graf agenta Plan and Solve](img/pas.png)

TODO @Mikołaj

### Wariant ReAct
![Graf agenta ReAct](img/react.png)

TODO @Mariusz

### Algorytm self-correction

Self-correction jest uruchamiany, gdy zapytanie nie wykona się poprawnie albo zostanie odrzucone przez walidator
bezpieczeństwa. Dla błędów typu `no such column` lub `no such table` agent może najpierw przełączyć się na pełny schemat
bazy, ponieważ pierwotnie wybrane tabele mogły być niewystarczające.

Następnie model otrzymuje:

- pytanie użytkownika,
- schemat bazy danych,
- poprzednie zapytanie SQL,
- komunikat błędu.

Na tej podstawie generuje poprawione zapytanie. Domyślnie liczba prób korekty jest ograniczona, na przykład do dwóch.
Pozwala to porównać wariant bez korekty, wariant z jedną próbą oraz wariant z większą liczbą prób.

### Struktura kodu źródłowego

* `agent` - pakiet z implementacją agenta
    * `common` - komponenty wspólne dla wszystkich wariantów agenta
      * `agent` - abstrakcyjna klasa bazowa agenta
      * `llm` - interfejs i konkretne adaptery do modeli językowych
      * `logging_config` - konfiguracja logowania
      * `modes` - definicja wariantów agenta
      * `nodes` - węzły grafu agenta
      * `state` - bazowy interfejs dla stanu agenta
      * `utils` - funkcje pomocnicze
    * `chain_of_thought` - implementacja wariantu Chain-of-Thought
      * `agent` - implementacja agenta
      * `nodes` - implementacja węzłów specyficznych dla tego wariantu
      * `state` - stan agenta specyficzny dla tego wariantu
    * `plan_and_solve` - implementacja wariantu Plan and Solve
      * `agent`, `nodes`, `state`
    * `react_like` - implementacja wariantu ReAct
      * `agent`, `nodes`, `state`
    * `agent` - budowanie agenta, skrypt demonstracyjny
    * `make_predictions` - skrypt do generowania predykcji dla zbioru Spider
* `eval` - moduł do ewaluacji wygenerowanych predykcji
    * kod zapożyczony z repozytorium https://github.com/taoyds/spider

## Instrukcja obsługi

* Do zarządzania projektem Python, zależnościami: [uv](https://docs.astral.sh/uv/)
* Do wykonywania komend: [just](https://github.com/casey/just)
* Wszystkie komendy opisane w `Justfile`
    * lista wszystkich dostępnych `just -l`
    * opis skryptów `just <komenda> --help`
    * komendy uruchamiane np. `just test`
* Instalacja zależności: `just install`
* Pobranie zbiorów danych `just datasets`
* Demonstracyjne uruchomienie agenta, z odpowiedzią w języku naturalnym: `just agent`
* Przeprowadzenie ewaluacji
    * `just make_predictions` - generuje za pomocą agenta zapytania SQL dla zapytań w języku naturalnym i baz danych ze
      zbioru Spider.
    * `just eval` - oblicza miary jakości porównując wygenerowane i wzorcowe zapytania SQL

## Testy
TODO opracowanie wyników benchmarków
TODO porównanie z literaturą


## Wnioski
TODO

## Bibliografia
