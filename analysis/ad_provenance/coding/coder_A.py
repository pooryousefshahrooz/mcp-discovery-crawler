#!/usr/bin/env python3
"""Coder A's codes (first coder), written from out/review_sheet.md + out/review_sheet_supplement.md
only, following CODEBOOK.md. Run to (re)write out/coding_A.json.

Compact rows: sig, status, origin, basis, confidence, tool_category, note.
Abbreviations: C=confirmed_ad P=promotional X=commercial_other N=not_ad;
op=operator up=upstream_api tp=third_party_content mu=multiple un=unknown -=n/a;
sc=source_code tr=in_response_trace doc=documentation own=own_host_redirect_only no=none.
"""
import json
from pathlib import Path

S = {"C": "confirmed_ad", "P": "promotional", "X": "commercial_other", "N": "not_ad"}
O = {"op": "operator", "up": "upstream_api", "tp": "third_party_content", "mu": "multiple",
     "un": "unknown", "-": "n/a"}
B = {"sc": "source_code", "tr": "in_response_trace", "doc": "documentation",
     "own": "own_host_redirect_only", "no": "none"}
CF = {"h": "high", "m": "medium", "l": "low", "-": "n/a"}

ROWS = """
af7f636b736f N - no - other | 'sponsored build bounties' in a tool-catalog text; no ad item
a6497a3b3d7c X op doc m ad_network | integration docs for the operator's ad middleware; not an ad impression
2f54a1569a4b C op tr h shopping | Amazon tag + aff:true per item; ascsubtag=clk_X equals the server's own /v1/go/clk_X id -> minted by the server
21362fda8086 C op tr h shopping | server's /v1/go/clk_ redirect for the same aff:true items
47f7131daa86 N - no - shopping | items:[] with disclosure string only
7282f9d48632 N - no - other | capability text of a listed agent
98ec2d06ad5f N - no - other | "tier":"paid" = paid API tool tier, not an ad
5495fcb2e9a9 N - no - other | 'employer-sponsored' tax text
09640fb24c1e P op doc m shopping | operator describes its own affiliate-network business in about text; no ad item
ab141921052c N - no - other | own-host booking redirect for direct-booking listings; no affiliate/paid evidence
4306175a4c64 C op doc m shopping | response disclosure: store links are affiliate links, only paying stores listed (first-party catalogue)
3e43371ca9d4 N - no - ad_network | placements:[] empty sponsored slot
b744adae2de4 X op doc m ad_network | sponsorship rules/terms of the operator's paid-ranking product
24fbe68eda89 C op doc m shopping | Amazon tag on editorial picks; instructions: buy links are affiliate (Amazon Associates)
abe3ff51859c N - no - shopping | disclosure text in responses without any product link
e3fa3c501006 N - no - other | 'paid placement' inside a price comparison of ad vendors
a3c55d3b50b4 X op doc m ad_network | comparison of ad-placement prices incl. the operator's own; market info, not an ad
29ea73875793 N - no - other | 'paid placement' in directory-submission notes
8462ac961b6c P op doc l shopping | own listing pages; disclosure refers to links on its pages, returned links are not affiliate
5af037f3c7c7 C op doc m shopping | picks.bonizu.com/out redirect; tool description: returns tracked affiliate links
490aad779f81 N - no - shopping | empty promo-code lists + disclosure
5f069de50435 C op doc m shopping | cashbackpro /api/go link; response note: already a CashbackPro affiliate link
a2a23d3de2d2 C op doc m shopping | own-host /api/go product links; description: product URLs are CashbackPro affiliate links
2ed08b360a71 C op doc m shopping | same product links as a2a23d3de2d2, response disclosure covers them
43660246de3e N - no - other | directory description of another server mentions affiliate links
7d7749a1fe75 C op doc m shopping | own-host deal redirect with 'Relationship: affiliate' per offer
9a44484dab73 C op doc m shopping | same offers as 7d7749a1fe75 ('Relationship: affiliate')
ca8e688fc58c N - no - shopping | no deals matched + disclosure boilerplate
83c663e818d8 N - no - other | FTC legal text quoted in search result
79656ace2da3 C op doc m shopping | deal.ly/go redirect on eBay listings; instructions: eBay Partner Network affiliate links
177927c8e395 C op doc m shopping | as 79656ace2da3
dc5ad4ceaacc C op doc m shopping | Amazon search link tag=dealspingai-21; instructions name the affiliate tag and tool returns a 'monetized affiliate link'
3cb3d220f877 C op doc m shopping | tool generates an Amazon affiliate search link for any query
fd3fa46dae9e N - no - shopping | deals:[] + disclosure
426f32508b9f N - no - shopping | deals:[] + disclosure
24e2f78bc1df C op doc m shopping | catalog items with affiliate_url tag=webdealsping-21; description: ready-to-use affiliate links
ffe86e32a1d0 N - no - shopping | results:[] + disclosure
b4087718f3cb C op doc m shopping | zero-result fallback Amazon link with the operator's affiliate tag
a227dda73f89 P op doc m shopping | measured /go link to the operator's own Shopify store; instructions: preserve query string so publisher can measure
18421fcb14ce C op doc m other | /go registration links; response: 'go through Domain Search King's Namecheap and Spaceship affiliate links'
23e17e74c00a C op doc m other | same registration links, response disclosure
225627078e83 N - no - other | Eventbrite ?aff= tracking code supplied with provider record (discotech); no evidence of a paid relationship
49c5f2e3ce6b N - no - other | Eventbrite ?aff=oddtdtcreator organiser tracking code; no paid evidence
90f6b0f2a0f6 N - no - shopping | all responses empty + disclosure
098381de9b6e C op doc m shopping | cex.io referral signup link; instructions: we may earn a commission on our codes or links
2b6bdc8f5199 C op doc m shopping | fomo referral invite link; instructions: may earn commission on our codes/links
309825957c25 C op doc m shopping | aave referral link; same instructions
dbef19ae5e25 C op doc m shopping | TradingView aff_id partner link; same instructions
b8fbf696e09b N - no - other | API endpoint path /v1/ref/
9ab312dd2afd N - no - other | 'sponsored by the Department for Transport'
1525fbd89aa4 C op tr h other | grabgpu /go rent_url on offers flagged is_referral:true by the server
9bce12b00db3 C op tr h other | Vast.ai ref_id link on offers flagged is_referral:true
119717ba291e C op doc m shopping | affiliate_url field with Amazon tag; description: results may contain affiliate URLs
2c052dcee62f N - no - other | directory placement table, not an ad
6822798ca27a N - no - other | a listed site's own description mentions its ads
218f6f14ce9d N - no - ad_network | placements:[] empty
295760870459 N - no - shopping | order-tracking page link
d052495a1a19 C op doc m shopping | Awin affiliate link; description: links may be affiliate links
7278846c2052 N - no - other | own-host short links to tour platforms; no affiliate/paid evidence in the evidence shown
df9fca6da349 C op tr h ad_network | sponsored result with utm_medium=cpc, bid/impression tokens from the server's auction (demo tenant)
a61f27df57c6 C op tr h ad_network | sponsored_rank emitted by the server's ad auction
0c06102bfee0 C op tr h ad_network | disclosure_label Ad on sponsored results
8dfeca748afa C op tr h ad_network | sponsored_rank 2
630565dbb8d1 C op tr h ad_network | sponsored_rank 3
6bc76565b34f C op tr h ad_network | sponsored_search tool output (same sponsored items)
4843f4721014 N - no - other | as 7278846c2052
ba695ee3e363 N - no - other | "featured":true on a property listing; no evidence that featured is paid
76c6d7844146 C op doc m shopping | own-host /go shop links; response footer 'Kann Affiliate-Links enthalten'
d7edfe86ba08 C op doc m shopping | as 76c6d7844146
4aedffc1293d C tp tr h web_search | Amazon tag inside the scraped WSJ result body; asc_refurl names that WSJ page
be5e81228116 C tp tr h web_search | Skimlinks link inside the scraped WSJ result body; sref names that page
cf120e526b6b N - no - web_search | reddit /r/ path
b0d53445fa88 N - no - shopping | own-host buy redirect; no affiliate statement in evidence
c293d6759a2c N - no - other | describes search-engine ads as data
1bbf8a734ca0 N - no - shopping | plain merchant URLs with generic 'may earn' boilerplate
40d82506297f C op doc m shopping | Awin link next to canonical URL; response: Kit's Deals may earn a commission
645d527caea8 C op doc m shopping | CJ link next to canonical URL; same disclosure
f9e18fcb3fe6 N - no - ad_network | click tracker on organic catalogue products (no sponsored label in list_products)
eec85d48f5e2 N - no - ad_network | click tracker on all products; the sponsored subset is coded via the [Sponsored] label sig
60081f046011 N - no - ad_network | click tracker on recipes
a07e89acea0b C op tr h ad_network | [Sponsored] item with campaign id, bid and auction score emitted by the server
34d5bbca2648 N - no - ad_network | German 'Anzeige' = display (product text)
ccf707a5a8d8 C op doc m other | getMarketplaceAdverts: classified adverts from the operator's marketplace (description: third-party partner deals)
26b156cdb923 C op tr m shopping | REI Impact link in server field affiliate_links on 'Our Pick' catalogue items
1242bcb843c1 C op tr m shopping | Amazon tag in affiliate_links field
4f18bf7b6b29 C op tr m shopping | REI Impact link in affiliate_links field
5ee823aa318c C op tr m shopping | Amazon tag in affiliate_links field
d56a29aa7a68 C op tr m shopping | Amazon tag in affiliate_links field
fd5555baa08a N - no - other | UK visa-sponsor register
fa9f54483236 N - no - other | areFeesSponsored payment metadata
7e54a0dfb514 N - no - other | directory referral redirect to listed servers; no paid evidence
acb0aef50184 C op tr m ad_network | ad creatives for publisher agents to inject; moltadserver redirect wrapping a CJ link (ft=affiliate_network)
8bd18a103681 X op doc m ad_network | buy-side placement inventory listing for advertisers
1f8c4dd09cb7 X op doc m ad_network | as 8bd18a103681
3939a5dd34db X op doc m ad_network | as 8bd18a103681
ffc51f4083a5 X op doc m ad_network | as 8bd18a103681
abcf4fdac813 X op doc m ad_network | as 8bd18a103681
693447541d32 X op doc m ad_network | as 8bd18a103681
14cd6d4573e2 X op doc m ad_network | as 8bd18a103681
a13e54d9a48b X op doc m ad_network | as 8bd18a103681
6d81bb462891 X op doc m ad_network | as 8bd18a103681
14b700b849d6 X op doc m ad_network | as 8bd18a103681
f4f27ea3cb04 X op doc m ad_network | as 8bd18a103681
7fb8f11ff6bd C op tr m ad_network | TikTok Shop product ad units with tracked moltadserver clickUrl and Sponsored disclosure
4bc52645761c C op tr m ad_network | same ad units: 'Sponsored * affiliate partner offer'
3918c66e1cb4 C op doc m shopping | amzn.to link with per-offer 'Affiliate link. padel.how may earn a commission'
4f96274273e5 C op doc m shopping | as 3918c66e1cb4
783b2938c34d C op doc m shopping | Amazon tag + per-offer affiliate disclosure
9d21b0fea766 C op doc m shopping | as 3918c66e1cb4
4a723d55cec2 N - no - shopping | 'No retailer link is returned here'
698de0966f9a X tp tr m other | Amazon tag inside one seller's example output in a marketplace listing
2c79425ee523 N - no - ad_network | sponsored:[] Hub not found
e38dd2be6c7d C op tr h ad_network | picoads /rs/<serve_id> redirect on 'Sponsored via picoads' items
c5caade63374 C op tr h ad_network | non-empty sponsored array served by the ad network
f1e5b68f885c C op tr h ad_network | '(Sponsored)' creatives
fa13207b8df8 C op tr h ad_network | 'Sponsored via picoads' disclosure
a21583f95738 N - no - other | is_sponsored:false
56a07dc69040 C op doc m other | piqod signed redirect; description 'redirect PIQOD affiliato'; response: commission goes to PIQOD
1ec0dc52d3d4 P op doc m other | links to the operator's own cruise booking engine (agency commission model)
c71351ac6ab8 C op tr h other | is_promoted:true listings ranked first by the job board
24ab6d4f3b2f C op tr h other | promotion_tier spotlight on the same listings
aee79dba1ebc X op doc m other | operator's referral-programme handbook
8b744af7b699 X op doc m other | example referral link in the operator's affiliate-programme docs
838294f9b9dd X op doc m other | referral deep-link template in programme docs
1666ce6b0f2c N - no - other | reddit /r/ paths
9e036127b2f8 N - no - other | 'paid placement' in an agent profile
d306463fa7c7 N - no - other | rules text mentioning sponsored tasks
ebae3840352f N - no - other | 'paid placement' in an agent profile
91df7c666e08 P op doc m other | the operator's own funded-task prompts promoting its product
15fe1540a79d N - no - other | PDF path /rs/
82ba72e89ccf C op doc m other | /api/go partner sign-up links; description: 'recommended affiliate partner(s)'
9d0bcb774311 C op doc m other | same /api/go partner link ('StackSwap partner')
2eb59c9775ab N - no - other | /go booking links decode to venues' own websites, no partner key
caa14deb4d4a N - no - other | directory outbound redirect, no paid evidence
755a2a6d1267 N - no - other | sales-commission calculator name
5ec5f13756b2 N - no - other | 'sponsored by the Department for Transport'
f585ec75003f C op tr h other | <!-- agent-ad ... kind=house disclosure=sponsored --> block inserted in the post
90d18f39a5a8 C op tr h other | '## Sponsored: ... house ad placed by the owner of this site'
c4e11fc6bd2b N - no - other | 'paid placement' in article text
6c66303560f5 N - no - other | blog search result about ads
57eb8b484d37 N - no - other | plain merchant URLs; generic 'earns affiliate commission on some purchases'
c7d9ef6f5c45 N - no - other | policy text about rel=sponsored
087ca09dcc00 N - no - other | sponsoredResults: [] (empty)
f696440ffb29 N - no - other | sponsoredResults: []
bfbeee96420c N - no - other | sponsoredResults: []
ae19e28e142c C op doc m other | Travelpayouts tp.media links generated for any destination; sibling tools and responses state VoyageHacks affiliate links
559b81706a82 C op doc m other | CJ Booking.com link with sid=mcp-cars
1fff6efc9649 C op doc m other | Travelpayouts eSIM links; description: affiliate links, VoyageHacks may earn a commission
df6a74994f11 C op doc m shopping | Amazon tag on gear-catalogue picks; responses: some links are affiliate links
d049ac7fc2ad C op doc m shopping | Amazon storefront link with tag + affiliate disclosure
7366762a21d1 C op tr m shopping | wem3 /api/go wrapping Awin (clickref=wem-...) and AliExpress affiliate links; instructions: funded by affiliate commission
8e87915168b7 C op doc m shopping | same links; response: outbound links are affiliate-tracked
19fe673d0381 C op tr m shopping | as 7366762a21d1
5ff65bf717e4 C op doc m shopping | same links; response disclosure
d19c964a4bad N - no - ad_network | placements:[]
ca3396d79c8c N - no - other | calendar booking link
21a9478ba20c C op doc m shopping | /out redirect wrapping eBay EPN campid / Amazon tag / AliExpress; instructions: links go to merchant (Affiliate)
658f0b0e9f78 C op doc m shopping | as 21a9478ba20c
9b25a1ee0383 C op doc m shopping | as 21a9478ba20c
3db85ec61212 C op doc m shopping | as 21a9478ba20c
286a58524d18 C op doc m shopping | as 21a9478ba20c
6c3ddb985b05 C op doc m shopping | as 21a9478ba20c
b01c2febcba0 C op doc m shopping | as 21a9478ba20c
39a7bc78fd99 C op doc m shopping | as 21a9478ba20c
6408cf71f5b9 C op doc m shopping | as 21a9478ba20c
9a3729f40a2d C op doc m shopping | as 21a9478ba20c
2e577309415a C op doc m shopping | as 21a9478ba20c
98fd98b222b8 C op doc m shopping | as 21a9478ba20c
6aabde9b0ade C op doc m shopping | as 21a9478ba20c
3574ec06d01a N - no - shopping | 'Anzeige' = watch display
0fbe9e808867 C op doc m shopping | as 21a9478ba20c
6cdac2bf992b C op tr h other | [Sponsored] tariffs rendered by the server; description: affiliate links
40a1f30394d2 C op tr m other | recommended exchange with referral_code COINREBATE and /go signup redirect
b6bfc68065c8 N - no - other | guide titles about commissions
f2d04bbdf4cb P op doc m other | the operator's own discount card ('FineRx may earn a fee')
dcb563e82731 P op doc m other | as f2d04bbdf4cb
5630bdfe71d4 N - no - other | 'paid placement cannot move a studio' ranking-method text
918689120a49 C tp tr l other | Impact Ticketmaster link carried with booking.source='dailyinfo' (third-party listing site); upstream page not verifiable
2ee7c7a29162 C un no l other | Awin SeeTickets link with booking.source='seetickets'; could be feed-supplied or operator-built
d2a911262b02 C op doc m other | /go/get-crypto redirect; instructions: affiliate links from PeanutButterJelly
8ff5c1926e3c C op doc m other | same links; response: 'These are affiliate links'
"""


# Supplement 2 (kind=nested): every nested signature is coded per host from the evidence on
# out/review_sheet_supplement2.md; ids are read from that sheet.
NESTED = {
    "lmk.today": ("C op tr m shopping", "affiliate link (Amazon tag=lmk.today-20 / aff_url bid-redirect) nested in the operator's /c/ click wrapper; instructions: query string carries click attribution"),
    "moltad.net": ("C op tr m ad_network", "CJ affiliate link nested in a moltadserver ad-unit redirect (ft=affiliate_network)"),
    "wem3.ai": ("C op tr m shopping", "Awin/AliExpress affiliate link nested in the wem3 /api/go redirect; response: outbound links are affiliate-tracked"),
    "wo*.de": ("C op doc m shopping", "eBay EPN / Amazon tag / AliExpress / Tradedoubler affiliate link nested in the /out redirect; instructions: links go to merchant (Affiliate)"),
}


def nested_rows():
    import re
    sheet = Path(__file__).resolve().parents[1] / "out" / "review_sheet_supplement2.md"
    rows, host = [], None
    for line in open(sheet):
        m = re.match(r"## (\S+) :: ", line)
        if m:
            host = m.group(1)
        m = re.match(r"### SIG (\w+)", line)
        if m:
            key = "wo*.de" if re.fullmatch(r"wo[a-z]+\.de", host) else host
            code, note = NESTED[key]
            rows.append(f"{m.group(1)} {code} | {note}")
    return rows


def main():
    out = {}
    for line in ROWS.strip().splitlines() + nested_rows():
        head, note = line.split(" | ", 1)
        sig, st, o, b, cf, cat = head.split()
        out[sig] = {"status": S[st], "origin": O[o], "basis": B[b], "confidence": CF[cf],
                    "tool_category": cat, "note": note.strip()}
    p = Path(__file__).resolve().parents[1] / "out" / "coding_A.json"
    json.dump(out, open(p, "w"), indent=1)
    print(f"coder A: {len(out)} signatures -> {p}")


if __name__ == "__main__":
    main()
