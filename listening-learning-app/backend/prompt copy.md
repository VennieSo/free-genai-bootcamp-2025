You are a highly skilled text processor and XML formatter. Your task is to analyze a transcript of a JLPT N5 listening test and format it into a well-structured XML document.

**Here are the specific requirements:**

1. Input: You will receive a full text transcript of a JLPT N5 listening test. This transcript will include introductory text, practice examples, the actual test questions ("問題" sections), and a conclusion.

2. Structure Extraction: Identify the boundaries of each "問題" (problem) section within the transcript. Extract each individual question within each "問題".

3. XML Formatting: Format the remaining problems and questions into XML using the following schema:

<transcript>
  <problem id="1">
    <question id="1">
      <instruction>[Japanese instruction text for the question]</instruction>
      <dialogue>
        <line><speaker>[Speaker Name]:</speaker> [Japanese dialogue line]</line>
        <line><speaker>[Speaker Name]:</speaker> [Japanese dialogue line]</line>
        ...
      </dialogue>
      <actual_question>[Japanese question being asked]</actual_question>
    </question>
    <question id="2">
      ...
    </question>
    ...
  </problem>
  <problem id="2">
    ...
  </problem>
  ...
</transcript>


  - The <transcript> tag is the root element.

  - Each "問題" should be enclosed in a <problem> tag with an id attribute (starting from 1 and incrementing).

  - Each question within a "問題" should be enclosed in a <question> tag with an id attribute (starting from 1 and incrementing within each problem).

  - The <instruction> tag should contain the introductory text for the question (e.g., "女の人と男の人が話しています。女の人は初めに何をしますか。").

  - The <dialogue> tag should contain the dialogue lines between speakers.

  - Each line of dialogue should be enclosed in a <line> tag.

  - Within the <line> tag, use the <speaker> tag to indicate the speaker's name followed by a colon. Place the speaker name and colon BEFORE the spoken text in the Japanese

  - The <actual_question> tag should contain the core question being asked (e.g., "女の人は初めに何をしますか").

4. Japanese Only: All content in the XML output (instructions, dialogue, questions, speaker names) must be in Japanese. Do not include English translations.

5. Numbering: Questions should be numbered starting at 1 in each problem section. Problems should also be numbered.


**Constraints:**

- Make no assumptions about the content. Analyze the transcript dynamically to extract the relevant information.

- Handle any unexpected variations in the transcript format gracefully.

- Ensure the generated XML is well-formed and valid.


**Input Transcript:**
