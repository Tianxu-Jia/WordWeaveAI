from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, after_kickoff
from gloable_config import llm_ollama
from datetime import datetime



# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators
from pydantic import BaseModel
from typing import List

class research_topics(BaseModel):
    phrase_list: List[str]  # list of research topics



@CrewBase
class AcademicWriterCrew:
    """academic_writer_crew"""

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # If you would lik to add tools to your crew, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def PhD_candidate(self) -> Agent:
        return Agent(
            config=self.agents_config["PhD_candidate"],
            llm=llm_ollama
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def extract_research_topics(self) -> Task:
        return Task(
            config=self.tasks_config["extract_research_topics"],
            output_pydantic=research_topics,
        )

    @task
    def paper_review(self) -> Task:
        return Task(
            config=self.tasks_config["paper_review"],
        )
    
    
    @after_kickoff
    def save_output(self, result):
        # Format the output as markdown
        markdown_output = f"""
# CrewAI Execution Results
Generated on: {datetime.now().isoformat()}

## Raw Output
{result.raw}

## Tasks Output            
{'\n\n'.join(item.raw for item in result.tasks_output)}

## Token Usage
{result.token_usage}
"""
        markdown_output = markdown_output.replace("```", "")

        # Save to a file
        with open("./debug_docs/crew_output.md", "w") as f:
            f.write(markdown_output)
        
        return result

    @crew
    def crew_extract_research_topic(self) -> Crew:
        """Creates the Research Crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            #process=Process.sequential,
            #verbose=True,
        )
