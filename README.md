# epigraph — declarative flow diagrams for epi compartmental models

Turns an easy to read, declarative epi compartmental model spec into a
[Graphviz](https://graphviz.org/) [DOT
file](https://graphviz.org/doc/info/lang.html).

For example, here is as simple compartmental model spec loosely based on the
[Gauld et al.
2018](https://journals.plos.org/plosntds/article?id=10.1371/journal.pntd.0006759)
Typhoid fever in Santiago, Chile model:

```
# Core compartments
state U  [label="Unexposed"]
state S  [label="Susceptible"]
state E  [label="Exposed"]
state A  [label="Acute"]
state SC [label="Subclinical"]
state C  [label="Chronic Carrier"]

# Environmental reservoirs
state SCycle [label="Short Cycle", rank=sink]
state LCycle [label="Long Cycle", rank=sink]

# Natural history
U --> S
S --λ--> E
E --π--> A
E --1 − π--> SC
A --ρ · γ--> C
SC --ρ · γ--> C

# Environmental contamination (short and long cycle)
A  --θ_A → SC--> SCycle
SC --θ_SC → SC--> SCycle
C  --θ_C → SC--> SCycle

A  --θ_A → LC--> LCycle
SC --θ_SC → LC--> LCycle
C  --θ_C → LC--> LCycle

# Re-entry from environmental reservoirs
SCycle --λ_SC--> S
LCycle --λ_LC--> S
```

To render this, 

```bash
$ epigraph typhoid.flow --out typhoid.svg 
```
