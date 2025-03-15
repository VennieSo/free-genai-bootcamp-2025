import boto3
import xml.etree.ElementTree as ET
from typing import Optional, Dict, Any
import os

# Model ID for Bedrock (same as chat.py)
MODEL_ID = "amazon.nova-micro-v1:0"

class TranscriptProcessor:
    def __init__(self, model_id: str = MODEL_ID):
        """Initialize the transcript processor with Bedrock client"""
        self.bedrock_client = boto3.client('bedrock-runtime', region_name="us-east-1")
        self.model_id = model_id
        
    def _get_prompt_template(self) -> str:
        """Read the prompt template from the prompt.md file"""
        prompt_path = os.path.join(os.path.dirname(__file__), 'prompt.md')
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
            
    def process_transcript(self, transcript_text: str) -> str:
        """Process the transcript using Bedrock and return the output"""
        # Combine prompt template with transcript
        prompt_template = self._get_prompt_template()
        full_prompt = f"{prompt_template}\n\n{transcript_text}"
        
        # Prepare the message for Bedrock
        messages = [{
            "role": "user",
            "content": [{"text": full_prompt}]
        }]
        
        try:
            # Call Bedrock
            response = self.bedrock_client.converse(
                modelId=self.model_id,
                messages=messages,
                inferenceConfig={"temperature": 0.1}
            )
            
            # Extract and clean the output
            raw_output = response['output']['message']['content'][0]['text']
            
            # Remove code block markers if present
            cleaned_output = raw_output.strip()
            if cleaned_output.startswith("```xml"):
                cleaned_output = cleaned_output[6:]  # Remove ```xml
            if cleaned_output.endswith("```"):
                cleaned_output = cleaned_output[:-3]  # Remove ```
            
            # Ensure the XML is well-formed
            try:
                ET.fromstring(cleaned_output)  # Validate XML
                return cleaned_output.strip()
            except ET.ParseError as e:
                raise Exception(f"Invalid XML structure in response: {str(e)}")
                
        except Exception as e:
            raise Exception(f"Error processing transcript: {str(e)}")
            
    def save_structured_transcript(self, output_content: str, output_path: str = "output.txt") -> None:
        """Save the output content to a file in the questions directory"""
        # Create the questions directory if it doesn't exist
        questions_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'questions')
        os.makedirs(questions_dir, exist_ok=True)
        
        # Update the output path to include the questions directory
        output_path = os.path.join(questions_dir, output_path)  # Ensure this is just the filename
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(output_content)  # Save the raw output content
        except Exception as e:
            raise Exception(f"Error saving output file: {str(e)}")

    def format_structured_transcript(self, xml_content: str) -> str:
        """Convert XML transcript to formatted HTML"""
        try:
            root = ET.fromstring(xml_content)
            formatted_output = []
            
            for question in root.findall(".//question"):
                # Question header
                q_id = question.get('id')
                formatted_output.append(f'<h4>Question {q_id}</h4>')
                
                # Scenario
                scenario = question.find('scenario')
                if scenario is not None and scenario.text:
                    formatted_output.append(f'<p><strong>Scenario:</strong> {scenario.text}</p>')
                
                # Dialogue
                dialogue = question.find('dialogue')
                if dialogue is not None:
                    formatted_output.append('<div class="dialogue">')
                    for elem in dialogue:
                        if elem.tag == 'speaker':
                            speaker_text = elem.tail.strip() if elem.tail else ""
                            formatted_output.append(
                                f'<p><strong>{elem.text}:</strong> {speaker_text}</p>'
                            )
                    formatted_output.append('</div>')
                
                # Actual question
                actual_question = question.find('actual_question')
                if actual_question is not None and actual_question.text:
                    formatted_output.append(
                        f'<p><strong>Question:</strong> {actual_question.text}</p>'
                    )
                
                formatted_output.append('<hr>')  # Divider between questions
            
            return '\n'.join(formatted_output)
        except ET.ParseError as e:
            return f'<p class="error">Error parsing XML: {str(e)}</p>'

if __name__ == "__main__":
    # Example usage
    processor = TranscriptProcessor()
    
    # Read transcript text from a file in the transcripts directory
    transcript_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'transcripts', '0e0duD8_LFE.txt')
    
    try:
        with open(transcript_file_path, 'r', encoding='utf-8') as f:
            sample_transcript = f.read()
    except FileNotFoundError:
        print(f"Error: The file {transcript_file_path} does not exist.")
        exit(1)
    except Exception as e:
        print(f"Error reading transcript file: {str(e)}")
        exit(1)
    
    try:
        structured_transcript = processor.process_transcript(sample_transcript)
        processor.save_structured_transcript(structured_transcript)
        print("Successfully processed transcript and saved output!")
        print(processor.format_structured_transcript(structured_transcript))
    except Exception as e:
        print(f"Error: {str(e)}")
