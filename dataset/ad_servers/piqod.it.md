# piqod.it

- **Endpoint:** https://piqod.it/mcp
- **Server:** piqod-experiences-oracle 1.28.1
- **Ad-serving tool(s):** search_experiences
- **Tool category:** other
- **Distinct ads observed:** 10 | **ad impressions:** 10
- **Coder confidence / basis:** medium / documentation
- **Server instructions:** Oracolo PIQOD per esperienze di viaggio (tour, attività, biglietti). Cerca e confronta tra più provider (Viator, Tiqets, Headout) e restituisce un link di prenotazione. Usa questi tool quando l'utente cerca COSE DA FARE, tour, attività, biglietti o vuole il MIGLIOR PREZZO per un'esperienza.

## Evidence (why coded as advertising)
- *tool `search_experiences`* — piqod signed redirect; description 'redirect PIQOD affiliato'; response: commission goes to PIQOD

## Example advertised items / links
- `piqod.it/api/oracle/go/viator_5452DRINK`  (impressions: 1)
- `piqod.it/api/oracle/go/headout_3336`  (impressions: 1)
- `piqod.it/api/oracle/go/viator_285621P1`  (impressions: 1)
- `piqod.it/api/oracle/go/viator_42233P1`  (impressions: 1)
- `piqod.it/api/oracle/go/viator_6918ULA`  (impressions: 1)
- `piqod.it/api/oracle/go/tiqets_973980`  (impressions: 1)
- `piqod.it/api/oracle/go/viator_6353P7`  (impressions: 1)
- `piqod.it/api/oracle/go/viator_394285P13`  (impressions: 1)
- `piqod.it/api/oracle/go/viator_3731NORMANDY`  (impressions: 1)
- `piqod.it/api/oracle/go/viator_6353P8`  (impressions: 1)

## All tools exposed by this server
### `search_experiences`
Cerca tour, attività ed esperienze da prenotare in un luogo o per un intento     di viaggio (es. "cosa fare a Roma", "biglietti per il Colosseo", "tour in barca a     Capri"). Restituisce risultati reali con città, prezzo, rating e un link di     prenotazione (redirect PIQOD affiliato). USA QUESTO TOOL quando l'utente cerca     cose da fare, tour, attività, biglietti o esperienze in una destinazione.     IMPORTANTE per la coerenza: se l'utente nomina un'ATTRAZIONE/attività precisa     (es. "tour del Colosseo"), passa quel nome in `keyword` (es. "Colosseo") → i     risultati saranno SUL Colosseo, non genericamente vicini. Mappa anche gli INTENTI     sui filtri: "salta fila/skip the line" → skip_the_line=True; "più economico/cheapest"     → sort="price"; "cancellazione gratuita" → free_cancellation=True; "con bambini/per     famiglie" → traveler_type="famiglie", "romantico/in coppia" → "coppie"; "la sera/di     notte/al tramonto" → day_part="sera", "la mattina/all'alba" → "mattina", "il     pomeriggio" → "pomeriggio".      Nel risultato (lo stesso testo delle azioni GPT, api/oracle_openapi):         min_people: Minimo di persone per prenotare, solo se il provider lo chiede ed è 2 o p

### `compare_experience`
Confronta il prezzo della STESSA esperienza tra i provider (Viator, Tiqets,     Headout) e indica dove costa meno, con un verdetto e il link di prenotazione.     USA QUESTO TOOL quando l'utente vuole il MIGLIOR PREZZO per un tour/attività     specifico (passa l'experience_id ottenuto da search_experiences).      Nel risultato (lo stesso testo delle azioni GPT, api/oracle_openapi):         min_people: Minimo di persone per prenotare, solo se il provider lo chiede ed è 2 o più: dillo accanto al             prezzo («minimo 2 persone»). null = nessuno o ignoto. price_from non è il totale: a persona se             price_basis=PER_PERSON, per unità se UNIT; con price_basis '' scrivi «minimo N persone» senza «a persona».         price_basis: PER_PERSON | UNIT (prezzo per veicolo/gruppo/barca) | '' = dato non fornito dal provider (oggi             disponibile sui prodotti Viator arricchiti; copertura in crescita).         price_unit: VEHICLE/GROUP/BOAT/... quando price_basis=UNIT; altrimenti ''.      Args:         experience_id: id dell'esperienza (es. "viator_12345").         query: (opzionale) la richiesta originale dell'utente — migliora             l'attribuzione del click; se assente 

### `get_destination_guide`
Le migliori esperienze e cose da fare in una destinazione (città o paese),     ordinate per qualità, con link di prenotazione. USA QUESTO TOOL quando l'utente     pianifica un viaggio o chiede le TOP attività/esperienze di un posto.      Nel risultato (lo stesso testo delle azioni GPT, api/oracle_openapi):         min_people: Minimo di persone per prenotare, solo se il provider lo chiede ed è 2 o più: dillo accanto al             prezzo («minimo 2 persone»). null = nessuno o ignoto. price_from non è il totale: a persona se             price_basis=PER_PERSON, per unità se UNIT; con price_basis '' scrivi «minimo N persone» senza «a persona».         price_basis: PER_PERSON | UNIT (prezzo per veicolo/gruppo/barca) | '' = dato non fornito dal provider (oggi             disponibile sui prodotti Viator arricchiti; copertura in crescita).         price_unit: VEHICLE/GROUP/BOAT/... quando price_basis=UNIT; altrimenti ''.      Args:         place: città o paese (es. "Roma", "Giappone").         limit: numero risultati (max 30).
