# SIR-Modelling
To model the SIR models

## Parameters Explaination inside ABM_Parameters.json

| Parameter | Description | Datatype |
| --- | ----------- |---------|
| Name | Name of the simulation, if name is "MULTI", it enables multiprocessing multiple scenarios | String |
| Population | self explainatory |integer |
| Init_Inf | Intially infected agents | 0&lt;integer &lt;Population |
| Days | self explainatory | integer |
| Sectors| Different specialized sectors in interaction space| list(String) |
| SecVirus| A dictionary representing virus related parameters in the specialized interaction spaces. | dict(string:dict(string:list(float))) |
| SecVirus-N| Each element represents the proportion of total spaces in the indexed subsector  | list(float) |
| SecVirus-E| Each element represents the total expected agents per space in the in the indexed subsector  | list(int) |
| SecVirus-V| First element represent the average time of contact and second is the average distance inthe sector  | [int,int] |
| Family_Size | Average number of agents in a Family and its standard deviation | [int,int] |
| Density| self-explainatory | people/km^2 |
| Pop_Groups| Maximum age of different groups of Population. Eg if it is [16,80] then first age group is 0-16 and other is 17-80 | list(int) |
| Pop_Dist|Proportion of population present in the indexed population group | list(float) |
|Empl_Dist|Employee distribution, proportion of agents of a specific age group working in a particular specialized sector. last sector is always unemployed | len(Pop_Groups) X (len(sector)+1) (float)|
|VName|Name of Virus/Variant | string|
|R0|self-explainatory | float|    
|Death_Rates|Death rate per age group |len(Pop_Groups) (float)|
|Inc_Period|Incubation period TI per age group |len(Pop_Groups) (float)|
|Death_Rates|Death rate per age group |len(Pop_Groups) (int)|
|Cure_Days|Average number of days to cure |int|
|Severity|Severity in Mild Moderate Severe per age group |len(Pop_Groups)x3 (float)|
|UseTran|Proportion of population using transport |0&le;float &le;1|
|Init_CR|Initial Compliance Rate |0&le;float &le;1|
|SD_Ratio|Social Distancing Ratio |float|
|Virus_Params| Virus Parameters of non-specialized default interaction spaces, refer SecVirus-V| {string:dict(string:float)}|
|Commerce_On|Whether Transactions/Grocery default interaction space is enabled or not| bool|
|PPurchase|Proportion of agents going out to purchase grocercies| float|
|TestingOn|Whether Testing is enabled or not| bool|
|TracingOn|Whether contact Tracing is enabled or not| bool|
|LockdownPhases|A list of intervention policies undertaken by the administration. Consists of start day, duration, type, Scrutiny,sectors,CR, Threshold,period|list(list(8))|
|LockdownPhases-Start Day; Duration| Starting day from which the policy can be triggered, Duration represents the amount of time after start day policy can be triggered, After Start Day+Duration that policy could never be triggered| int|
|LockdownPhases-type; Scrutiny;sectors;|Type represents whether it is Citywide lockdown or specific region, Scrutiny is the criterian for imposition of policy (available are Hard, TAbsoulte and TRelative), in Hard policy would trigger no matter what, TAbsoulte defines policy would trigger after total number of cases crosses a threshold, TRelative defines policy would trigger if daily cases crosses a threshold. Sectors represent affteced sectors, use "Complete" for all interactions spaces except Home to be triggered| string|
|LockdownPhases-CR;Threshold; Period|CR is the compliance rate during the lockdown phase. Threshold is the threshold for TRelative and TAbsoulte type policy. Null otherwise. Period represents the length of active policy time after it is triggered.| float;int;int|