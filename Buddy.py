import tkinter as tk
import pyautogui
import subprocess
import openai

# OpenAI API credentials
openai.api_key = ''

# Create a tkinter window
window = tk.Tk()
window.title("AI Task Automation")
window.geometry("400x200")

# Create a label to display AI results
result_label = tk.Label(window, text="AI Results")
result_label.pack()

# Create a feedback entry field
feedback_entry = tk.Entry(window)
feedback_entry.pack()

# Create a chatbot response label
chatbot_response_label = tk.Label(window, text="Chatbot Response")
chatbot_response_label.pack()

# Variable for reinforcement learning
feedback_points = 0

# Function to process user feedback
def process_feedback():
    global feedback_points
    feedback = feedback_entry.get()
    
    # Process feedback and update AI model based on user ratings
    try:
        rating = int(feedback)
        if 0 <= rating <= 100:
            feedback_points += rating
            if rating < 50:
                result_label.configure(text="Thank you for your feedback. We'll work on improving.")
            else:
                result_label.configure(text="Thank you for your positive feedback. We'll continue to improve.")
        else:
            result_label.configure(text="Invalid feedback. Please provide a rating between 0 and 100.")
    except ValueError:
        result_label.configure(text="Invalid feedback. Please provide a numerical rating.")
    
    feedback_entry.delete(0, tk.END)

# Function to process user query with the chatbot
def process_query():
    query = feedback_entry.get()
    
    # Perform actions based on user query
    if "open notepad" in query.lower():
        try:
            subprocess.Popen("notepad.exe")
            chatbot_response = "Notepad has been opened."
        except OSError:
            chatbot_response = "Failed to open Notepad."
    elif "close notepad" in query.lower():
        try:
            pyautogui.hotkey('alt', 'f4')
            chatbot_response = "Notepad has been closed."
        except pyautogui.FailSafeException:
            chatbot_response = "Unable to close Notepad. Action aborted."
    elif "take screenshot" in query.lower():
        try:
            screenshot = pyautogui.screenshot()
            screenshot.save('screenshot.png')
            chatbot_response = "Screenshot captured and saved as 'screenshot.png'."
        except pyautogui.FailSafeException:
            chatbot_response = "Failed to capture screenshot. Action aborted."
    else:
        # Query OpenAI for chatbot response
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": query}
        ]
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            chatbot_response = response['choices'][0]['message']['content']
        except openai.Error as e:
            chatbot_response = f"OpenAI API Error: {str(e)}"
        except Exception as e:
            chatbot_response = f"An error occurred while processing the request: {str(e)}"

    chatbot_response_label.configure(text=chatbot_response)
    feedback_entry.delete(0, tk.END)

    # Perform reinforcement learning and optimization based on user query
    # Adapt AI model and automation tactics based on feedback points

# Create a button to submit feedback
submit_button = tk.Button(window, text="Submit Feedback", command=process_feedback)
submit_button.pack()

# Create a button to submit chatbot query
query_button = tk.Button(window, text="Chat with AI", command=process_query)
query_button.pack()

# Start the GUI event loop
window.mainloop()
