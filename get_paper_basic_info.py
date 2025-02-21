import requests
import search_zz
import json

header = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
    }

def get_paper_citations(paper_name):
    is_success = False
    def save_data(entries):
        save_file = f"./data/{paper_name}_step1.json"
        with open(save_file, 'w', encoding='utf-8') as f:
            json.dump(entries, f, ensure_ascii=False, indent=4)
    while not is_success:
        paper_id = get_paper_id(paper_name)
        # paper_id = "CorpusId:56481942"
        print(' getting citations information......')
        r = requests.get(
            f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}/citations?fields=contexts,title,publicationVenue,year,authors&offset=0&limit=400",
            headers=header
        )
        json_r = r.json()
        data_js = json_r['data']
        entry_list = []
        for data in data_js:
            context_list = data["contexts"]
            publication_venue = ""
            paper_title = ""
            year = ""
            authors_list = []
            if "citingPaper" in data:
                if "publicationVenue" in data['citingPaper'] and data['citingPaper']['publicationVenue'] is not None:
                    publication_venue = data['citingPaper']['publicationVenue']['name']
                paper_title = data['citingPaper']['title'] if 'title' in data['citingPaper'] else ""
                year = data['citingPaper']['year'] if 'year' in data['citingPaper'] else ""
                authors_list = data['citingPaper']['authors'] if 'authors' in data['citingPaper'] else []
            entry_list.append(dict(title=paper_title, year=year, authors=authors_list, publication_venue=publication_venue, context_list=context_list))
        # get google
        titles_google = search_zz.get_google_titles(paper_name)
        title_list = [entry['title'] for entry in entry_list]
        lowercase_list1 = [item.lower() for item in titles_google]
        lowercase_list2 = [item.lower() for item in title_list]
        not_in_list = [item for item in lowercase_list1 if item not in lowercase_list2]
        print("In google but not in PPT:", ",\n".join(not_in_list))
        entry_list.sort(key=lambda x: int(x['year'] if x['year'] else 2023))
        save_data(entry_list)
        print(f"#papers={len(entry_list)}")
        
        
        is_success = True
    
def get_paper_id(paper_name):
    query_list = "+".join(paper_name.split(" ")[:4])
    #query_list = "Domain Adaptation via Bidirectional Cross-Attention Transformer"
    r = requests.get(
        f'https://api.semanticscholar.org/graph/v1/paper/autocomplete?query={query_list}',
        headers=header
    )
    r_json = r.json()['matches']
    if len(r.json()['matches']) == 0:
        return None
    print("Get paper:",r_json[0]['title'])
    paper_id = r_json[0]['id']
    return paper_id

if __name__ == '__main__':
    # 要查找的文章名字
    article_title = "Learning Inverse Dynamics by Gaussian Process Regression under the Multi-Task Learning Framework"

    get_paper_citations(article_title)

    # base_search.generate_author_link(article_title)