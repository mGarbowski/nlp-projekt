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
    

## Do sprawdzenia
* CoSQL dataset
* table gpt 2 https://arxiv.org/abs/2411.02059

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