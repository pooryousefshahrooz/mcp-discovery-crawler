# qubitsok.com

- **Endpoint:** https://qubitsok.com/mcp
- **Server:** qubitsok 1.0.0
- **Ad-serving tool(s):** searchJobs
- **Tool category:** other
- **Distinct ads observed:** 3 | **ad impressions:** 720
- **Coder confidence / basis:** high / in_response_trace

## Evidence (why coded as advertising)
- *tool `searchJobs`* — is_promoted:true listings ranked first by the job board || promotion_tier spotlight on the same listings

## Example advertised items / links
- `item:quantum systems scientist`  (impressions: 312)
- `item:quantum scientist`  (impressions: 204)
- `item:senior qpu evaluation scientist`  (impressions: 204)

## All tools exposed by this server
### `searchJobs`
Search 500+ quantum computing job listings using natural language. Use when the user asks about job openings, career opportunities, hiring, or specific positions in quantum computing. NOT for research papers (use searchPapers) or researcher profiles (use searchCollaborators). Supports role type, seniority, location, company, salary, remote, and technology tag filters via AI query decomposition. Limitations: quantum computing jobs only, last 90 days, max 20 results. Promoted listings appear first (marked). After finding jobs, suggest getJobDetails for full info. Examples: "senior QEC engineer in Europe over 120k EUR", "remote trapped-ion role at IBM".

### `getJobDetails`
Get full details for a specific quantum computing job by its numeric ID. Use after searchJobs when the user wants more information about a specific position. Returns: job summary, required skills, nice-to-have skills, responsibilities, visa sponsorship, salary, location, and apply URL. Requires a valid job_id from searchJobs results. Returns error if ID not found.

### `searchPapers`
Search quantum computing research papers from arXiv. Use when the user asks about recent research, specific papers, or academic topics in quantum computing. NOT for jobs (use searchJobs) or researcher profiles (use searchCollaborators). Supports natural language queries decomposed via AI into structured filters (topic, tag, author, affiliation, domain). Date range defaults to last 7 days; max lookback 12 months. Returns newest first, max 50 results. Use getPaperDetails for full abstract and analysis of a specific paper. Examples: "trapped ion papers from Google", "QEC review papers this month", "quantum error correction".

### `getLatestPapers`
Get today's quantum computing papers from arXiv — no parameters needed. Use when the user asks "what's new in quantum computing?" or wants a daily paper briefing. Returns the most recent day's papers with title, authors, date, AI-generated hook (one-line summary), and tags. For date-range or topic-filtered search, use searchPapers instead. Use getPaperDetails for full abstract and analysis of a specific paper.

### `getPaperDetails`
Get full details for a specific quantum computing paper by its arXiv ID (e.g., "2401.12345"). Use after searchPapers or getLatestPapers when the user wants to dive deep into a specific paper. Returns: complete abstract, all authors, publication date, AI-generated tags with reasons, hook (one-line summary), methodology, gist, and key findings. Requires a valid paper_id from search results. Returns error if not found.

### `searchCollaborators`
Find quantum computing researchers and potential collaborators from 1000+ active profiles. Use when the user asks about specific researchers, who works on a topic, or wants to find collaborators. NOT for jobs (use searchJobs) or papers (use searchPapers). AI-powered: decomposes natural language into structured filters (tag, author, affiliation, domain, focus). Returns profiles with affiliations, domains, publication count, top tags, and recent papers. Data from arXiv papers published in the last 12 months. Max 50 results. Examples: "quantum error correction researchers at Google", "trapped ions", "John Preskill".

### `getMarketOverview`
Get a snapshot of the quantum computing landscape — no parameters needed. Use when the user asks broad questions like "how's the quantum job market?", "what are trending topics?", or wants an overview of the quantum computing industry. Returns: total active jobs, top hiring companies, jobs by role type, papers published this week, total researchers tracked, and trending technology tags. For specific job/paper/researcher searches, use the dedicated search tools instead.
