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

## Wyniki dla wszystkich 2148 przykładów ze zbioru testowego, Qwen

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

## Wyniki dla zbioru walidacyjnego - wariant COT, Qwen

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

## Wyniki dla zbioru testowego Plan and solve, Qwen
Predykcje zapisane w [pliku](docs/predictions-pas-test.txt)

```
                     easy                 medium               hard                 extra                all                 
count                470                  857                  463                  357                  2147                
=====================   EXECUTION ACCURACY     =====================
execution            0.611                0.383                0.220                0.182                0.364               

====================== EXACT MATCHING ACCURACY =====================
exact match          0.219                0.112                0.043                0.008                0.103               

---------------------PARTIAL MATCHING ACCURACY----------------------
select               0.884                0.826                0.789                0.884                0.844               
select(no AGG)       0.891                0.851                0.789                0.884                0.857               
where                0.800                0.693                0.372                0.276                0.606               
where(no OP)         0.800                0.711                0.512                0.310                0.644               
group(no Having)     1.000                0.500                0.840                0.438                0.667               
group                0.000                0.286                0.840                0.438                0.533               
order                0.978                0.795                0.553                0.062                0.705               
and/or               1.000                0.936                0.943                0.860                0.939               
IUEN                 0.000                0.000                0.000                0.000                0.000               
keywords             0.950                0.763                0.671                0.488                0.764               
---------------------- PARTIAL MATCHING RECALL ----------------------
select               0.277                0.194                0.130                0.106                0.184               
select(no AGG)       0.279                0.200                0.130                0.106                0.186               
where                0.276                0.256                0.062                0.036                0.153               
where(no OP)         0.276                0.262                0.085                0.041                0.163               
group(no Having)     0.132                0.025                0.162                0.051                0.068               
group                0.000                0.014                0.162                0.051                0.055               
order                0.549                0.242                0.146                0.007                0.198               
and/or               0.994                0.991                0.986                0.977                0.989               
IUEN                 0.000                0.000                0.000                0.000                0.000               
keywords             0.362                0.173                0.108                0.059                0.162               
---------------------- PARTIAL MATCHING F1 --------------------------
select               0.421                0.314                0.223                0.190                0.301               
select(no AGG)       0.425                0.323                0.223                0.190                0.306               
where                0.410                0.374                0.106                0.064                0.245               
where(no OP)         0.410                0.383                0.146                0.072                0.260               
group(no Having)     0.233                0.047                0.271                0.092                0.124               
group                1.000                0.027                0.271                0.092                0.099               
order                0.703                0.371                0.231                0.013                0.309               
and/or               0.997                0.963                0.964                0.915                0.963               
IUEN                 1.000                1.000                1.000                1.000                1.000               
keywords             0.525                0.283                0.186                0.105                0.267  
```

## Wyniki dla zbioru testowego Plan and solve, Llama
Predykcje zapisane w [pliku](docs/predictions-pas-llama-test.txt)

```
                     easy                 medium               hard                 extra                all                 
count                470                  857                  463                  357                  2147                
=====================   EXECUTION ACCURACY     =====================
execution            0.168                0.054                0.052                0.034                0.075               

====================== EXACT MATCHING ACCURACY =====================
exact match          0.081                0.002                0.002                0.000                0.019               

---------------------PARTIAL MATCHING ACCURACY----------------------
select               0.583                0.451                0.426                0.368                0.500               
select(no AGG)       0.625                0.479                0.444                0.368                0.530               
where                0.397                0.236                0.065                0.167                0.240               
where(no OP)         0.397                0.236                0.130                0.333                0.269               
group(no Having)     0.000                0.400                0.600                0.000                0.263               
group                0.000                0.200                0.600                0.000                0.211               
order                0.486                0.043                0.056                0.000                0.244               
and/or               1.000                0.919                0.937                0.858                0.931               
IUEN                 0.000                0.000                0.000                0.000                0.000               
keywords             0.568                0.328                0.286                0.400                0.416               
---------------------- PARTIAL MATCHING RECALL ----------------------
select               0.149                0.037                0.050                0.020                0.061               
select(no AGG)       0.160                0.040                0.052                0.020                0.065               
where                0.159                0.042                0.012                0.009                0.044               
where(no OP)         0.159                0.042                0.023                0.018                0.049               
group(no Having)     0.000                0.007                0.023                0.000                0.009               
group                0.000                0.004                0.023                0.000                0.007               
order                0.220                0.008                0.007                0.000                0.040               
and/or               0.994                0.994                0.998                0.987                0.994               
IUEN                 0.000                0.000                0.000                0.000                0.000               
keywords             0.174                0.031                0.031                0.017                0.049               
---------------------- PARTIAL MATCHING F1 --------------------------
select               0.237                0.069                0.089                0.037                0.109               
select(no AGG)       0.254                0.073                0.093                0.037                0.116               
where                0.227                0.071                0.020                0.017                0.074               
where(no OP)         0.227                0.071                0.039                0.034                0.083               
group(no Having)     1.000                0.014                0.044                1.000                0.017               
group                1.000                0.007                0.044                1.000                0.013               
order                0.303                0.013                0.012                1.000                0.069               
and/or               0.997                0.955                0.967                0.918                0.961               
IUEN                 1.000                1.000                1.000                1.000                1.000               
keywords             0.266                0.056                0.056                0.032                0.088         
```
## Wyniki dla zbioru testowego Chain of Thought, QWEN
Predykcje zapisane w [pliku](docs/predictions-cot-qwen-test.txt)

```
					 easy                 medium               hard                 extra                all                 
count                470                  857                  463                  357                  2147                
=====================   EXECUTION ACCURACY     =====================
execution            0.636                0.421                0.281                0.227                0.406               

====================== EXACT MATCHING ACCURACY =====================
exact match          0.304                0.152                0.067                0.025                0.146               

---------------------PARTIAL MATCHING ACCURACY----------------------
select               0.857                0.807                0.868                0.840                0.838               
select(no AGG)       0.872                0.807                0.877                0.860                0.846               
where                0.825                0.618                0.316                0.256                0.528               
where(no OP)         0.825                0.634                0.474                0.326                0.585               
group(no Having)     0.900                0.778                0.879                0.417                0.780               
group                0.000                0.704                0.848                0.417                0.634               
order                0.963                0.756                0.622                0.214                0.741               
and/or               1.000                0.936                0.947                0.867                0.941               
IUEN                 0.000                0.000                0.000                0.000                0.000               
keywords             0.916                0.778                0.587                0.500                0.738               
---------------------- PARTIAL MATCHING RECALL ----------------------
select               0.370                0.224                0.214                0.118                0.236               
select(no AGG)       0.377                0.224                0.216                0.120                0.238               
where                0.324                0.246                0.093                0.050                0.169               
where(no OP)         0.324                0.252                0.139                0.064                0.188               
group(no Having)     0.237                0.074                0.223                0.037                0.109               
group                0.000                0.067                0.215                0.037                0.089               
order                0.634                0.266                0.194                0.021                0.236               
and/or               0.996                0.996                0.968                0.987                0.989               
IUEN                 0.000                0.000                0.000                0.000                0.000               
keywords             0.411                0.204                0.141                0.070                0.192               
---------------------- PARTIAL MATCHING F1 --------------------------
select               0.517                0.351                0.343                0.206                0.368               
select(no AGG)       0.526                0.351                0.347                0.211                0.372               
where                0.465                0.352                0.143                0.084                0.256               
where(no OP)         0.465                0.361                0.215                0.106                0.284               
group(no Having)     0.375                0.136                0.356                0.068                0.192               
group                1.000                0.123                0.344                0.068                0.156               
order                0.765                0.393                0.296                0.038                0.358               
and/or               0.998                0.965                0.957                0.923                0.964               
IUEN                 1.000                1.000                1.000                1.000                1.000               
keywords             0.568                0.323                0.227                0.123                0.304
```

## Wyniki dla zbioru testowego Chain of Thought, Llama
Predykcje zapisane w [pliku](docs/predictions-cot-llama-test.txt)

```
                     easy                 medium               hard                 extra                all                 
count                470                  857                  463                  357                  2147                
=====================   EXECUTION ACCURACY     =====================
execution            0.155                0.049                0.043                0.031                0.068               

====================== EXACT MATCHING ACCURACY =====================
exact match          0.060                0.007                0.006                0.000                0.017               

---------------------PARTIAL MATCHING ACCURACY----------------------
select               0.549                0.452                0.649                0.429                0.525               
select(no AGG)       0.575                0.468                0.703                0.429                0.550               
where                0.328                0.196                0.088                0.095                0.212               
where(no OP)         0.375                0.216                0.176                0.286                0.276               
group(no Having)     0.000                1.000                0.000                0.000                0.750               
group                0.000                0.333                0.000                0.000                0.250               
order                0.714                0.556                0.250                0.000                0.533               
and/or               1.000                0.920                0.937                0.858                0.931               
IUEN                 0.000                0.000                0.000                0.000                0.000               
keywords             0.440                0.431                0.382                0.227                0.402               
---------------------- PARTIAL MATCHING RECALL ----------------------
select               0.132                0.033                0.052                0.034                0.059               
select(no AGG)       0.138                0.034                0.056                0.034                0.061               
where                0.145                0.032                0.012                0.009                0.039               
where(no OP)         0.166                0.036                0.023                0.027                0.050               
group(no Having)     0.000                0.011                0.000                0.000                0.005               
group                0.000                0.004                0.000                0.000                0.002               
order                0.122                0.039                0.007                0.000                0.032               
and/or               0.979                0.996                0.995                0.984                0.990               
IUEN                 0.000                0.000                0.000                0.000                0.000               
keywords             0.125                0.036                0.029                0.014                0.043               
---------------------- PARTIAL MATCHING F1 --------------------------
select               0.213                0.061                0.096                0.062                0.106               
select(no AGG)       0.223                0.063                0.104                0.062                0.111               
where                0.201                0.056                0.020                0.017                0.065               
where(no OP)         0.230                0.061                0.041                0.050                0.085               
group(no Having)     1.000                0.021                1.000                1.000                0.010               
group                1.000                0.007                1.000                1.000                0.003               
order                0.208                0.073                0.014                1.000                0.061               
and/or               0.989                0.957                0.965                0.917                0.960               
IUEN                 1.000                1.000                1.000                1.000                1.000               
keywords             0.194                0.067                0.053                0.026                0.078 
```


## Wyniki dla zbioru testowego React-lite, Qwen
Predykcje zapisane w [pliku](docs/predictions-react-lite-qwen-test.txt)
```
                     easy                 medium               hard                 extra                all                 
count                470                  857                  463                  357                  2147                
=====================   EXECUTION ACCURACY     =====================
execution            0.606                0.474                0.300                0.246                0.428               

====================== EXACT MATCHING ACCURACY =====================
exact match          0.449                0.270                0.104                0.059                0.238               

---------------------PARTIAL MATCHING ACCURACY----------------------
select               0.742                0.672                0.720                0.623                0.695               
select(no AGG)       0.784                0.680                0.731                0.642                0.715               
where                0.780                0.605                0.396                0.341                0.549               
where(no OP)         0.827                0.630                0.530                0.412                0.614               
group(no Having)     0.480                0.727                0.765                0.500                0.676               
group                0.000                0.634                0.741                0.485                0.587               
order                0.949                0.706                0.333                0.233                0.541               
and/or               1.000                0.969                0.955                0.879                0.958               
IUEN                 0.000                0.000                0.429                0.400                0.400               
keywords             0.866                0.826                0.684                0.592                0.767               
---------------------- PARTIAL MATCHING RECALL ----------------------
select               0.630                0.468                0.445                0.277                0.467               
select(no AGG)       0.666                0.474                0.451                0.286                0.480               
where                0.683                0.476                0.251                0.132                0.364               
where(no OP)         0.724                0.495                0.336                0.159                0.407               
group(no Having)     0.316                0.472                0.500                0.250                0.416               
group                0.000                0.411                0.485                0.243                0.362               
order                0.683                0.375                0.188                0.099                0.292               
and/or               0.991                0.987                0.953                0.943                0.974               
IUEN                 0.000                0.000                0.075                0.021                0.045               
keywords             0.660                0.555                0.385                0.252                0.466               
---------------------- PARTIAL MATCHING F1 --------------------------
select               0.681                0.552                0.550                0.384                0.559               
select(no AGG)       0.720                0.558                0.558                0.395                0.574               
where                0.728                0.533                0.307                0.190                0.438               
where(no OP)         0.772                0.554                0.411                0.230                0.490               
group(no Having)     0.381                0.572                0.605                0.333                0.515               
group                1.000                0.499                0.586                0.324                0.448               
order                0.794                0.490                0.240                0.139                0.380               
and/or               0.996                0.978                0.954                0.910                0.966               
IUEN                 1.000                1.000                0.128                0.039                0.081               
keywords             0.749                0.664                0.492                0.354                0.579               
```