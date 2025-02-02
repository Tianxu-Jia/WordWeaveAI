#!/usr/bin/env python
from pydantic import BaseModel
from crewai.flow import Flow, listen, start

from wordweaveai.crews.academic_writer_crew.academic_writer_crew import AcademicWriterCrew
from wordweaveai.tools.custom_tool import ArxivSearch


class PoemState(BaseModel):
    sentence_count: int = 1
    poem: str = ""


#class AcademicWritingFlow(Flow[PoemState]):
class AcademicWritingFlow(Flow):
    def __init__(self, 
                 research_proposal_md_file, 
                 major):
        super().__init__()
        self.research_proposal_md_file=research_proposal_md_file
        self.research_proposal=""
        self.major = major

    @start()
    def read_research_proposal(self):
        print("reading the research proposal")
        with open(research_proposal_md_file, "r", encoding="utf-8") as file:
            content = file.read()
        self.research_proposal = content


    @listen(read_research_proposal)
    def extract_research_topic(self):
        print("Generating searching keywords and phrases")
        inputs = {"major": self.major,
                  "research_proposal": self.research_proposal}
        topics = AcademicWriterCrew().crew_extract_research_topic().kickoff(inputs=inputs)

        self.topics = topics.pydantic.phrase_list
        debug = 1   
    
    @listen(extract_research_topic)
    def search_and_download_ref_papers(self):
        arx_eng = ArxivSearch()
        for topic in self.topics:


    @listen(generate_search_phrases)
    def save_poem(self):
        print("Saving poem")
        with open("poem.txt", "w") as f:
            f.write(self.state.poem)


def kickoff(research_proposal_md_file, major, plot_flow):
    academic_writing_flow = AcademicWritingFlow(research_proposal_md_file,
                                                major)

    if plot_flow:
        academic_writing_flow.plot("cacdemic_writing_flow.html")

    academic_writing_flow.kickoff()

if __name__ == "__main__":
    research_proposal_md_file = "./src/wordweaveai/crews/academic_writer_crew/config/research_proposal.md"
    major = "finacial, AI"
    kickoff(research_proposal_md_file, 
            major=major,
            plot_flow=False)
