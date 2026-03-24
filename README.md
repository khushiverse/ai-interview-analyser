# Interview Insight

Interview Insight is a Streamlit-based AI interview practice app that helps users improve their interview answers with timing, analysis, and AI-powered coaching.

## Features

- Practice with multiple common interview questions
- Set a timer for each answer
- Analyze filler words, sentiment, structure, and keyword coverage
- Get AI-generated coaching with:
  - what works
  - what to improve
  - a better sample answer
- Clean, minimal interface built with Streamlit

## Tech Stack

- Python
- Streamlit
- NLTK
- Requests
- Hugging Face Inference API

## Project Structure

```text
ai-interview-analyser/
|-- app.py
|-- analyser.py
|-- requirements.txt
|-- .gitignore
|-- README.md
```

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/khushiverse/ai-interview-analyser.git
cd ai-interview-analyser
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add your Hugging Face API key

Create a `.env` file in the project root:

```env
HF_API_KEY=your_huggingface_token
```

## Run the App

```bash
streamlit run app.py
```

Then open the local Streamlit URL shown in the terminal.

## How It Works

1. Select an interview question
2. Set the answer timer
3. Click `Start Interview`
4. Type your response
5. Click `Analyze`
6. Review the score, feedback, keyword coverage, and AI coaching

## Sample Questions

- Tell me about yourself
- Why should we hire you?
- What are your strengths?
- What is your biggest weakness?
- Describe a challenge you faced and how you handled it
- Tell me about a time you worked in a team
- Why do you want this role?
- Where do you see yourself in 5 years?
- Tell me about a project you are proud of
- How do you handle pressure or tight deadlines?

## Notes

- `.env` is ignored using `.gitignore`, so your API key is not pushed to GitHub
- If the AI request fails, the app still provides rule-based feedback
- If you change the API key, restart Streamlit so the app picks up the new value

## Future Improvements

- Speech-to-text answer input
- Answer history and progress tracking
- More question categories
- Export feedback to PDF

## Author

Built by Khushi Venkatesh.
