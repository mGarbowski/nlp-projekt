# Benchmarki, metryki ewaluacji oraz uzasadnienie architektury systemu Text-to-SQL

W niniejszym projekcie wykorzystano przegląd literatury dotyczącej zastosowania dużych modeli językowych (LLM) do konwersji języka naturalnego na zapytania SQL. W szczególności analizie poddano prace poświęcone benchmarkom, metrykom ewaluacji oraz typowym błędom pojawiającym się w systemach Text-to-SQL opartych na promptingowych metodach pracy z LLM [^1], [^6].

Analiza literatury wskazuje, że zadanie Text-to-SQL nie sprowadza się wyłącznie do bezpośredniego przekształcenia pytania użytkownika w zapytanie SQL. Najczęstsze błędy modeli językowych dotyczą nie tylko końcowej składni zapytania, ale również wcześniejszych etapów rozumowania, takich jak niepoprawne dopasowanie elementów schematu bazy danych, błędne generowanie złączeń tabel, niewłaściwe użycie agregacji i grupowania oraz problemy z obsługą zapytań zagnieżdżonych [^6].

Z tego względu w projekcie przyjęto założenie, że skuteczny system Text-to-SQL powinien mieć **architekturę wieloetapową**, obejmującą co najmniej:

- identyfikację istotnych elementów schematu bazy danych (**schema linking**),
- określenie struktury i poziomu złożoności zapytania,
- wygenerowanie właściwego zapytania SQL,
- mechanizm automatycznej korekty błędów (**self-correction**).

Takie podejście jest zgodne z aktualnymi kierunkami badań i pozwala lepiej analizować źródła błędów niż proste podejście typu „pytanie → model → SQL”.

---

## Wybrane benchmarki i metryki ewaluacyjne

W literaturze wyróżnia się kilka podstawowych metryk oceny systemów Text-to-SQL. W niniejszym projekcie zdecydowano się na wybór metryk, które najlepiej odpowiadają celom pracy, a więc ocenie poprawności generowanych zapytań SQL, ich skuteczności na złożonych zapytaniach analitycznych oraz analizie mechanizmu self-correction.

## Wybrane metryki ewaluacyjne z literatury [^1]

### 1. Execution Accuracy

Metryka **Execution Accuracy** określa zgodność wyników zapytania wygenerowanego przez model z wynikami zapytania referencyjnego (_gold SQL_). Zapytanie uznaje się za poprawne, jeżeli po wykonaniu na bazie danych zwraca taki sam rezultat jak zapytanie wzorcowe.

Metryka ta jest szczególnie istotna w systemach Text-to-SQL, ponieważ mierzy rzeczywistą poprawność działania systemu z perspektywy użytkownika. W praktyce możliwe jest bowiem wygenerowanie zapytania o innej strukturze niż zapytanie referencyjne, które mimo to zwraca poprawny wynik.

Należy jednak zaznaczyć, że metryka ta może prowadzić do tzw. **fałszywie pozytywnych ocen**, ponieważ dwa różne zapytania SQL mogą zwrócić ten sam rezultat mimo odmiennej logiki, np. w przypadkach obejmujących wartości NULL lub szczególne własności danych.

---

### 2. Exact Set Match Accuracy

Metryka **Exact Set Match Accuracy** (Exact Match) polega na porównaniu struktury zapytania SQL wygenerowanego przez model z zapytaniem referencyjnym. Zapytanie uznaje się za poprawne, jeżeli wszystkie jego komponenty, takie jak SELECT, WHERE, GROUP BY czy ORDER BY, odpowiadają komponentom zapytania wzorcowego.

Metryka ta pozwala ocenić zgodność logicznej struktury wygenerowanego zapytania z rozwiązaniem referencyjnym. Jej ograniczeniem jest jednak to, że różne zapytania SQL mogą być semantycznie równoważne i zwracać identyczny wynik, mimo że ich składnia nie jest identyczna.

Z tego względu Exact Match traktowane będzie w projekcie jako metryka uzupełniająca wobec Execution Accuracy.

---

## Metryki niewykorzystane w projekcie

W literaturze opisano również inne metryki ewaluacyjne, które nie zostały zastosowane w niniejszym projekcie ze względu na ich złożoność implementacyjną lub brak bezpośredniej przydatności w analizowanym systemie.

### 1. Test Suite Accuracy

Metryka **Test Suite Accuracy** wymaga generowania wielu instancji baz danych oraz zestawów testowych o wysokim pokryciu kodu SQL. Ze względu na wysokie wymagania implementacyjne i obliczeniowe metryka ta nie została zastosowana w niniejszym projekcie.

---

### 2. Valid Efficiency Score (VES)

W literaturze, w szczególności w benchmarku **BIRD**, zaproponowano metrykę **Valid Efficiency Score (VES)**, która uwzględnia zarówno poprawność zapytania SQL, jak i jego wydajność obliczeniową [^4].

Metryka ta jest szczególnie istotna w systemach pracujących na dużych zbiorach danych i w środowiskach produkcyjnych, gdzie czas wykonania zapytania ma istotne znaczenie. W niniejszym projekcie metryka ta nie została zastosowana, ponieważ analizowane bazy danych mają stosunkowo niewielki rozmiar, a głównym celem pracy jest ocena poprawności generowanych zapytań SQL, a nie ich wydajności.

---

### 3. ESM+

Metryka **ESM+** stanowi rozszerzenie Exact Match o dodatkowe reguły obejmujące bardziej zaawansowane aspekty zapytań SQL, takie jak JOIN, DISTINCT czy aliasy tabel.

Ze względu na złożoność implementacyjną oraz brak konieczności tak szczegółowej analizy strukturalnej, metryka ta nie została wykorzystana w niniejszym projekcie.

---

## Metryki wykorzystane z benchmarku Spider [^3]

Oprócz standardowych metryk ewaluacyjnych, w projekcie wykorzystane zostaną również metryki zaimplementowane w benchmarku **Spider**, który stanowi jeden z najważniejszych standardów badawczych w dziedzinie Text-to-SQL.

### 1. Execution Accuracy per SQL Hardness

Benchmark Spider klasyfikuje zapytania SQL według poziomu złożoności na cztery kategorie:

- easy,
- medium,
- hard,
- extra hard.

Klasyfikacja ta opiera się na analizie struktury zapytania SQL, w szczególności na obecności:

- złączeń tabel (JOIN),
- grupowania danych (GROUP BY),
- zapytań zagnieżdżonych,
- operacji zbiorowych,
- liczby warunków i agregacji.

Metryka **Execution Accuracy per SQL Hardness** pozwala ocenić skuteczność systemu w zależności od poziomu złożoności zapytań SQL. Jest ona szczególnie istotna w kontekście wymagań projektu dotyczących obsługi złożonych zapytań analitycznych.

---

### 2. Partial Matching

Metryka **Partial Matching** umożliwia analizę poprawności poszczególnych komponentów zapytania SQL, takich jak:

- SELECT,
- WHERE,
- GROUP BY,
- ORDER BY,
- JOIN,
- nested SQL.

Metryka ta ma duże znaczenie diagnostyczne, ponieważ pozwala określić, które elementy zapytań sprawiają modelowi największą trudność. Jest to szczególnie istotne w świetle analiz błędów opisywanych w literaturze, gdzie najczęstsze problemy dotyczą właśnie **schema linking**, **JOIN**, **GROUP BY** oraz zapytań zagnieżdżonych [^6].

---

## Metryki Spider niewykorzystane w projekcie

Niektóre metryki dostępne w benchmarku Spider nie zostały wykorzystane w niniejszym projekcie ze względu na ich ograniczoną przydatność lub zbyt wysoki poziom szczegółowości.

W szczególności nie wykorzystano:

- **SQL Keyword Analysis** — metryka analizująca szczegółowe użycie słów kluczowych SQL, przydatna głównie w badaniach modelowych,
- **F1 per Component** — metryka stosowana głównie do szczegółowej oceny modeli uczenia maszynowego na poziomie komponentów zapytania,
- **Advanced Test Suite Metrics** — metryki wymagające bardziej złożonej infrastruktury testowej.

---

## Dodatkowe metryki diagnostyczne

### 1. Valid SQL Rate

W kontekście analizy mechanizmu **self-correction** zastosowana zostanie dodatkowa metryka diagnostyczna: **Valid SQL Rate**.

Metryka ta określa procent zapytań SQL wygenerowanych przez system, które zostały poprawnie wykonane przez system zarządzania bazą danych bez błędów składniowych lub semantycznych.

Choć poprawne wykonanie zapytania nie oznacza jeszcze poprawności jego wyniku, metryka ta jest przydatna jako wskaźnik stabilności systemu oraz skuteczności mechanizmu automatycznej korekty błędów.

---

### 2. Analiza typów błędów

Na podstawie literatury [^6] w projekcie planowana jest również jakościowa analiza typów błędów pojawiających się w generowanych zapytaniach SQL. W szczególności analizowane będą następujące klasy błędów:

- błędy **schema linking**,
- błędy związane z **JOIN**,
- błędy związane z **GROUP BY** i agregacjami,
- błędy dotyczące zapytań zagnieżdżonych,
- błędy składniowe (invalid SQL),
- inne błędy logiczne, np. brakujące warunki, zbędne DISTINCT lub niepoprawne sortowanie.

Taki podział wynika bezpośrednio z obserwacji opisanych w literaturze i pozwoli dokładniej ocenić, które elementy generacji SQL sprawiają największe trudności badanym modelom i strategiom planowania.

---

# Wybór benchmarku

W niniejszym projekcie wykorzystany zostanie benchmark:

## Spider 1.0 

Benchmark **Spider 1.0** stanowi obecnie jeden z najważniejszych standardów ewaluacji systemów Text-to-SQL w literaturze naukowej . [^3]

Dataset ten został wybrany ze względu na następujące właściwości:

- obsługuje złożone operacje SQL, takie jak:
    - JOIN,
    - GROUP BY,
    - zapytania zagnieżdżone,
    - agregacje,
- zawiera wiele baz danych o różnej strukturze,
- jest szeroko wykorzystywany w badaniach naukowych,
- umożliwia ocenę systemów w kontekście złożonych zapytań analitycznych.

Wybór benchmarku Spider jest zgodny z wymaganiami projektu dotyczącymi analizy zdolności systemu do obsługi złożonych zapytań SQL.

Dodatkowym argumentem za wykorzystaniem benchmarku Spider jest fakt, że stanowi on standardowe środowisko badawcze dla analiz błędów związanych z problemami takimi jak schema linking, błędne JOIN-y, niewłaściwe użycie agregacji czy trudności z zapytaniami zagnieżdżonymi [^6].

---

## Benchmarki niewykorzystane w projekcie

W literaturze opisano również inne benchmarki Text-to-SQL, takie jak:

- WikiSQL [^5],
- BIRD [^4],
- Dr.Spider,
- Spider 2.0,
- Science Benchmark.

Benchmark **WikiSQL** nie został wybrany jako główny dataset, ponieważ zawiera przede wszystkim proste zapytania SQL i nie obejmuje wielu złożonych operacji analitycznych, takich jak złączenia tabel czy zapytania zagnieżdżone.

Może on jednak zostać wykorzystany pomocniczo do porównania skuteczności systemu na prostszych zapytaniach SQL.

Pozostałe benchmarki, takie jak BIRD czy Spider 2.0, wymagają większych zasobów obliczeniowych oraz bardziej rozbudowanej infrastruktury eksperymentalnej, co wykracza poza zakres niniejszego projektu.

---

# Uzasadnienie architektury wieloetapowej systemu

Analiza literatury wskazuje, że proste podejście typu few-shot prompting nie zapewnia satysfakcjonującej skuteczności w przypadku bardziej złożonych zapytań SQL, szczególnie takich, które wymagają poprawnego schema linking, wielu złączeń tabel, grupowania lub zapytań zagnieżdżonych [^6].

W związku z tym w niniejszym projekcie przyjęto założenie, że generacja zapytań SQL powinna zostać rozbita na kilka etapów odpowiadających najważniejszym podproblemom zadania Text-to-SQL. W szczególności zakłada się uwzględnienie następujących komponentów:

1. **schema linking** — identyfikacja tabel, kolumn oraz wartości istotnych dla pytania użytkownika,
2. **planowanie lub dekompozycja zapytania** — określenie typu i struktury zapytania, np. czy wymaga ono złączeń, agregacji lub zapytania zagnieżdżonego,
3. **generacja właściwego SQL**,
4. **self-correction** — automatyczna korekta błędnych zapytań na podstawie błędów wykonania lub heurystyk kontrolnych.

Takie podejście znajduje potwierdzenie w literaturze i pozwala na bardziej kontrolowaną analizę zachowania modeli językowych niż generowanie zapytania SQL w pojedynczym kroku.

---

# Wybór strategii planowania zapytań w agencie SQL

W projektowanym systemie konwersacyjnego agenta SQL zdecydowano się na porównanie trzech strategii generowania zapytań: **Chain-of-Thought (CoT)**, **ReAct (Reason and Act)** oraz **Plan-and-Solve**. Strategie te reprezentują odmienne podejścia do rozumowania i podejmowania decyzji przez model językowy w zadaniach konwersji języka naturalnego na zapytania SQL (Text-to-SQL).

W literaturze naukowej [^2], [^6] strategie te są powszechnie stosowane jako podstawowe mechanizmy planowania i rozwiązywania zadań wymagających wieloetapowego rozumowania oraz interakcji z zewnętrznymi narzędziami lub źródłami danych. Ich wybór pozwala na przeprowadzenie kontrolowanego eksperymentu, w którym zmieniana jest jedynie metoda planowania zapytań, przy zachowaniu tej samej architektury systemu oraz tych samych danych wejściowych.

---

## 1. Chain-of-Thought (CoT)

Strategia **Chain-of-Thought** polega na generowaniu rozwiązania poprzez sekwencję kroków rozumowania, bez bezpośredniej interakcji z narzędziami lub środowiskiem wykonawczym w trakcie procesu wnioskowania. Model językowy analizuje zapytanie użytkownika i generuje końcowe zapytanie SQL w jednym przebiegu.

W kontekście systemów Text-to-SQL strategia ta pełni rolę punktu odniesienia, ponieważ reprezentuje najprostszy wariant działania systemu, w którym model generuje zapytanie wyłącznie na podstawie swojej wiedzy wewnętrznej oraz opisu schematu bazy danych.

Zaletą tego podejścia jest prostota implementacji oraz niskie koszty obliczeniowe. Ograniczeniem jest natomiast brak bezpośredniego mechanizmu weryfikacji poprawności generowanego zapytania w trakcie jego tworzenia, co może prowadzić do błędów logicznych, błędów doboru tabel i kolumn oraz problemów z bardziej złożonymi strukturami SQL.

---

## 2. ReAct (Reason and Act)

Strategia **ReAct (Reason and Act)** łączy proces rozumowania z wykonywaniem akcji w środowisku zewnętrznym. Model językowy generuje kolejne kroki działania, wykonuje zapytania SQL lub operacje pomocnicze, analizuje wyniki ich wykonania oraz w razie potrzeby modyfikuje swoje decyzje.

W praktyce oznacza to iteracyjny proces obejmujący:

1. analizę zapytania użytkownika,
2. wybór odpowiednich narzędzi,
3. wygenerowanie i wykonanie zapytania SQL,
4. analizę wyniku lub komunikatu błędu,
5. ewentualną poprawę zapytania.

Strategia ta jest szczególnie istotna w systemach agentowych, ponieważ umożliwia dynamiczne reagowanie na błędy i wykorzystanie informacji zwrotnej z systemu bazodanowego. W świetle literatury podejście ReAct zwiększa ugruntowanie odpowiedzi w danych zewnętrznych i ogranicza ryzyko halucynacji, choć może prowadzić do zapętleń lub błędów w doborze kolejnych akcji [^2].

W implementacji systemu wykorzystany zostanie komponent **SQL Agent** frameworka LangChain, który domyślnie realizuje logikę działania zgodną z podejściem ReAct. Strategia ta stanowi zatem naturalny wariant bazowy dla systemów konwersacyjnych operujących na bazach danych.

---

## 3. Plan-and-Solve

Strategia **Plan-and-Solve** polega na rozdzieleniu procesu rozwiązywania problemu na dwa etapy:

1. utworzenie planu rozwiązania,
2. wykonanie zaplanowanych kroków.

Model językowy najpierw generuje strukturę działania opisującą sposób rozwiązania zadania, a następnie realizuje kolejne kroki prowadzące do wygenerowania zapytania SQL.

Podejście to jest szczególnie przydatne w przypadku złożonych zapytań analitycznych obejmujących:

- złączenia tabel,
- agregacje i grupowanie,
- zapytania zagnieżdżone,
- wieloetapowe filtrowanie i sortowanie.

Rozdzielenie etapu planowania od etapu wykonania pozwala na bardziej uporządkowane rozumowanie oraz zmniejsza ryzyko błędów logicznych w przypadku złożonych struktur SQL. Strategia ta dobrze wpisuje się również w wnioski z literatury wskazujące, że rozbicie zadania Text-to-SQL na podproblemy może istotnie poprawiać skuteczność systemu [^6].

---

## Uzasadnienie wyboru strategii

Wybór strategii Chain-of-Thought, ReAct oraz Plan-and-Solve wynika z kilku czynników metodologicznych i praktycznych.

Po pierwsze, strategie te reprezentują trzy różne modele działania systemu:

- generowanie rozwiązania w jednym przebiegu (Chain-of-Thought),
- iteracyjne rozumowanie z wykorzystaniem informacji zwrotnej i narzędzi (ReAct),
- planowanie wieloetapowego rozwiązania przed jego wykonaniem (Plan-and-Solve).

Po drugie, metody te są szeroko opisane w literaturze naukowej dotyczącej systemów agentowych i Text-to-SQL, co umożliwia odniesienie wyników eksperymentów do istniejących badań [^2], [^6].

Po trzecie, strategie te można stosunkowo łatwo zaimplementować w ramach jednego systemu opartego na frameworku LangChain, co pozwala zachować spójność architektury oraz porównywalność wyników.

Wreszcie, liczba trzech strategii została uznana za optymalną z punktu widzenia przeprowadzenia eksperymentów: umożliwia uchwycenie istotnych różnic między podejściami bez nadmiernego zwiększania złożoności systemu.

---

## Zakres eksperymentu

W ramach projektu każda z opisanych strategii zostanie zaimplementowana w tym samym środowisku systemowym, obejmującym:

- framework LangChain,
- relacyjną bazę danych SQLite,
- zbiór danych Spider,
- identyczne dane wejściowe i procedurę ewaluacji.

W zależności od ostatecznej konfiguracji eksperymentalnej porównanie strategii może być prowadzone dla jednego lub dwóch modeli językowych. Zmienną niezależną w eksperymencie będzie strategia planowania zapytania, natomiast pozostałe elementy systemu zostaną utrzymane możliwie stałe.

Pozwoli to na przeprowadzenie kontrolowanego porównania skuteczności systemu w zależności od sposobu generowania zapytań SQL.

---


# Wybór modeli językowych

W niniejszym projekcie zdecydowano się na wykorzystanie dwóch modeli językowych reprezentujących odmienne podejścia do implementacji systemów opartych na dużych modelach językowych (LLM):

- model dostępny poprzez API — **GPT-4o**
- model open-source uruchamiany lokalnie — **Llama 3**

Celem takiego wyboru jest umożliwienie przeprowadzenia eksperymentu porównawczego pomiędzy modelami reprezentującymi dwa najważniejsze paradygmaty wdrożeń systemów opartych na LLM: modele komercyjne dostępne jako usługa oraz modele open-source uruchamiane lokalnie.

Takie podejście jest zgodne z aktualnymi kierunkami badań w dziedzinie systemów opartych na LLM, w których analizuje się różnice pomiędzy modelami komercyjnymi i open-source w zakresie jakości generowania kodu, kosztów wdrożenia oraz możliwości lokalnego uruchamiania modeli [^7].

---

## Uzasadnienie wyboru modelu GPT-4o

Model **GPT-4o** został wybrany jako reprezentant nowoczesnych modeli językowych dostępnych poprzez API, które charakteryzują się wysoką skutecznością w zadaniach wymagających rozumowania oraz generowania kodu.

Badania wykazują, że modele z rodziny GPT-4 osiągają wysokie wyniki w zadaniach wymagających rozumowania, generowania kodu oraz pracy z danymi tabelarycznymi, co czyni je odpowiednimi do zastosowań takich jak konwersja języka naturalnego na zapytania SQL [^8].

W szczególności modele tej klasy wykazują wysoką skuteczność w zadaniach wymagających wieloetapowego rozumowania oraz interakcji z narzędziami zewnętrznymi, co stanowi podstawę działania agentów typu ReAct i Plan-and-Solve [^2].

Wybór modelu GPT-4o wynika z następujących przesłanek:

- wysoka skuteczność w zadaniach reasoning i code generation,
- stabilność działania i szerokie zastosowanie w systemach produkcyjnych,
- dostępność poprzez API umożliwiająca integrację z frameworkami agentowymi,
- wysoka jakość generowanych odpowiedzi w zadaniach wymagających pracy z bazami danych.

---

## Uzasadnienie wyboru modelu Llama 3

Model **Llama 3** został wybrany jako reprezentant nowoczesnych modeli open-source, które mogą być uruchamiane lokalnie i dostosowywane do konkretnych zastosowań.

Modele open-source, takie jak Llama, odgrywają istotną rolę w badaniach nad systemami opartymi na LLM, ponieważ umożliwiają pełną kontrolę nad środowiskiem wykonawczym, modyfikację parametrów modelu oraz uruchamianie systemu bez zależności od usług zewnętrznych [^9].

W literaturze podkreśla się, że modele open-source stanowią istotną alternatywę dla modeli komercyjnych, szczególnie w kontekście badań eksperymentalnych, wdrożeń lokalnych oraz analizy kosztów systemów opartych na LLM [^7].

Wybór modelu Llama 3 wynika z następujących przesłanek:

- możliwość lokalnego uruchamiania modelu,
- dostęp do parametrów modelu i możliwość jego modyfikacji,
- rosnąca popularność modeli open-source w zastosowaniach badawczych,
- możliwość analizy kompromisu pomiędzy jakością modelu a kosztami wdrożenia.

---

## Uzasadnienie wyboru pary modeli (API vs open-source)

Wybór jednego modelu komercyjnego oraz jednego modelu open-source pozwala na przeprowadzenie eksperymentu odpowiadającego rzeczywistym scenariuszom wdrożeniowym systemów opartych na LLM.

W literaturze podkreśla się, że skuteczność systemów Text-to-SQL zależy nie tylko od architektury systemu, ale również od właściwości zastosowanego modelu językowego, w tym jego zdolności do rozumowania, generowania kodu oraz obsługi złożonych zapytań SQL [^1].

Porównanie modeli o różnych charakterystykach umożliwia analizę:

- jakości generowanych zapytań SQL,
- stabilności działania systemu,
- skuteczności mechanizmów self-correction,
- kosztów wdrożenia systemu.

Takie podejście jest zgodne z metodologią badań eksperymentalnych w dziedzinie systemów Text-to-SQL, gdzie porównuje się różne modele językowe przy zachowaniu tej samej architektury systemu i danych testowych [^1].
## Literatura

[^1]: [Shi, Y., Tang, et al. _A Survey on Employing Large Language Models for Text-to-SQL Tasks_. arXiv:2407.15186](https://arxiv.org/abs/2407.15186).  
[^2]: [Yao, S., Zhao, J., et al. _ReAct: Synergizing Reasoning and Acting in Language Models_. arXiv:2210.03629](https://arxiv.org/abs/2210.03629).  
[^3]: [Yu, T., et al. _Spider: A Large-Scale Human-Labeled Dataset for Complex and Cross-Domain Semantic Parsing and Text-to-SQL Task_. arXiv:1809.08887](https://arxiv.org/abs/1809.08887).  
[^4]: [Li, J., Hui, B., et al. _Can LLM Already Serve as a Database Interface? A Big Bench for Large-Scale Database Grounded Text-to-SQLs_. arXiv:2305.03111](https://arxiv.org/abs/2305.03111).  
[^5]: [Zhong, V., Xiong, C., Socher, R. _Seq2SQL: Generating Structured Queries from Natural Language using Reinforcement Learning_. arXiv:1709.00103](https://arxiv.org/abs/1709.00103).  
[^6]: [Pourreza, M., Rafiei, D. _DIN-SQL: Decomposed In-Context Learning of Text-to-SQL with Self-Correction_. arXiv:2304.11015](https://arxiv.org/abs/2304.11015).
[^7]: [Bommasani, R., et al.  On the Opportunities and Risks of Foundation Models](https://arxiv.org/abs/2108.07258)
[^8]: [OpenAI  GPT-4 Technical Report](https://arxiv.org/abs/2303.08774)
[^9]: [Touvron, H., et al.  Llama 3: Open Foundation and Instruction Models Meta AI  2024](https://arxiv.org/abs/2302.13971)