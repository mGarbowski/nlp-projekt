# Literatura
Do przeglądu literatury i inne źródła

* [Tutorial budowania agenta SQL w LangChain](https://docs.langchain.com/oss/python/langchain/sql-agent#run-your-agent-in-studio)
  * jest już gotowiec do integracji z bazami SQL
  * wykonywanie zapytań, sprawdzanie schematu
* [Tutorial z budowania własnego agenta SQL w LangChain](https://docs.langchain.com/oss/python/langgraph/sql-agent)
  * z użyciem mniejszej liczby gotowców
* [Toward Real-World Table Agents: Capabilities, Workflows, and Design Principles for LLM-based Table Intelligence](https://arxiv.org/pdf/2507.10281)
  * ogromny przegląd literatury
  * identyfikuje wyzwania
    * zrozumienie struktury tabel
    * zrozumienie semantyki tabel i zapytań
    * retrieval i kompresja
    * rozumowanie i traceability, wydajność
    * generalizacja na inne domeny
  * zrozumienie struktury tabel
    * serializacja tabeli do formatów tekstowych
    * markdown, json, html, latex
    * rozważania o tabelkach jako obrazy, grafy i specjalnych enkoderach dla danych tabelarycznych
  * zrozumienie semantyki
    * problemy z niejasnymi nazwami kolumn, szumem
    * detekcja intencji z zapytania użytkownika - może wymagać dopytywania
    * dodanie kontekstu pomaga
    * można generowac kilka wersji do wybrania przez użytkownika
  * retrieval
    * najprostsze podejście - wykrycie przez LLM istotnych tabel mając cąły chemat i zapyranie
    * schema link
    * dla dużych schematów wieloetapowe strategie - np. chunkowanie
    * też rozważany retrieval na poziomie, rekordów, komórek
    * nie za bardzo są benchmarki na to
  * rozumowanie i traceability
    * problemy z sql - mało zróżnicowane przykłady benchmarkowe, metryki często opierają się na dokładnych dopasowaniach, brak benchmarków text-to-sql w językach innych niż angielski, słabej jakości tłumaczone benchmarki
    * też rozwiązania text-to-python i text-to-dsl
    * traceability jest bardzo trudne dla wszystkich rozwiązań poza DSL
  * generalizacja na różne domeny
    * sporo benchmarków text-to-sql dla danyhc finansowych
  * architektura systemów
    * spory przegląd dostęþnych rozwiąząń
    * dominują formaty tesktowe
    * słaby preprocessing danych z tabel
    * ograniczone zastosowanie rozpoznawania intencji użytkownika
    * najczęściej python albo sql jako wyjście
    * sandboxy do wykonywania kodu
    * trudności z przenoszeniem między domenami, testowane podejścia typu RAG
    * najbardizej zaawansowane dostępne rozwiązanie - TableGPT2
  * Ocena jakości
    * metryka execution accuracy - poprawność wyniku zapytania SQL
    * porównanie wielu metod (chain of thought, mac-sql, mag-sql, chess, magic)
    * cot działa kiepsko
    * opensearch-sql działa dosyć dobrze nawet dla słabszych modeli
  * sugerowane dobre praktyki
    * wsparcie dla wielu formatów wejściowych
    * zintegrowany preprocessing danych
    * rozumowanie krokowe i traceability - na potrzeby zaufania i debugowania
    * dbanie o bezpieczeństwo
    * modularna architektura

## TableGPT2
* Koder danych tabelraycznych
  * jak w modelach typu VLM
  * dnae tabelaryczne jako oddzielna modalność
  * pozwala lepiej uchwycić niejednoznaczne zapytania, schemat itp
* Dekoder z wielkiego modelu wielomodalnego
* Są dostępne wagi na hugging face
  * i repozytorium na githubie z workflow dla agenta
  * w langgraph - też chcemy go używać więc można się wzorować
* W praktycznych zastosowaniach cały zbiór danych nie mieści się w kontekście
* Dla zastosowań BI rozwiązania typu natural language to SQL i table comprehension są niewystarczające
  * często polegają na prostych schematach baz danych, słabo przenoszą się na rzeczywiste problemy analityczne
  * benhcmarki opierają się na dobrze ustrukturyzowanych zapytaniach i czystych schematach
* Fine-tunowany Qwen (wersja 7b i 72b) specyficznie do zadań z danymi tabelarycznymi
* Augmentacje danych treningowych
  * np. znaonimizowane nazwy kolumn
  * poprawiają zdolność do generalizacji
* Sam schemat to jeszcze mało, istotna jest charakterystyka danych, przykładowe wartości
* Unikalne właściwości danych tabelarycznych jako modalności
  * struktura dwuwymiarowa
  * redundancja
  * rzadkość
* Koder tabeli
  * jako wejście cała tabela
  * embeddingi dla kolumn
  * semantyka tabeli wynika z: komórek, wierszy, kolumn, struktury całej tabeli
  * dwuwymiarowa atencja
  * bez kodowania pozycyjnego
  * hierarchiczny proces ekstrakcji cech
* Embeddingi kolumn są alignowane z tekstowymi przez moduł adaptera
* Opublikowali swój bencharm RealTabBench
* Sam dekoder jest wystarczający do prostszych zastosowań
  * koder-dekoder rekomendowany do bardziej złożonych
  * w artykule piszą że koder jeszczen ie jest udostępniony, do zweryfikowania
* Filtrowanie tokenów w zbiorze treningowym
  * na podstawie innego modelu jest oceniane jak bardzo obniżają stratę
* Czemu koder tabeli
  * tabela ma strukturę 2-wymiarową, a nie 1-wymiarową jak tekst
  * serializacja do formatu tekstowego wykorzystuje dużo tokenów
  * ograniczenia długości kontekstu
* Działanie kodera
  * nie ma kodowania pozycyjnego bo permutacja nie zmienia semantyki
  * dla każdej komórki wyznaczony embedding
  * poten atencja 2D po wierszach i po kolumnach
  * adapter do formatu embeddingów tekstowych z cross-attention
* Bardzo rozbudowany opis terningu
* Framework dla agentów
  * składa się z prompt enigneering w czasie wykonywania, sandboxa wykonywania kodu i modułu ewaluacji agenta
  * rag do zasilania agenta wiedzą
  * normalizacja tebli
  * generowanie kodu python/sql
  * opcjonalna integracja z VLM do analizy wykresów
  * wywołania narzędzi (pliki, bazy danych, wizualizacja)
* Szczegółowe opisy ewaluacji
  * wiele zadań (table understanding, table qa, table fact verification, table to text, nl2sql)
* Podsumowanie
  * SOTA jeszcze sporo brakuje do wdrożenia w zastosowaniach typu BI
    
## Zbiory danych
* Wszystkie zwierają pary pytanie-wynik dla zadania Text-to-SQL i bazy danyhc SQLite
* Zobaczymy czy wystarczy nam zasobów na ewaluację na całych zbiorach, czy ograniczymy się do podzbiorów
* WikiSQL
  * tylko proste zapytania do jednej tabeli, może być niewystarczające na nasez potrzeby
  * 26MB
  * [kaggle](https://www.kaggle.com/datasets/shahrukhkhan/wikisql)
  * [repo](https://github.com/salesforce/WikiSQL)
  * [paper](https://arxiv.org/pdf/1709.00103)
* Spider
  * chyba to jest odpowiednie dla nas - złożone zapytania z joinami itp.
  * 1GB
  * [kaggle](https://www.kaggle.com/datasets/jeromeblanchet/yale-universitys-spider-10-nlp-dataset)
  * [repo](https://github.com/taoyds/spider)
  * [paper](https://arxiv.org/pdf/1809.08887)
* BIRD
  * bardziej kompleksowe niż Spider, większe tabele
  * 30GB
  * [paper](https://arxiv.org/pdf/2305.03111)
  * [repo](https://github.com/AlibabaResearch/DAMO-ConvAI/tree/main/bird)

## Do sprawdzenia
* CoSQL dataset
* table gpt 2 https://arxiv.org/abs/2411.02059
* RealTabBench - bencharm z tablegpt2

## Do pobrania z sieci PW
* https://ieeexplore.ieee.org/document/11199504

## Wyniki wyszukiwania w Scopus

is there something specifically on the topic of LLM-based AI agents that take user input in natural language and produce and or execute SQL queries, if so, are there benchmarks to measure their quality

### Summary: LLM-Based AI Agents for Natural Language to SQL Query Generation and Benchmarks

Yes, there is relevant information on LLM-based AI agents that take natural language input and produce or execute SQL queries. Additionally, there are benchmarks and evaluation methods to measure their quality.

---

### **LLM-Based AI Agents for SQL Query Generation**
- **Functionality**: LLMs are increasingly used to transform natural language queries into SQL statements, enabling non-technical users to interact with databases seamlessly. These systems often include multi-agent architectures to handle query generation, execution, and even visualization [1] [2] [3] .
- **Applications**: Such systems are applied in various domains, including enterprise environments, financial data analysis, and healthcare, where they automate SQL query generation and execution to retrieve data efficiently [2] [4] [5] [6] .
- **Enhancements**: Techniques like fine-tuning LLMs on domain-specific datasets, iterative error correction, and prompt engineering are employed to improve query accuracy and alignment with user intent [3] [5] .

---

### **Benchmarks for Evaluating Quality**
Several benchmarks and evaluation frameworks have been developed to assess the performance of LLMs in generating SQL queries:
- **Spider and WikiSQL**: These datasets are widely used to evaluate text-to-SQL models, focusing on their accuracy and generalization capabilities [7] .
- **BIRD Dataset**: A refined benchmark addressing inconsistencies in SQL outputs, designed to test logical reasoning and domain adaptability of LLMs [8] .
- **Custom Benchmarks**: Some studies create domain-specific benchmarks, such as for financial data or enterprise environments, to evaluate correctness, execution success, and efficiency of SQL queries [4] [5] .
- **Metrics**: Common metrics include:
  - **Correctness**: Percentage of SQL queries that are syntactically and semantically correct [4] [5] [7] .
  - **Execution Success**: Whether the generated SQL queries execute without errors and retrieve the intended results [4] [8] .
  - **Effort and Success Rate**: Proposed metrics to measure the number of steps taken and the quality of the output [9] .

---

### **Key Findings**
- **Performance Variability**: LLMs like GPT-4 perform well in generating SQL queries (e.g. 87.6% correctness for SQL), but performance varies across models and domains [4] .
- **Challenges**: Issues such as hallucinated queries, logical errors, and poor handling of complex multi-table queries remain significant challenges [2] [5] [10] .
- **Improvements**: Multi-agent systems, retrieval-augmented generation (RAG), and iterative refinement mechanisms have shown promise in improving query accuracy and handling complex tasks [1] [2] [11] .

---

### **Conclusion**
LLM-based AI agents for natural language to SQL query generation are a growing area of research, with several benchmarks available to evaluate their quality. While these systems show promise, challenges like logical errors and domain-specific adaptability highlight the need for further advancements.

References
1. Semantic Search and Filtering with AI Agents
Bulín, M., Švec, J., Polák, F., Šmídl, L.
Lecture Notes in Computer Science, 2025
https://www.scopus.com/pages/publications/105006612285?origin=scopusAI

2. Multi-Agent System for Querying and Visualization Using Large Language Models
Gumilang, M.A., Ferdiana, R., Hidayah, I., (...), Fadli, A.I.
International Conference on Computer and Communication Engineering Technology, CCET, 2025
https://www.scopus.com/pages/publications/105021813960?origin=scopusAI

3. Large Language Model Data Query Method Based on Feedback Optimization Prompt Word Engineering
Zhang, X., Liu, Y., Li, W., Huang, Y.
Proceedings of 2025 2nd International Conference on Cloud Computing and Big Data, ICCBD 2025, 2026
https://www.scopus.com/pages/publications/105028660064?origin=scopusAI

4. LLM-Based Code Generation for Querying Temporal Tabular Financial Data
Lashuel, M., Kurdistan, G., Green, A., (...), Bennett, K.P.
2024 IEEE Symposium on Computational Intelligence for Financial Engineering and Economics, CIFEr 2024, 2024
https://www.scopus.com/pages/publications/85210241019?origin=scopusAI

5. Innovating SQL Automation: Evaluating Open-Source Large Language Models with a Dual-Stage Approach for Corporate Data Solutions
Arslan, E., Harinda, E.
UBMK 2024 - Proceedings: 9th International Conference on Computer Science and Engineering, 2024
https://www.scopus.com/pages/publications/85215522780?origin=scopusAI

6. AI-Powered Automation in Healthcare: A Multi-agent Approach with LLM
Almeida, M., Machado, J., Sousa, R., Peixoto, H.
Communications in Computer and Information Science, 2025
https://www.scopus.com/pages/publications/105021821588?origin=scopusAI

7. Text to SQL Transformation Using LLM: A Comparative Research of T5, Seq2Seq, and SQLNet Models
Shaikhiyeva, Z., Mansurova, M., Amirkhanova, G.
UBMK 2024 - Proceedings: 9th International Conference on Computer Science and Engineering, 2024
https://www.scopus.com/pages/publications/85215527290?origin=scopusAI

8. Refining Zero-Shot Text-to-SQL Benchmarks via Prompt Strategies with Large Language Models
Zhou, R., Zhang, F.
Applied Sciences (Switzerland), 2025
https://www.scopus.com/pages/publications/105006715952?origin=scopusAI

9. Magenta: Metrics and Evaluation Framework for Generative Agents Based on LLMs
Barkur, S.K., Sitapara, P., Leuschner, S., Schacht, S.
Applied Human Factors and Ergonomics International, 2024
https://www.scopus.com/pages/publications/105031300901?origin=scopusAI

10. EXASAGE: The first data center operational data analysis assistant
Ahmed Khan, J., Molan, M., Bartolini, A.
Future Generation Computer Systems, 2026
https://www.scopus.com/pages/publications/105020818559?origin=scopusAI

11. Bridging natural language and GIS: a multi-agent framework for LLM-driven autonomous geospatial analysis
Mansourian, A., Oucheikh, R.
International Journal of Digital Earth, 2026
https://www.scopus.com/pages/publications/105030928762?origin=scopusAI