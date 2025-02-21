import traceback

import requests
import json
from tqdm import tqdm

header = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
    }


class AuthorInfo():
    def __init__(self, paper_title, limit=10):
        self.paper_title = paper_title
        input_path = f"./data/{self.paper_title}_step1.json"
        with open(input_path, encoding='utf-8') as f:
            papers = json.load(f)
        authors = []
        for paper in papers:
            _author_list = [(_['authorId'], _['name']) for _ in paper['authors']]
            authors = authors + _author_list
        # authors = [_ for _ in authors if _[0] is not None]
        authors = set(authors)
        self.authors = [dict(author_id=_[0], name=_[1]) for _ in authors]
        self.save_file = f"./data/{paper_title}_authors.json"
        self.save_data()
        self.limit = limit if limit > 0 else len(self.authors)

    def save_data(self):
        with open(self.save_file, 'w', encoding='utf-8') as f:
            json.dump(self.authors, f, ensure_ascii=False, indent=4)

    def get_author_info_from_semantic(self):
        url = 'https://api.semanticscholar.org/graph/v1/author/batch'
        fields = "name,hIndex,citationCount,url,externalIds,homepage,affiliations,hIndex"
        ids = [_['author_id'] for _ in self.authors[:self.limit] if _['author_id'] is not None]
        r = requests.post(url,
            params={'fields': fields},
            json={"ids": ids}
        )
        info_dict = {}
        for info in r.json():
            if info is not None:
                author_id = info['authorId']
                info_dict[author_id] = info
        for e in self.authors:
            if e['author_id'] in info_dict:
                e['semantic_url'] = info_dict[e['author_id']]['url']
                e['semantic_info'] = info_dict[e['author_id']]

        self.save_data()

    def get_author_from_google(self):
        url = "https://google.serper.dev/search"
        api_key = "" # update the key
        for i, e in tqdm(enumerate(self.authors[:self.limit])):
            author_name = e['name']
            query = f"homepage of {author_name}, a researcher on computer science"
            is_success = False
            while not is_success:
                try:
                    payload = json.dumps({
                        "q": query
                    })
                    headers = {
                        'X-API-KEY': api_key,
                        'Content-Type': 'application/json'
                    }
                    response = requests.request("POST", url, headers=headers, data=payload)
                    google_url = ""
                    google_result_list = []
                    if response.status_code == 200:
                        result_dict = json.loads(response.text)
                        google_result_list = result_dict['organic'][0:5]
                        google_result_list = [dict(title=_['title'], link=_['link'], snippet=_['snippet']) for _ in google_result_list]

                        if len(google_result_list) == 0:
                            break
                        google_url = google_result_list[0]['link']
                        # for r in google_result_list:
                        #     if ratio(author_name.lower(), r['title'][0:25].lower()) > 0.5:
                        #         google_url = r['link']

                    e['google_url'] = google_url
                    e['google_info'] = google_result_list
                    is_success = True
                except Exception as e:
                    traceback.print_exc()
                    print(f"exception in name: {author_name}")
                    is_success = True
            self.save_data()

if __name__ == '__main__':

    article_title = "Learning Inverse Dynamics by Gaussian Process Regression under the Multi-Task Learning Framework"

    author_info = AuthorInfo(article_title, 0)
    author_info.get_author_info_from_semantic()
    author_info.get_author_from_google()

    # base_search.generate_author_link(article_title)