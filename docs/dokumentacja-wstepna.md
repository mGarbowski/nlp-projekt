# Dokumentacja wstępna

Przeprowadzimy eksperymenty, w których porównamy skuteczność różnych strategii agenta generującego zapytania SQL.

## Wbór zbioru danych

Do oceny jakości zaimplementowanego agenta wykorzystamy zbiór danych Spider[^3].
Ten zbiór zawiera problemy, które dobrze odzwierciedlają realistyczne problemy analityczne.

Innym popularnym zbiorem do oceny jakości jest WikiSQL[^5], natomiast zawarte w nim przykłady są raczej proste (obejmują pojedyncze tabele).

Kolejnym potencjalnym wyborem może być bardzo obszerny zbiór danych BIRD[^4], natomiast my decydujemy się na nieco mniejszy i bardzo popularny Spider. [^1]

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

## Krótkie streszczenie pomysłów z opracowanych artykułów
TODO [^10] [^11]

## Bibliografia
[^1]: [Shi, Y., Tang, et al. _A Survey on Employing Large Language Models for Text-to-SQL Tasks_. arXiv:2407.15186](https://arxiv.org/abs/2407.15186).
[^2]: [Yao, S., Zhao, J., et al. _ReAct: Synergizing Reasoning and Acting in Language Models_. arXiv:2210.03629](https://arxiv.org/abs/2210.03629).
[^3]: [Yu, T., et al. _Spider: A Large-Scale Human-Labeled Dataset for Complex and Cross-Domain Semantic Parsing and Text-to-SQL Task_. arXiv:1809.08887](https://arxiv.org/abs/1809.08887).
[^4]: [Li, J., Hui, B., et al. _Can LLM Already Serve as a Database Interface? A Big Bench for Large-Scale Database Grounded Text-to-SQLs_. arXiv:2305.03111](https://arxiv.org/abs/2305.03111).
[^5]: [Zhong, V., Xiong, C., Socher, R. _Seq2SQL: Generating Structured Queries from Natural Language using Reinforcement Learning_. arXiv:1709.00103](https://arxiv.org/abs/1709.00103).
[^6]: [Pourreza, M., Rafiei, D. _DIN-SQL: Decomposed In-Context Learning of Text-to-SQL with Self-Correction_. arXiv:2304.11015](https://arxiv.org/abs/2304.11015).
[^7]: [Bommasani, R., et al.  On the Opportunities and Risks of Foundation Models](https://arxiv.org/abs/2108.07258)
[^8]: [OpenAI  GPT-4 Technical Report](https://arxiv.org/abs/2303.08774)
[^9]: [Touvron, H., et al.  Llama 3: Open Foundation and Instruction Models Meta AI  2024](https://arxiv.org/abs/2302.13971)
[^10]: [Tian, J., et al. Toward Real-World Table Agents: Capabilities, Workflows, and Design Principles for LLM-based Table Intelligence](https://arxiv.org/pdf/2507.10281)
[^11]: [Su, A., et al. TableGPT2: A Large Multimodal Model with Tabular Data Integration](https://arxiv.org/abs/2411.02059)
