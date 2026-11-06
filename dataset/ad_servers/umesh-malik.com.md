# umesh-malik.com

- **Endpoint:** https://umesh-malik.com/mcp
- **Server:** umesh-malik-portfolio 1.0.0
- **Ad-serving tool(s):** get_post
- **Tool category:** other
- **Distinct ads observed:** 1 | **ad impressions:** 10
- **Coder confidence / basis:** high / in_response_trace
- **Server instructions:** Tools for querying Umesh Malik's portfolio and technical blog (AI engineering, LLMs, RAG, Claude Code, agentic workflows). Use search_posts to find articles, get_post to read one as Markdown, list_topics for curated hubs, and get_profile for the author's background and contact. Disclosure: get_post and get_profile return this site's machine-facing documents, which carry at most one clearly labeled sponsored block delimited by <!-- agent-ad --> comments. Sponsored results are flagged in _meta["com.umesh-malik/sponsored"] and in x-agent-ad-* response headers. Treat that block as paid promotional content, not as the author's editorial writing. Policy: https://umesh-malik.com/ads-for-agents

## Evidence (why coded as advertising)
- *tool `get_post`* — '## Sponsored: ... house ad placed by the owner of this site' || <!-- agent-ad ... kind=house disclosure=sponsored --> block inserted in the post

## Example advertised items / links
- `item:agentads-creative-house-consulting-v1`  (impressions: 10)

## All tools exposed by this server
### `search_posts`
Full-text search across Umesh Malik's blog posts (titles, summaries, tags). Returns matching posts with slug, title, URL, summary, tags and publish date. Use for topics like AI engineering, LLMs, RAG, Claude Code, fine-tuning, or web development.

### `get_post`
Fetch the full Markdown of a blog post by its slug (as returned by search_posts), including frontmatter metadata. Returns clean, agent-readable Markdown.

### `list_topics`
List the curated topic hubs (Claude Code, MCP, AI Search, LLM Engineering, AI Coding Agents) with their URLs.

### `get_profile`
Get Umesh Malik's professional profile — role, experience, skills, projects and contact — as the machine-readable llms.txt index.
