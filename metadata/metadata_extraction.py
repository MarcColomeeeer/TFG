import urllib.request
import xml.etree.ElementTree as ET
import os
import time
from datetime import datetime
import json

# --- Set of already seen paper IDs ---
seen_papers = set()


def save_to_json(papers, filename="papers.json"):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(papers, f, ensure_ascii=False, indent=2)
    print(f"✅ Saved {len(papers)} papers to '{filename}'")


def download_papers(queries):
    base_url = "http://export.arxiv.org/api/query"

    for query in queries:
        papers = []
        print(f"\n🔍 Starting query: {query}")

        for start in range(0, 20001, 2000):
            url = f"{base_url}?search_query={query}&start={start}&max_results=2000"
            print(f"Fetching {query} results {start}–{start+1999}...")

            try:
                response = urllib.request.urlopen(url)
                xml_data = response.read().decode('utf-8', errors='replace')
            except Exception as e:
                print(f"❌ Failed to fetch data: {e}")
                continue

            try:
                root = ET.fromstring(xml_data)
            except ET.ParseError as e:
                print(f"❌ Failed to parse XML: {e}")
                continue

            atom_ns = '{http://www.w3.org/2005/Atom}'
            arxiv_ns = '{http://arxiv.org/schemas/atom}'

            for entry in root.findall(f'{atom_ns}entry'):
                paper_id = entry.find(f'{atom_ns}id')
                if paper_id is None or paper_id.text in seen_papers:
                    continue

                seen_papers.add(paper_id.text)

                primary_cat = entry.find(f'{arxiv_ns}primary_category')
                if primary_cat is None:
                    continue

                category_term = primary_cat.attrib.get('term', '')
                if category_term != query.split(':')[1]:
                    continue

                title = entry.find(f'{atom_ns}title').text.strip()
                authors = [author.find(f'{atom_ns}name').text.strip()
                           for author in entry.findall(f'{atom_ns}author')]
                summary = entry.find(f'{atom_ns}summary').text.strip()
                published_raw = entry.find(f'{atom_ns}published').text.strip()
                pdf_link = None
                for link in entry.findall(f'{atom_ns}link'):
                    if link.attrib.get('title') == 'pdf':
                        pdf_link = link.attrib['href']
                        break

                published_year = datetime.strptime(published_raw, '%Y-%m-%dT%H:%M:%SZ').year

                papers.append({
                    "title": title,
                    "authors": authors[:10],
                    "category": category_term,
                    "published_year": published_year,
                    "summary": summary,
                    "pdf_link": pdf_link or ""
                })

            time.sleep(1)  # Respect API rate limits

        if papers:
            category_name = query.split(':')[1]
            filename = f"{category_name}.json"
            save_to_json(papers, filename)
        else:
            print(f"⚠️ No papers found for query '{query}'")


raw_categories = """
math.AC	math.AG	math.AP	math.AT	math.CA	math.CO	math.CT	math.CV	math.DG	math.DS	math.FA	math.GM	math.GN	math.GR	math.GT	math.HO	math.IT	math.KT	math.LO	math.MG	math.MP	math.NA	math.NT	math.OA	math.OC	math.PR	math.QA	math.RA	math.RT	math.SG	math.SP	math.ST
stat.AP	stat.CO	stat.ME	stat.ML	stat.OT	stat.TH
q-fin.CP	q-fin.EC	q-fin.GN	q-fin.MF	q-fin.PM	q-fin.PR	q-fin.RM	q-fin.ST	q-fin.TR
astro-ph.CO	astro-ph.EP	astro-ph.GA	astro-ph.HE	astro-ph.IM	astro-ph.SR	cond-mat.dis-nn	cond-mat.mes-hall	cond-mat.mtrl-sci	cond-mat.other	cond-mat.quant-gas	cond-mat.soft	cond-mat.stat-mech	cond-mat.str-el	cond-mat.supr-con	gr-qc	hep-ex	hep-lat	hep-ph	hep-th	math-ph	nlin.AO	nlin.CD	nlin.CG	nlin.PS	nlin.SI	nucl-ex	nucl-th	physics.acc-ph	physics.ao-ph	physics.app-ph	physics.atm-clus	physics.atom-ph	physics.bio-ph	physiscs.chem-ph	physics.class-ph	physics.comp-ph	physics.data-an	physics.ed-ph	physics.flu-dyn	physics.gen-ph	physics.geo-ph	physics.hist-ph	physics.ins-det	physics.med-ph	physics.optics	physics.plasm-ph	physics.pop-ph	physics.soc-ph	physics.space-ph	quant-ph
q-bio.BM	q-bio.CB	q-bio.GN	q-bio.MN	q-bio.NC	q-bio.OT	q-bio.PE	q-bio.QM	q-bio.SC	q-bio.TO
cs.AI	cs.AR	cs.CC	cs.CE	cs.CG	cs.CL	cs.CV	cs.CY	cs.DB	cs.DC	cs.DL	cs.DM	cs.DS	cs.ET	cs.FL	cs.GL	cs.GR	cs.GT	cs.HC	cs.IR	cs.IT	cs.LG	cs.LO	cs.MA	cs.MM	cs.MS	cs.NA	cs.NE	cs.NI	cs.OH	cs.OS	cs.PF	cs.PL	cs.RO	cs.SC	cs.SD	cs.SE	cs.SI	cs.SY	econ.GN	econ.EM	econ.TH
eess.AS	eess.IV	eess.SP	eess.SY
"""
queries = [f"cat:{cat.strip()}" for cat in raw_categories.split() if cat.strip()]


if __name__ == "__main__":
    download_papers(queries)
