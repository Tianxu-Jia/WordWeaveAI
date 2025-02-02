from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class MyCustomToolInput(BaseModel):
    """Input schema for MyCustomTool."""

    argument: str = Field(..., description="Description of the argument.")


class MyCustomTool(BaseTool):
    name: str = "Name of my tool"
    description: str = (
        "Clear description for what this tool is useful for, your agent will need this information to use it."
    )
    args_schema: Type[BaseModel] = MyCustomToolInput

    def _run(self, argument: str) -> str:
        # Implementation goes here
        return "this is an example of a tool output, ignore it and move along."

##########################################################
from semanticscholar import SemanticScholar
import arxiv
import time
from pypdf import PdfReader
import os

class SemanticScholarSearch:
    def __init__(self):
        self.sch_engine = SemanticScholar(retry=False)

    def find_papers_by_str(self, query, N=10):
        paper_sums = list()
        results = self.sch_engine.search_paper(query, limit=N, min_citation_count=3, open_access_pdf=True)
        references = []
        for _i in range(len(results)):
            paper_sum = f'Title: {results[_i].title}\n'
            paper_sum += f'Abstract: {results[_i].abstract}\n'
            paper_sum += f'Citations: {results[_i].citationCount}\n'
            paper_sum += f'Release Date: year {results[_i].publicationDate.year}, month {results[_i].publicationDate.month}, day {results[_i].publicationDate.day}\n'
            paper_sum += f'Venue: {results[_i].venue}\n'
            paper_sum += f'Paper ID: {results[_i].externalIds["DOI"]}\n'
            paper_sums.append(paper_sum)

            entry = {
            'title': results[_i].title,
            'authors': [author['name'] for author in results[_i].authors],
            'year': {{results[_i].publicationDate.year}, {results[_i].publicationDate.month}, {results[_i].publicationDate.day}},
            'journal': results[_i].venue,
            'url': results[_i].paperUrl,
            }
            references.append(entry)
        return paper_sums, references

    def retrieve_full_paper_text(self, query):
        pass


class ArxivSearch:
    def __init__(self):
        # Construct the default API client.
        self.sch_engine = arxiv.Client()
        
    def _process_query(self, query: str) -> str:
        """Process query string to fit within MAX_QUERY_LENGTH while preserving as much information as possible"""
        MAX_QUERY_LENGTH = 300
        
        if len(query) <= MAX_QUERY_LENGTH:
            return query
        
        # Split into words
        words = query.split()
        processed_query = []
        current_length = 0
        
        # Add words while staying under the limit
        # Account for spaces between words
        for word in words:
            # +1 for the space that will be added between words
            if current_length + len(word) + 1 <= MAX_QUERY_LENGTH:
                processed_query.append(word)
                current_length += len(word) + 1
            else:
                break
            
        return ' '.join(processed_query)
    
    def find_papers_by_str(self, query, N=20):
        processed_query = self._process_query(query)
        max_retries = 3
        retry_count = 0
        
        references = []
        while retry_count < max_retries:
            try:
                search = arxiv.Search(
                    query="abs:" + processed_query,
                    max_results=N,
                    sort_by=arxiv.SortCriterion.Relevance)

                paper_sums = list()
                # `results` is a generator; you can iterate over its elements one by one...
                for r in self.sch_engine.results(search):
                    paperid = r.pdf_url.split("/")[-1]
                    pubdate = str(r.published).split(" ")[0]
                    paper_sum = f"Title: {r.title}\n"
                    paper_sum += f"Summary: {r.summary}\n"
                    paper_sum += f"Publication Date: {pubdate}\n"
                    paper_sum += f"Categories: {' '.join(r.categories)}\n"
                    paper_sum += f"arXiv paper ID: {paperid}\n"
                    paper_sums.append(paper_sum)

                    entry = {
                        'title': r.title,
                        'authors': [author.name for author in r.authors],
                        'year': pubdate,
                        'journal': 'arXiv',
                        'url': 'https://arxiv.org/pdf/' + paperid,
                        #'abstract': r.summary
                        }
                    references.append(entry)
                time.sleep(2.0)
                return "\n".join(paper_sums), references
                
            except Exception as e:
                retry_count += 1
                if retry_count < max_retries:
                    # 递增延时
                    time.sleep(2 * retry_count)
                    continue
                
        return None

    def retrieve_full_paper_text(self, query):
        pdf_text = str()
        paper = next(arxiv.Client().results(arxiv.Search(id_list=[query])))
        # Download the PDF to the PWD with a custom filename.
        paper.download_pdf(filename="downloaded-paper.pdf")
        # creating a pdf reader object
        reader = PdfReader('downloaded-paper.pdf')
        # Iterate over all the pages
        for page_number, page in enumerate(reader.pages, start=1):
            # Extract text from the page
            try:
                text = page.extract_text()
            except Exception as e:
                os.remove("downloaded-paper.pdf")
                time.sleep(2.0)
                return "EXTRACTION FAILED"

            # Do something with the text (e.g., print it)
            pdf_text += f"--- Page {page_number} ---"
            pdf_text += text
            pdf_text += "\n"
        os.remove("downloaded-paper.pdf")
        time.sleep(2.0)
        return pdf_text


if __name__ == "__main__":
    topic = "Statistical Empirical Study"

    arxiv_eng = ArxivSearch()

    _, references = arxiv_eng.find_papers_by_str(topic)
    arxiv_ids = [ref['url'].split('/')[-1] for ref in references]
    
    for id in arxiv_ids:
        try:
            paper = next(arxiv.Client().results(arxiv.Search(id_list=[id])))
            paper.download_pdf(dirpath="./ref_papers")
        except Exception as e:
            print(e)
            continue



    debug = 1

