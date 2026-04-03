---
# pandoc dokumentacja-wstepna.md --citeproc -o dokumentacja-wstepna.pdf
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

## Wbór zbioru danych

Do oceny jakości zaimplementowanego agenta wykorzystamy zbiór danych Spider [@yu2018spider].
Ten zbiór zawiera problemy, które dobrze odzwierciedlają realistyczne problemy analityczne.

Innym popularnym zbiorem do oceny jakości jest WikiSQL [@zhong2017seq2sql], natomiast zawarte w nim przykłady są raczej proste (obejmują pojedyncze tabele).

Kolejnym potencjalnym wyborem może być bardzo obszerny zbiór danych BIRD [@li2023bird], natomiast my decydujemy się na nieco mniejszy i bardzo popularny Spider [@shi2024survey].

## Wybrane miary jakości

Wybrano takie miary jakości jak:

- execution accuracy - określa zgodność wyników zapytania wygenerowanego przez model z wynikami zapytania referencyjnego. Zapytanie uznaje się za poprawne jeśli po wykonaniu na bazie danych zwraca taki sam rezultat jak zapytanie wzorcowe.

- exact set match accuracy - polega ona na porównaniu struktury zapytania SQL wygenerowanego przez model z zapytaniem referencyjnym. Zapytanie uznaje się za poprawne, jeżeli wszystkie jego komponenty, takie jak SELECT, WHERE, GROUP BY czy ORDER BY, odpowiadają komponentom zapytania wzorcowego.

- execution Accuracy per SQL Hardness - dzieli on zapytania SQL według poziomu złożoności na cztery kategorie:

    * easy,
    * medium,
    * hard,
    * extra hard.

    Klasyfikacja ta opiera się na analizie struktury     zapytania SQL, w szczególności na obecności:
    
    * złączeń tabel (JOIN),
    * grupowania danych (GROUP BY),
    * zapytań zagnieżdżonych,
    * operacji zbiorowych,
    * liczby warunków i agregacji.


## Wybrane narzędzia

### Platforma
Za platformę roboczą przyjmujemy środowisko uruchomieniowe Google Colab. Dostarcza ona możliwość korzystania z dedykownych kart TPU/GPU oraz uruchamiania notatników Jupyter. W przypadku chęci rozwoju projektu o GUI dopuszczamy możliwość skonteneryzowania aplikacji i uruchamiania jej lokalnie.

### Główne narzędzia LLM
1. langchain/langgraph - biblioteki dostarczaczające rozwiązania dotyczące budowania promptów, agentów oraz zdolności rozumowania 
2. transformers - biblioteka ułatwiająca pracę z wielkimi modelami językowymi
3. pytorch - biblioteka ogólnego przeznaczona do działań głębokiego uczenia oraz tensorów

### Baza danych
SQLite - urchamiania lokalnie relacyjna baza danych. Jest to typowy wybór przy tego typu zadaniach, używana w popularnych zbiorach danych.

## Porównywane strategie agenta
ReAct - Strategia ReAct (Reason and Act) łączy proces rozumowania z wykonywaniem akcji w środowisku zewnętrznym. Model językowy generuje kolejne kroki działania, wykonuje zapytania SQL lub operacje pomocnicze, analizuje wyniki ich wykonania oraz w razie potrzeby modyfikuje swoje decyzje.

Chain-of-thought - polega na generowaniu rozwiązania poprzez sekwencję kroków rozumowania, bez bezpośredniej interakcji z narzędziami lub środowiskiem wykonawczym w trakcie procesu wnioskowania. Model językowy analizuje zapytanie użytkownika i generuje końcowe zapytanie SQL w jednym przebiegu.

Plan and Solve - polega na rozdzieleniu procesu rozwiązywania problemu na dwa etapy - utworzenie planu rozwiązania i wykonanie zaplanowanych kroków. Model językowy najpierw generuje strukturę działania opisującą sposób rozwiązania zadania, a następnie realizuje kolejne kroki prowadzące do wygenerowania zapytania SQL.
    

## Wybrane modele LLM
Porównamy ze sobą modele o otwartych wagach dostępne na platformie HuggingFace.
Ograniczymy się do mniejszych modeli, możliwych do uruchomienia lokalnie lub na darmowych platformach.
Wstępnie planujemy porównać model z rodziny Llama oraz Bielika.

## Przegląd
Zagadnienie wykorzystania modeli językowych do zastosowań z zakresu analizy danych i zadań BI dla baz relacyjnych jest szeroko badane.
Typowe rozwiązania obejmują podejścia typu text-to-sql, a także text-to-python i text-to-dsl jako popularne alternatywy do obrabiania ustrukturyzowanych danych [@tian2025tableagents].

W celu zrozumienia struktury tabeli, typowo dane tabelaryczne są serializowane do jakiejś postaci tekstowej (markdown, json, itp.) co pozwala na bezpośrednie umieszczenie danych w prompcie, natomiast wyzwaniem jest ograniczony rozmiar kontekstu.
Badane są także alternatywne podejścia, np. przetwarzanie obrazu tabeli modelami typu VLM, przetwarzanie tabeli w postaci struktur grafowych, a także szczególnie interesujące: traktowanie danych tableraycznych jako odrędnej modalności.
Przykładem takiego rozwiązania jest TableGPT2 [@su2024tablegpt2], które łączy koder danych tabelarycznych, produkujący semantyczne osadzenia dla kolumn tabeli, połączony z modelem językowym typu tylko-dekoder wykorzystującym te osadzenia oraz prompt użytkownika.

Sposobem na rozwiązanie problemu z rozmiarem kontekstu, wzbogacenie promptu użytkownika o wiedzę domenową, a także wydobycie informacji o schemacie bazy danych, stosowane są metody znane z zastosowań typu RAG, zadania *retrieval*.

Często stosowane zbiory benchmarkowe oraz typowe miary oceny jakości zostały opisane we wcześniejszych punktach.

## Bibliografia
