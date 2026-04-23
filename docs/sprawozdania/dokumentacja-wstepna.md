---
# pandoc sprawozdania.md --citeproc -o sprawozdania.pdf
lang: pl
bibliography: references.bib
nocite: "@*"
csl: ieee.csl
link-citations: true
---

# Dokumentacja wstępna

* Mikołaj Garbowski
* Mariusz Pakulski
* Paweł Łasica

Przeprowadzimy eksperymenty, w których porównamy skuteczność różnych strategii agenta generującego zapytania SQL.

## Wybrany zbiór danych

Do oceny jakości zaimplementowanego agenta wykorzystamy zbiór danych Spider [@yu2018spider].
Ten zbiór zawiera problemy, które dobrze odzwierciedlają realistyczne problemy analityczne.

Innym popularnym zbiorem do oceny jakości jest WikiSQL [@zhong2017seq2sql], natomiast zawarte w nim przykłady są raczej proste (obejmują pojedyncze tabele).

Kolejnym potencjalnym wyborem może być bardzo obszerny zbiór danych BIRD [@li2023bird], natomiast my decydujemy się na nieco mniejszy i bardzo popularny Spider [@shi2024survey].

## Wybrane miary jakości

- Execution accuracy [@shi2024survey] - Określa zgodność wyników zapytania wygenerowanego przez model z wynikami zapytania referencyjnego. Zapytanie uznaje się za poprawne jeśli po wykonaniu na bazie danych zwraca taki sam rezultat jak zapytanie wzorcowe. 

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


## Wybrane narzędzia

### Platforma
Za platformę roboczą przyjmujemy środowisko uruchomieniowe Google Colab. Dostarcza ona możliwość korzystania z dedykownych kart TPU/GPU oraz uruchamiania notatników Jupyter. W przypadku chęci rozwoju projektu o GUI dopuszczamy możliwość skonteneryzowania aplikacji i uruchamiania jej lokalnie.

### Główne narzędzia LLM
- langchain/langgraph [@langchainsqlagent], [@langgraphsqlagent] - biblioteki dostarczaczające rozwiązania dotyczące budowania promptów, agentów oraz zdolności rozumowania
- transformers - biblioteka ułatwiająca pracę z wielkimi modelami językowymi
- pytorch - biblioteka ogólnego przeznaczona do działań głębokiego uczenia oraz tensorów

### Baza danych
SQLite - urchamiania lokalnie relacyjna baza danych. Jest to typowy wybór przy tego typu zadaniach, używana w popularnych zbiorach danych [@yu2018spider], [@zhong2017seq2sql], [@li2023bird].

## Porównywane strategie agenta

- Plan and Solve [@wang2023planandsolve] - polega na rozdzieleniu procesu rozwiązywania problemu na dwa etapy - utworzenie planu rozwiązania i wykonanie zaplanowanych kroków. Model językowy najpierw generuje strukturę działania opisującą sposób rozwiązania zadania, a następnie realizuje kolejne kroki prowadzące do wygenerowania zapytania SQL.

- Chain-of-thought [@yao2022react] - polega na generowaniu rozwiązania poprzez sekwencję kroków rozumowania, bez bezpośredniej interakcji z narzędziami lub środowiskiem wykonawczym w trakcie procesu wnioskowania. Model językowy analizuje zapytanie użytkownika i generuje końcowe zapytanie SQL w jednym przebiegu.

- ReAct - Strategia ReAct (Reason and Act) [@yao2022react] łączy proces rozumowania z wykonywaniem akcji w środowisku zewnętrznym. Model językowy generuje kolejne kroki działania, wykonuje zapytania SQL lub operacje pomocnicze, analizuje wyniki ich wykonania oraz w razie potrzeby modyfikuje swoje decyzje. 
W implementacji systemu wykorzystany zostanie komponent SQL Agent frameworka LangChain [@langchainsqlagent], który domyślnie realizuje logikę działania zgodną z podejściem ReAct. Strategia ta stanowi zatem naturalny wariant bazowy dla systemów konwersacyjnych operujących na bazach danych.

## Porównywane strategie tworzenia promptów self-correction

- Gentle self-correction prompt [@pourreza2023dinsql] - nie zakłada błędu, lecz prosi model o sprawdzenie zapytania i ewentualne wskazanie problemów, podając wskazówki dotyczące elementów SQL do weryfikacji.
- Generic prompt [@pourreza2023dinsql] - Zakłada, że zapytanie jest błędne i poleca modelowi zidentyfikować oraz poprawić błędy.

Obie strategie zostały zaimplementowane w strategii zero-shot, czyli bez dodatkowego trenowania modelu na danych specyficznych dla zadania.

## Wybrane modele LLM
Porównamy ze sobą modele o otwartych wagach dostępne na platformie HuggingFace.
Ograniczymy się do mniejszych modeli, możliwych do uruchomienia lokalnie lub na darmowych platformach.
Wstępnie planujemy porównać model z rodziny Llama [@touvron2024llama3] oraz Bielika.

## Przegląd
Zagadnienie wykorzystania modeli językowych do zastosowań z zakresu analizy danych i zadań BI dla baz relacyjnych jest szeroko badane.
Typowe rozwiązania obejmują podejścia typu text-to-sql, a także text-to-python i text-to-dsl jako popularne alternatywy do obrabiania ustrukturyzowanych danych [@tian2025tableagents].

W celu zrozumienia struktury tabeli, typowo dane tabelaryczne są serializowane do jakiejś postaci tekstowej (markdown, json, itp.) co pozwala na bezpośrednie umieszczenie danych w prompcie, natomiast wyzwaniem jest ograniczony rozmiar kontekstu.
Badane są także alternatywne podejścia, np. przetwarzanie obrazu tabeli modelami typu VLM, przetwarzanie tabeli w postaci struktur grafowych, a także szczególnie interesujące: traktowanie danych tableraycznych jako odrędnej modalności.
Przykładem takiego rozwiązania jest TableGPT2 [@su2024tablegpt2], które łączy koder danych tabelarycznych, produkujący semantyczne osadzenia dla kolumn tabeli, połączony z modelem językowym typu tylko-dekoder wykorzystującym te osadzenia oraz prompt użytkownika.

Sposobem na rozwiązanie problemu z rozmiarem kontekstu, wzbogacenie promptu użytkownika o wiedzę domenową, a także wydobycie informacji o schemacie bazy danych, stosowane są metody znane z zastosowań typu RAG, zadania *retrieval*.

Często stosowane zbiory benchmarkowe oraz typowe miary oceny jakości zostały opisane we wcześniejszych punktach.

## Bibliografia
