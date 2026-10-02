"""
Chatbot over the uploaded Excel files.

Flow: question -> prompt with the DataFrame structure -> Gemini writes pandas code
-> the code runs on the DataFrames -> the `result` variable is formatted for the user.
"""

from app.chat.service import answer_question

__all__ = ["answer_question"]
